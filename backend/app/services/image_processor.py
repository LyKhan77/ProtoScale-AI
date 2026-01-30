import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def remove_background(input_path: str, output_path: str) -> str:
    """Remove background from image using rembg.
    Always saves as PNG to support RGBA transparency.
    """
    from rembg import remove
    from PIL import Image

    logger.info(f"Removing background: {input_path}")
    inp = Image.open(input_path)
    out = remove(inp)

    # Always save as PNG (supports RGBA)
    png_path = str(Path(output_path).with_suffix(".png"))
    out.save(png_path)
    logger.info(f"Background removed: {png_path}")
    return png_path
