import logging
import shutil
import math
from pathlib import Path

from app.config import DEVICE, MODEL_PATH, OUTPUTS_DIR
from app.workers.task_queue import update_job

logger = logging.getLogger(__name__)

_pipeline = None
_rembg = None


def load_model():
    """Load Hunyuan3D-2 pipeline at startup."""
    global _pipeline, _rembg
    try:
        from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
        logger.info(f"Loading Hunyuan3D-2 from {MODEL_PATH} on {DEVICE}")
        _pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            MODEL_PATH,
            device=DEVICE,
        )
        logger.info("Hunyuan3D-2 model loaded successfully")

        try:
            from hy3dgen.rembg import BackgroundRemover
            _rembg = BackgroundRemover()
            logger.info("Background remover loaded")
        except Exception as e:
            logger.warning(f"Failed to load BackgroundRemover: {e}")

    except ImportError:
        logger.warning(
            "hy3dgen not installed. Running in mock mode. "
            "Install Hunyuan3D-2 for real inference."
        )
        _pipeline = None
    except Exception as e:
        logger.error(f"Failed to load Hunyuan3D-2: {e}")
        _pipeline = None


def _render_views_from_mesh(mesh, output_dir: str) -> list[str]:
    """Render 4 views (front, right, back, left) from a trimesh mesh."""
    import trimesh
    import numpy as np
    from PIL import Image

    views = []
    angles = [0, 90, 180, 270]

    scene = trimesh.Scene(mesh)
    for i, angle in enumerate(angles):
        path = str(Path(output_dir) / f"view_{i}.png")
        try:
            # Rotate camera around Y axis
            rad = math.radians(angle)
            # Get bounding sphere for camera distance
            bounds = mesh.bounds
            center = (bounds[0] + bounds[1]) / 2
            extent = np.linalg.norm(bounds[1] - bounds[0])
            distance = extent * 1.5

            camera_pos = center + np.array([
                distance * math.sin(rad),
                distance * 0.3,
                distance * math.cos(rad),
            ])

            rotation = trimesh.scene.cameras.look_at(
                [camera_pos], [center], up=[0, 1, 0]
            )

            render_scene = trimesh.Scene(mesh)
            render_scene.camera_transform = rotation[0]

            png_data = render_scene.save_image(resolution=(512, 512))
            if png_data is not None:
                img = Image.open(trimesh.util.wrap_as_stream(png_data))
                img.save(path)
                views.append(path)
            else:
                raise RuntimeError("render returned None")
        except Exception as e:
            logger.warning(f"View {i} render failed: {e}, using placeholder")
            # Create a simple placeholder image
            img = Image.new("RGB", (512, 512), (200, 200, 200))
            img.save(path)
            views.append(path)

    return views


def _get_inference_params(settings: dict) -> dict:
    """Get pipeline parameters based on job settings."""
    enhanced = settings.get("enhanced_detail", False)
    return {
        "num_inference_steps": 100 if enhanced else 50,
        "octree_resolution": 512 if enhanced else 384,
    }


def generate_multiview(job_id: str, image_path: str) -> list[str]:
    """Generate 4 multi-view images from a single input image.

    Hunyuan3D-2 doesn't have a separate multi-view stage.
    We generate the full 3D mesh first, then render 4 views from it.
    """
    from app.workers.task_queue import get_job

    job = get_job(job_id)
    settings = job.get("settings", {}) if job else {}
    params = _get_inference_params(settings)

    update_job(job_id, status="processing", stage="multiview", progress=10)

    job_output_dir = OUTPUTS_DIR / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)

    if _pipeline is not None:
        try:
            from PIL import Image

            update_job(job_id, progress=20)
            image = Image.open(image_path).convert("RGBA")

            # Only remove background here if NOT already removed at upload
            if _rembg is not None and not settings.get("remove_bg", False):
                image = _rembg(image)

            # Generate 3D mesh
            update_job(job_id, progress=30)
            result = _pipeline(
                image=image,
                **params,
            )

            update_job(job_id, progress=70)

            # result is List[List[trimesh.Trimesh]]
            mesh = result[0]

            # Save mesh for later use in generate_3d
            glb_path = str(job_output_dir / "model.glb")
            mesh.export(glb_path)
            update_job(job_id, model_path=glb_path)

            # Render 4 views from the mesh
            update_job(job_id, progress=85)
            views = _render_views_from_mesh(mesh, str(job_output_dir))

            update_job(job_id, progress=100, multi_angle_paths=views)
            return views
        except Exception as e:
            logger.error(f"Multi-view generation failed: {e}")
            raise
    else:
        # Mock mode
        import time
        views = []
        for i in range(4):
            time.sleep(0.5)
            dst = str(job_output_dir / f"view_{i}.png")
            shutil.copy2(image_path, dst)
            views.append(dst)
            update_job(job_id, progress=25 * (i + 1))

        update_job(job_id, multi_angle_paths=views)
        return views


def generate_3d(job_id: str, image_path: str) -> str:
    """Generate/export 3D GLB model.

    If mesh was already generated during multi-view stage, just return it.
    Otherwise generate from scratch.
    """
    from app.workers.task_queue import get_job

    job = get_job(job_id)
    existing_model = job.get("model_path") if job else None

    # If already generated during multi-view, just mark complete
    if existing_model and Path(existing_model).exists():
        update_job(job_id, status="processing", stage="3d_generation", progress=100,
                   model_path=existing_model)
        return existing_model

    update_job(job_id, status="processing", stage="3d_generation", progress=10)

    job_output_dir = OUTPUTS_DIR / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)
    output_glb = str(job_output_dir / "model.glb")

    if _pipeline is not None:
        try:
            from PIL import Image

            job = get_job(job_id)
            settings = job.get("settings", {}) if job else {}
            params = _get_inference_params(settings)

            update_job(job_id, progress=20)
            image = Image.open(image_path).convert("RGBA")

            if _rembg is not None and not settings.get("remove_bg", False):
                image = _rembg(image)

            result = _pipeline(
                image=image,
                **params,
            )
            update_job(job_id, progress=80)

            mesh = result[0]
            mesh.export(output_glb)

            update_job(job_id, progress=100, model_path=output_glb)
            return output_glb
        except Exception as e:
            logger.error(f"3D generation failed: {e}")
            raise
    else:
        # Mock mode
        import time
        time.sleep(2)
        update_job(job_id, progress=50)
        time.sleep(1)
        _create_mock_glb(output_glb)
        update_job(job_id, progress=100, model_path=output_glb)
        return output_glb


def _create_mock_glb(path: str):
    """Create a simple mock GLB file using trimesh."""
    try:
        import trimesh
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=0.5)
        mesh.export(path)
    except ImportError:
        import struct
        json_chunk = b'{"asset":{"version":"2.0"},"scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],"meshes":[{"primitives":[{"attributes":{"POSITION":0},"indices":1}]}],"accessors":[{"bufferView":0,"componentType":5126,"count":3,"type":"VEC3","max":[0.5,0.5,0],"min":[-0.5,-0.5,0]},{"bufferView":1,"componentType":5123,"count":3,"type":"SCALAR"}],"bufferViews":[{"buffer":0,"byteOffset":0,"byteLength":36},{"buffer":0,"byteOffset":36,"byteLength":6}],"buffers":[{"byteLength":44}]}'
        while len(json_chunk) % 4 != 0:
            json_chunk += b' '
        vertices = struct.pack('<9f', -0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.0, 0.5, 0.0)
        indices = struct.pack('<3H', 0, 1, 2)
        padding = b'\x00\x00'
        bin_chunk = vertices + indices + padding
        total_length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
        header = struct.pack('<4sII', b'glTF', 2, total_length)
        json_header = struct.pack('<II', len(json_chunk), 0x4E4F534A)
        bin_header = struct.pack('<II', len(bin_chunk), 0x004E4942)
        with open(path, 'wb') as f:
            f.write(header + json_header + json_chunk + bin_header + bin_chunk)
