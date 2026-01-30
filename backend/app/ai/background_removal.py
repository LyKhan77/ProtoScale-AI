"""Background removal using rembg.

Runs on GPU (CUDA) when available for faster inference.
RTX 4090: U2Net uses ~200MB VRAM.
"""
from PIL import Image
import io

from app.utils import get_logger

logger = get_logger(__name__)

# Global session singleton
_session = None


def get_session():
    """Get or create rembg session with GPU acceleration."""
    global _session

    if _session is not None:
        return _session

    try:
        from rembg import new_session
        import onnxruntime as ort

        # Use CUDA if available (RTX 4090), otherwise CPU
        available_providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in available_providers:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            logger.info("rembg: Using CUDA GPU acceleration")
        else:
            providers = ["CPUExecutionProvider"]
            logger.info("rembg: CUDA not available, using CPU")

        _session = new_session("u2net", providers=providers)
        logger.info("Background removal session created")

    except ImportError:
        logger.warning("rembg not installed, background removal will be skipped")
        _session = "fallback"

    except Exception as e:
        logger.warning(f"GPU session failed ({e}), falling back to CPU")
        try:
            from rembg import new_session
            _session = new_session("u2net")
            logger.info("Background removal session created (CPU fallback)")
        except Exception:
            _session = "fallback"

    return _session


def remove_background(image: Image.Image) -> Image.Image:
    """Remove background from image.

    Args:
        image: Input PIL image

    Returns:
        PIL image with transparent background (RGBA)
    """
    session = get_session()

    # Handle fallback case
    if session == "fallback":
        logger.info("Using fallback (no background removal)")
        if image.mode != "RGBA":
            return image.convert("RGBA")
        return image

    logger.info("Removing background from image")

    try:
        from rembg import remove

        # Convert to bytes for rembg
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # Remove background
        output_bytes = remove(
            img_byte_arr.getvalue(),
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
        )

        # Convert back to PIL
        result = Image.open(io.BytesIO(output_bytes))

        logger.info("Background removed successfully")
        return result

    except Exception as e:
        logger.error(f"Background removal failed: {e}")
        # Return original with alpha channel as fallback
        if image.mode != "RGBA":
            return image.convert("RGBA")
        return image


def cleanup():
    """Release session resources."""
    global _session
    if _session is not None and _session != "fallback":
        del _session
        _session = None
        logger.info("Background removal session cleaned up")
