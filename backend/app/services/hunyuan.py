import logging
import shutil
from pathlib import Path
from typing import Optional

from app.config import DEVICE, MODEL_PATH, OUTPUTS_DIR
from app.workers.task_queue import update_job

logger = logging.getLogger(__name__)

_pipeline = None


def load_model():
    """Load Hunyuan3D-2 pipeline at startup."""
    global _pipeline
    try:
        from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
        logger.info(f"Loading Hunyuan3D-2 from {MODEL_PATH} on {DEVICE}")
        _pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            MODEL_PATH,
            device=DEVICE,
        )
        logger.info("Hunyuan3D-2 model loaded successfully")
    except ImportError:
        logger.warning(
            "hy3dgen not installed. Running in mock mode. "
            "Install Hunyuan3D-2 for real inference."
        )
        _pipeline = None
    except Exception as e:
        logger.error(f"Failed to load Hunyuan3D-2: {e}")
        _pipeline = None


def generate_multiview(job_id: str, image_path: str) -> list[str]:
    """Generate 4 multi-view images from a single input image."""
    update_job(job_id, status="processing", stage="multiview", progress=10)

    job_output_dir = OUTPUTS_DIR / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)

    if _pipeline is not None:
        try:
            from hy3dgen.texgen import Hunyuan3DPaintPipeline
            from PIL import Image

            update_job(job_id, progress=20)
            image = Image.open(image_path)

            # Hunyuan3D-2 generates multi-view internally
            # Use the pipeline's multi-view generation
            result = _pipeline(
                image=image,
                num_inference_steps=50,
            )
            update_job(job_id, progress=60)

            # Save multi-view images if available
            views = []
            if hasattr(result, 'mv_images') and result.mv_images is not None:
                for i, mv_img in enumerate(result.mv_images):
                    path = str(job_output_dir / f"view_{i}.png")
                    mv_img.save(path)
                    views.append(path)

            if not views:
                # Fallback: use input as all 4 views
                for i in range(4):
                    dst = str(job_output_dir / f"view_{i}.png")
                    shutil.copy2(image_path, dst)
                    views.append(dst)

            update_job(job_id, progress=100, multi_angle_paths=views)
            return views
        except Exception as e:
            logger.error(f"Multi-view generation failed: {e}")
            raise
    else:
        # Mock mode: copy input image 4 times
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
    """Generate 3D GLB model from input image."""
    update_job(job_id, status="processing", stage="3d_generation", progress=10)

    job_output_dir = OUTPUTS_DIR / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)
    output_glb = str(job_output_dir / "model.glb")

    if _pipeline is not None:
        try:
            from PIL import Image

            update_job(job_id, progress=20)
            image = Image.open(image_path)

            result = _pipeline(
                image=image,
                num_inference_steps=50,
            )
            update_job(job_id, progress=70)

            # Export mesh to GLB
            if hasattr(result, 'mesh') and result.mesh is not None:
                result.mesh.export(output_glb)
            elif hasattr(result, 'export'):
                result.export(output_glb)
            else:
                raise RuntimeError("Pipeline result has no exportable mesh")

            update_job(job_id, progress=100, model_path=output_glb)
            return output_glb
        except Exception as e:
            logger.error(f"3D generation failed: {e}")
            raise
    else:
        # Mock mode: create a simple GLB placeholder
        import time
        time.sleep(2)
        update_job(job_id, progress=50)
        time.sleep(1)

        _create_mock_glb(output_glb)
        update_job(job_id, progress=100, model_path=output_glb)
        return output_glb


def _create_mock_glb(path: str):
    """Create a simple mock GLB file using trimesh if available."""
    try:
        import trimesh
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=0.5)
        mesh.export(path)
    except ImportError:
        # Create minimal valid GLB (empty scene)
        import struct
        # Minimal glTF 2.0 binary
        json_chunk = b'{"asset":{"version":"2.0"},"scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],"meshes":[{"primitives":[{"attributes":{"POSITION":0},"indices":1}]}],"accessors":[{"bufferView":0,"componentType":5126,"count":3,"type":"VEC3","max":[0.5,0.5,0],"min":[-0.5,-0.5,0]},{"bufferView":1,"componentType":5123,"count":3,"type":"SCALAR"}],"bufferViews":[{"buffer":0,"byteOffset":0,"byteLength":36},{"buffer":0,"byteOffset":36,"byteLength":6}],"buffers":[{"byteLength":44}]}'
        # Pad JSON to 4-byte alignment
        while len(json_chunk) % 4 != 0:
            json_chunk += b' '
        # Binary buffer: 3 vertices (9 floats) + 3 indices (3 uint16) + padding
        import struct
        vertices = struct.pack('<9f', -0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.0, 0.5, 0.0)
        indices = struct.pack('<3H', 0, 1, 2)
        padding = b'\x00\x00'  # pad to 4 bytes
        bin_chunk = vertices + indices + padding

        # GLB header
        total_length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
        header = struct.pack('<4sII', b'glTF', 2, total_length)
        json_header = struct.pack('<II', len(json_chunk), 0x4E4F534A)
        bin_header = struct.pack('<II', len(bin_chunk), 0x004E4942)

        with open(path, 'wb') as f:
            f.write(header + json_header + json_chunk + bin_header + bin_chunk)
