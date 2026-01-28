"""Mesh repair operations."""
import trimesh
import numpy as np
from typing import Optional

from app.utils import get_logger

logger = get_logger(__name__)


class MeshRepairer:
    """Mesh repair operations for FDM printing."""

    def fill_holes(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Fill holes in the mesh.

        Args:
            mesh: Trimesh object

        Returns:
            Mesh with holes filled
        """
        if mesh.is_watertight:
            logger.info("Mesh is already watertight, skipping hole filling")
            return mesh

        logger.info("Filling holes in mesh...")

        try:
            # Use trimesh's fill_holes method
            filled = mesh.copy()
            filled.fill_holes()

            logger.info(f"Holes filled. Watertight: {filled.is_watertight}")
            return filled

        except Exception as e:
            logger.warning(f"Hole filling failed: {e}")
            return mesh

    def fix_normals(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Fix face normals to point outward consistently.

        Args:
            mesh: Trimesh object

        Returns:
            Mesh with fixed normals
        """
        logger.info("Fixing face normals...")

        try:
            repaired = mesh.copy()
            repaired.fix_normals()

            logger.info("Normals fixed")
            return repaired

        except Exception as e:
            logger.warning(f"Normal fixing failed: {e}")
            return mesh

    def remove_degenerate(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Remove degenerate (zero-area) faces.

        Args:
            mesh: Trimesh object

        Returns:
            Mesh with degenerate faces removed
        """
        logger.info("Removing degenerate faces...")

        try:
            areas = mesh.area_faces
            valid_mask = areas > 1e-10

            if np.all(valid_mask):
                logger.info("No degenerate faces found")
                return mesh

            removed_count = int(np.sum(~valid_mask))

            # Create new mesh without degenerate faces
            valid_faces = mesh.faces[valid_mask]
            repaired = trimesh.Trimesh(
                vertices=mesh.vertices,
                faces=valid_faces,
                process=True,
            )

            logger.info(f"Removed {removed_count} degenerate faces")
            return repaired

        except Exception as e:
            logger.warning(f"Degenerate removal failed: {e}")
            return mesh

    def remove_duplicate_faces(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Remove duplicate faces.

        Args:
            mesh: Trimesh object

        Returns:
            Mesh with duplicates removed
        """
        logger.info("Removing duplicate faces...")

        try:
            repaired = mesh.copy()

            # Sort face vertex indices for comparison
            faces_sorted = np.sort(repaired.faces, axis=1)

            # Find unique faces
            _, unique_indices = np.unique(
                faces_sorted, axis=0, return_index=True
            )

            if len(unique_indices) == len(repaired.faces):
                logger.info("No duplicate faces found")
                return repaired

            removed_count = len(repaired.faces) - len(unique_indices)

            # Keep only unique faces
            unique_faces = repaired.faces[unique_indices]
            repaired = trimesh.Trimesh(
                vertices=repaired.vertices,
                faces=unique_faces,
                process=True,
            )

            logger.info(f"Removed {removed_count} duplicate faces")
            return repaired

        except Exception as e:
            logger.warning(f"Duplicate removal failed: {e}")
            return mesh

    def merge_close_vertices(
        self,
        mesh: trimesh.Trimesh,
        tolerance: float = 1e-8,
    ) -> trimesh.Trimesh:
        """Merge vertices that are very close together.

        Args:
            mesh: Trimesh object
            tolerance: Distance threshold for merging

        Returns:
            Mesh with merged vertices
        """
        logger.info(f"Merging close vertices (tolerance={tolerance})...")

        try:
            repaired = mesh.copy()
            repaired.merge_vertices(merge_tex=True, merge_norm=True)

            original_count = len(mesh.vertices)
            new_count = len(repaired.vertices)

            if new_count < original_count:
                logger.info(f"Merged {original_count - new_count} vertices")
            else:
                logger.info("No vertices merged")

            return repaired

        except Exception as e:
            logger.warning(f"Vertex merging failed: {e}")
            return mesh

    def repair(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Run all repair operations.

        Args:
            mesh: Trimesh object

        Returns:
            Repaired mesh
        """
        logger.info("Starting mesh repair...")

        # Apply repairs in order
        repaired = mesh.copy()

        # 1. Merge close vertices
        repaired = self.merge_close_vertices(repaired)

        # 2. Remove degenerate faces
        repaired = self.remove_degenerate(repaired)

        # 3. Remove duplicate faces
        repaired = self.remove_duplicate_faces(repaired)

        # 4. Fix normals
        repaired = self.fix_normals(repaired)

        # 5. Fill holes
        repaired = self.fill_holes(repaired)

        logger.info(f"Repair complete. Vertices: {len(repaired.vertices)}, Faces: {len(repaired.faces)}")

        return repaired
