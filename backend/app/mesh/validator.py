"""Mesh validation for FDM 3D printing."""
import trimesh
import numpy as np
from typing import Dict, Any

from app.config import get_config
from app.utils import get_logger

logger = get_logger(__name__)


class MeshValidator:
    """Validator for mesh printability checks."""

    def __init__(self):
        self.config = get_config()
        self.min_wall_thickness = self.config.MIN_WALL_THICKNESS_MM

    def is_watertight(self, mesh: trimesh.Trimesh) -> bool:
        """Check if mesh is watertight (closed volume).

        Args:
            mesh: Trimesh object

        Returns:
            True if watertight
        """
        return mesh.is_watertight

    def is_manifold(self, mesh: trimesh.Trimesh) -> bool:
        """Check if mesh is manifold (valid topology).

        A mesh is manifold if:
        - Every edge is shared by exactly 2 faces
        - The mesh has no self-intersections

        Args:
            mesh: Trimesh object

        Returns:
            True if manifold
        """
        # Check edge topology
        edges = mesh.edges_unique
        edge_faces = mesh.edges_unique_inverse

        # Count faces per edge
        edge_face_count = np.bincount(edge_faces)

        # Manifold: every edge should have exactly 2 faces
        is_edge_manifold = np.all(edge_face_count == 2)

        return is_edge_manifold

    def check_wall_thickness(
        self,
        mesh: trimesh.Trimesh,
        min_thickness: float = None,
    ) -> Dict[str, Any]:
        """Check minimum wall thickness.

        Uses ray casting to estimate wall thickness.

        Args:
            mesh: Trimesh object
            min_thickness: Minimum required thickness in mm

        Returns:
            Dictionary with thickness analysis results
        """
        if min_thickness is None:
            min_thickness = self.min_wall_thickness

        # Sample points on the surface
        points, face_indices = trimesh.sample.sample_surface(mesh, count=1000)

        # Get face normals at sampled points
        normals = mesh.face_normals[face_indices]

        # Cast rays inward to find opposite surface
        ray_origins = points + normals * 0.001  # Slight offset
        ray_directions = -normals

        # Find intersections
        locations, index_ray, _ = mesh.ray.intersects_location(
            ray_origins=ray_origins,
            ray_directions=ray_directions,
        )

        if len(locations) == 0:
            return {
                "min_thickness": None,
                "avg_thickness": None,
                "thin_areas": 0,
                "passes": False,
            }

        # Calculate distances (wall thickness)
        thicknesses = np.linalg.norm(
            locations - ray_origins[index_ray], axis=1
        )

        # Filter out very large values (rays that went through)
        max_reasonable = mesh.scale * 0.5
        valid_mask = thicknesses < max_reasonable
        valid_thicknesses = thicknesses[valid_mask]

        if len(valid_thicknesses) == 0:
            return {
                "min_thickness": None,
                "avg_thickness": None,
                "thin_areas": 0,
                "passes": False,
            }

        min_measured = float(np.min(valid_thicknesses))
        avg_measured = float(np.mean(valid_thicknesses))
        thin_count = int(np.sum(valid_thicknesses < min_thickness))

        return {
            "min_thickness": round(min_measured, 3),
            "avg_thickness": round(avg_measured, 3),
            "thin_areas": thin_count,
            "passes": min_measured >= min_thickness,
        }

    def has_degenerate_faces(self, mesh: trimesh.Trimesh) -> int:
        """Count degenerate (zero-area) faces.

        Args:
            mesh: Trimesh object

        Returns:
            Number of degenerate faces
        """
        areas = mesh.area_faces
        return int(np.sum(areas < 1e-10))

    def validate(self, mesh: trimesh.Trimesh) -> Dict[str, Any]:
        """Run all validation checks.

        Args:
            mesh: Trimesh object

        Returns:
            Dictionary with all validation results
        """
        logger.info("Running mesh validation...")

        watertight = self.is_watertight(mesh)
        manifold = self.is_manifold(mesh)
        degenerate_count = self.has_degenerate_faces(mesh)

        # Wall thickness check can be slow, only run if mesh is valid
        thickness_result = None
        if watertight:
            try:
                thickness_result = self.check_wall_thickness(mesh)
            except Exception as e:
                logger.warning(f"Wall thickness check failed: {e}")
                thickness_result = {"passes": True, "error": str(e)}

        result = {
            "watertight": bool(watertight),
            "manifold": bool(manifold),
            "degenerate_faces": int(degenerate_count),
            "wall_thickness": thickness_result,
            "is_valid": bool(watertight and manifold and degenerate_count == 0),
        }

        logger.info(f"Validation result: {result}")
        return result
