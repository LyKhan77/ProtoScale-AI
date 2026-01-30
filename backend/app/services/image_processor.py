import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def remove_background(input_path: str, output_path: str) -> str:
    """Remove background from image using rembg."""
    from rembg import remove
    from PIL import Image

    logger.info(f"Removing background: {input_path}")
    inp = Image.open(input_path)
    out = remove(inp)
    out.save(output_path)
    logger.info(f"Background removed: {output_path}")
    return output_path
