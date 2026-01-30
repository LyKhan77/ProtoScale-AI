"""
TripoSR Preview Renderer.

Render 2D multi-angle previews from TripoSR 3D mesh output
to maintain compatibility with ProtoScale UI flow.
"""
import io
import numpy as np
from PIL import Image
import trimesh
from typing import List, Tuple, Dict

from app.utils import get_logger

logger = get_logger(__name__)


def render_multi_angle_previews(
    mesh: trimesh.Trimesh,
    angles: List[int] = [0, 90, 180, 270],
    image_size: Tuple[int, int] = (512, 512),
) -> List[Image.Image]:
    """Render 2D previews from TripoSR 3D mesh.

    This function creates 2D rendered views of the 3D mesh from
    different azimuth angles for the ProtoScale ReviewView.

    Args:
        mesh: Trimesh object from TripoSR output
        angles: List of azimuth angles (0=front, 90=right, 180=back, 270=left)
        image_size: Output image size (width, height)

    Returns:
        List of PIL images at each angle

    Raises:
        ValueError: If mesh is invalid
        RuntimeError: If rendering fails
    """
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("Input must be Trimesh object")

    logger.info(f"Rendering {len(angles)} preview angles from TripoSR mesh...")

    preview_images = []

    # Create scene
    scene = trimesh.Scene(geometry=mesh)

    # Calculate camera distance
    radius = scene.scale * 2.5

    for angle in angles:
        try:
            # Calculate camera position for this angle
            rad = np.deg2rad(angle)

            # Set camera
            scene.set_camera(
                angles=[rad, 0, 0],
                distance=radius,
                center=scene.centroid
            )

            # Render scene to PNG buffer
            # trimesh.Scene.save_image() returns a PNG bytes directly
            png_data = scene.save_image(resolution=image_size)

            # Convert to PIL Image
            img = Image.open(io.BytesIO(png_data))
            preview_images.append(img)

            logger.info(f"Rendered angle {angle}°")

        except Exception as e:
            logger.error(f"Failed to render angle {angle}°: {e}")
            # Create error placeholder
            img = Image.new('RGB', image_size, color=(200, 200, 200))
            preview_images.append(img)

    logger.info(f"Rendered {len(preview_images)} preview images")

    return preview_images


def get_mesh_dimensions(mesh: trimesh.Trimesh) -> Dict:
    """Extract dimension metadata from mesh.

    Args:
        mesh: Trimesh object

    Returns:
        Dictionary with dimensions, bounds, volume, area
    """
    bounds = mesh.bounds
    dimensions = {
        'x_mm': float(bounds[1][0] - bounds[0][0]),
        'y_mm': float(bounds[1][1] - bounds[0][1]),
        'z_mm': float(bounds[1][2] - bounds[0][2]),
    }

    return {
        'dimensions': dimensions,
        'bounds': bounds.tolist(),
        'volume_mm3': float(mesh.volume),
        'area_mm2': float(mesh.area),
        'watertight': mesh.is_watertight,
        'manifold': mesh.is_watertight,
    }
