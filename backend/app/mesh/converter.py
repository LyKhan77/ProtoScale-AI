"""Mesh format conversion."""
import trimesh
from pathlib import Path
from typing import Union

from app.utils import get_logger

logger = get_logger(__name__)


class MeshConverter:
    """Mesh format converter for STL and OBJ export."""

    def to_stl(
        self,
        mesh: trimesh.Trimesh,
        output_path: Union[str, Path],
        binary: bool = True,
    ) -> Path:
        """Export mesh to STL format.

        Args:
            mesh: Trimesh object
            output_path: Output file path
            binary: If True, export as binary STL (smaller file)

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)

        logger.info(f"Exporting mesh to STL: {output_path}")

        try:
            # Export to STL
            mesh.export(
                output_path,
                file_type="stl",
            )

            file_size = output_path.stat().st_size / 1024  # KB
            logger.info(f"STL exported: {file_size:.1f} KB")

            return output_path

        except Exception as e:
            logger.error(f"STL export failed: {e}")
            raise

    def to_obj(
        self,
        mesh: trimesh.Trimesh,
        output_path: Union[str, Path],
        include_normals: bool = True,
    ) -> Path:
        """Export mesh to OBJ format.

        Args:
            mesh: Trimesh object
            output_path: Output file path
            include_normals: If True, include vertex normals

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)

        logger.info(f"Exporting mesh to OBJ: {output_path}")

        try:
            # Export to OBJ
            mesh.export(
                output_path,
                file_type="obj",
                include_normals=include_normals,
            )

            file_size = output_path.stat().st_size / 1024  # KB
            logger.info(f"OBJ exported: {file_size:.1f} KB")

            return output_path

        except Exception as e:
            logger.error(f"OBJ export failed: {e}")
            raise

    def to_ply(
        self,
        mesh: trimesh.Trimesh,
        output_path: Union[str, Path],
        binary: bool = True,
    ) -> Path:
        """Export mesh to PLY format.

        Args:
            mesh: Trimesh object
            output_path: Output file path
            binary: If True, export as binary PLY

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)

        logger.info(f"Exporting mesh to PLY: {output_path}")

        try:
            encoding = "binary" if binary else "ascii"
            mesh.export(
                output_path,
                file_type="ply",
                encoding=encoding,
            )

            file_size = output_path.stat().st_size / 1024  # KB
            logger.info(f"PLY exported: {file_size:.1f} KB")

            return output_path

        except Exception as e:
            logger.error(f"PLY export failed: {e}")
            raise

    def from_file(self, input_path: Union[str, Path]) -> trimesh.Trimesh:
        """Load mesh from file.

        Args:
            input_path: Input file path

        Returns:
            Trimesh object
        """
        input_path = Path(input_path)

        logger.info(f"Loading mesh from: {input_path}")

        try:
            mesh = trimesh.load(input_path)

            # Handle scene objects
            if isinstance(mesh, trimesh.Scene):
                # Get geometry from scene
                if len(mesh.geometry) == 0:
                    raise ValueError("No geometry found in scene")

                # Combine all meshes if multiple
                meshes = list(mesh.geometry.values())
                if len(meshes) == 1:
                    mesh = meshes[0]
                else:
                    mesh = trimesh.util.concatenate(meshes)

            logger.info(f"Loaded mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

            return mesh

        except Exception as e:
            logger.error(f"Mesh loading failed: {e}")
            raise
