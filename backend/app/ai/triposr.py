"""TripoSR 3D reconstruction.

Uses TripoSR from Stability AI for single-image 3D reconstruction.
Reference: https://github.com/VAST-AI-Research/TripoSR
"""
import torch
from PIL import Image
import trimesh
from typing import Optional

from app.config import get_config
from app.utils import get_logger

logger = get_logger(__name__)

# Global model singleton
_model = None


def get_device():
    """Get the appropriate device for inference."""
    config = get_config()
    if config.GPU_DEVICE == "cuda" and torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model():
    """Load the TripoSR model."""
    global _model

    if _model is not None:
        return _model

    logger.info("Loading TripoSR model...")

    device = get_device()
    config = get_config()

    try:
        from tsr.system import TSR

        logger.info(f"Loading TripoSR from {config.TRIPOSR_MODEL_ID}...")

        # Load on CPU first - will move to GPU only during inference
        _model = TSR.from_pretrained(
            config.TRIPOSR_MODEL_ID,
            config_name="config.yaml",
            weight_name="model.ckpt",
        ).cpu()

        # Set to eval mode
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


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess image for TripoSR.

    Args:
        image: Input PIL image

    Returns:
        Preprocessed PIL image
    """
    # Ensure RGB
    if image.mode == "RGBA":
        # Create white background
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")

    # Resize to 256x256 (TripoSR expected size)
    if image.size != (256, 256):
        image = image.resize((256, 256), Image.Resampling.LANCZOS)

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

    Args:
        image: Input PIL image (preferably with background removed)
        resolution: Mesh extraction resolution (default from config)

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

    # Preprocess image
    processed_image = preprocess_image(image)

    try:
        # Move model to GPU for inference
        logger.info(f"Moving TripoSR to {device} for inference...")
        model.to(device)

        with torch.no_grad():
            # Run inference
            scene_codes = model([processed_image], device=device)

            # Extract mesh
            meshes = model.extract_mesh(scene_codes, resolution=resolution)

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
