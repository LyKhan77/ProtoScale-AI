"""TripoSR 3D reconstruction.

Uses TripoSR from Stability AI for single-image 3D reconstruction.
Reference: https://github.com/VAST-AI-Research/TripoSR
"""
import numpy as np
import torch
from PIL import Image
import trimesh
from typing import Optional

from app.config import get_config
from app.utils import get_logger

logger = get_logger(__name__)

# Global model singleton
_model = None

# Default chunk size for surface extraction (from official run.py)
DEFAULT_CHUNK_SIZE = 8192

# Default foreground ratio (from official run.py)
DEFAULT_FOREGROUND_RATIO = 0.85


def get_device():
    """Get the appropriate device for inference."""
    config = get_config()
    if config.GPU_DEVICE == "cuda" and torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model():
    """Load the TripoSR model.

    Follows official initialization from run.py:
        model = TSR.from_pretrained(...)
        model.renderer.set_chunk_size(chunk_size)
    """
    global _model

    if _model is not None:
        return _model

    logger.info("Loading TripoSR model...")

    config = get_config()

    try:
        from tsr.system import TSR

        logger.info(f"Loading TripoSR from {config.TRIPOSR_MODEL_ID}...")

        _model = TSR.from_pretrained(
            config.TRIPOSR_MODEL_ID,
            config_name="config.yaml",
            weight_name="model.ckpt",
        )

        # Set chunk size for surface extraction (official default: 8192)
        _model.renderer.set_chunk_size(DEFAULT_CHUNK_SIZE)

        # Keep on CPU, move to GPU only during inference
        _model.cpu()
        _model.eval()

        logger.info("TripoSR model loaded on CPU (will move to GPU for inference)")

    except ImportError as e:
        logger.error(f"TripoSR not installed: {e}. Using fallback mesh generation")
        _model = "fallback"

    except Exception as e:
        logger.error(f"Failed to load TripoSR model: {type(e).__name__}: {e}", exc_info=True)
        logger.warning("Falling back to simple mesh generation")
        _model = "fallback"

    return _model


def preprocess_image(image: Image.Image, foreground_ratio: float = DEFAULT_FOREGROUND_RATIO) -> Image.Image:
    """Preprocess image for TripoSR following official run.py pipeline.

    Official pipeline:
        1. remove_background (via tsr.utils)
        2. resize_foreground to ratio 0.85
        3. Composite on gray (0.5) background
        4. Convert to uint8 PIL Image

    Since background removal is already done in our preprocessing step,
    we use resize_foreground + gray background compositing here.

    Args:
        image: Input PIL image (RGBA with background removed, or RGB)
        foreground_ratio: Ratio of foreground to image size (default 0.85)

    Returns:
        Preprocessed PIL image ready for TripoSR inference
    """
    try:
        from tsr.utils import resize_foreground
    except ImportError:
        # Fallback if tsr.utils not available
        logger.warning("tsr.utils not available, using basic preprocessing")
        return _basic_preprocess(image)

    # If image is RGBA (background already removed), use resize_foreground
    if image.mode == "RGBA":
        image = resize_foreground(image, foreground_ratio)
        # Composite on gray background (matching official run.py)
        image = np.array(image).astype(np.float32) / 255.0
        image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
        image = Image.fromarray((image * 255.0).astype(np.uint8))
    elif image.mode != "RGB":
        image = image.convert("RGB")

    return image


def _basic_preprocess(image: Image.Image) -> Image.Image:
    """Basic fallback preprocessing when tsr.utils is not available."""
    if image.mode == "RGBA":
        # Composite on gray background
        arr = np.array(image).astype(np.float32) / 255.0
        rgb = arr[:, :, :3] * arr[:, :, 3:4] + (1 - arr[:, :, 3:4]) * 0.5
        image = Image.fromarray((rgb * 255.0).astype(np.uint8))
    elif image.mode != "RGB":
        image = image.convert("RGB")
    return image


def create_fallback_mesh() -> trimesh.Trimesh:
    """Create a simple fallback mesh for testing.

    Returns:
        A simple sphere mesh
    """
    logger.info("Creating fallback mesh (sphere)")
    return trimesh.creation.icosphere(subdivisions=3, radius=1.0)


def reconstruct_mesh(
    image: Image.Image,
    resolution: int = None,
) -> trimesh.Trimesh:
    """Reconstruct 3D mesh from a single image.

    Follows official run.py inference flow:
        scene_codes = model([image], device=device)
        meshes = model.extract_mesh(scene_codes, has_vertex_color, resolution=resolution)

    Args:
        image: Input PIL image (preferably with background removed)
        resolution: Marching cubes grid resolution (default from config)

    Returns:
        Trimesh object
    """
    model = load_model()
    config = get_config()
    device = get_device()

    if resolution is None:
        resolution = config.MESH_RESOLUTION

    # Handle fallback case
    if model == "fallback":
        return create_fallback_mesh()

    logger.info(f"Reconstructing 3D mesh at resolution {resolution}")

    # Preprocess image (resize_foreground + gray bg compositing)
    processed_image = preprocess_image(image)

    try:
        # Move model to GPU for inference
        logger.info(f"Moving TripoSR to {device} for inference...")
        model.to(device)

        with torch.no_grad():
            # Run inference (official: model([image], device=device))
            scene_codes = model([processed_image], device=device)

            # Extract mesh (official: model.extract_mesh(scene_codes, True, resolution=mc_resolution))
            # First positional bool = has_vertex_color (True when not baking texture)
            meshes = model.extract_mesh(scene_codes, True, resolution=resolution)

            if len(meshes) == 0:
                raise ValueError("No mesh generated")

            mesh = meshes[0]

            logger.info(f"Mesh reconstructed: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

            return mesh

    except Exception as e:
        logger.error(f"Mesh reconstruction failed: {e}")
        raise

    finally:
        # Always move back to CPU and free GPU memory
        model.cpu()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("TripoSR moved back to CPU, GPU memory freed")


def cleanup():
    """Release model resources."""
    global _model
    if _model is not None and _model != "fallback":
        del _model
        _model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("TripoSR model cleaned up")
