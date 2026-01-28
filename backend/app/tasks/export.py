"""Mesh export task."""
from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_job_storage, get_export_storage
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.export.export_mesh", bind=True)
def export_mesh(self, repair_result: dict, job_id: str):
    """Export repaired mesh to STL and OBJ formats.

    Args:
        repair_result: Result from mesh repair task with mesh_path and validation
        job_id: Job identifier

    Returns:
        Dictionary with export paths and analysis data
    """
    job_service = get_job_service()
    job_storage = get_job_storage()
    export_storage = get_export_storage()

    try:
        # Update status
        job_service.update_status(job_id, JobStatus.EXPORTING_STL, 90)

        mesh_path = repair_result["mesh_path"]
        validation = repair_result["validation"]

        # Load repaired mesh
        input_path = job_storage.get_path(f"{job_id}/{mesh_path}")

        if not input_path.exists():
            raise FileNotFoundError(f"Repaired mesh not found: {input_path}")

        logger.info(f"Exporting mesh for job {job_id}")

        # Import mesh conversion module
        from app.mesh.converter import MeshConverter
        import trimesh

        # Load mesh
        mesh = trimesh.load(input_path)

        job_service.update_progress(job_id, 92)

        # Create export directory
        export_dir = export_storage.get_path(job_id)
        export_dir.mkdir(parents=True, exist_ok=True)

        # Export to STL
        converter = MeshConverter()
        stl_filename = "model.stl"
        stl_path = export_dir / stl_filename
        converter.to_stl(mesh, stl_path)

        job_service.update_progress(job_id, 95)

        # Export to OBJ
        obj_filename = "model.obj"
        obj_path = export_dir / obj_filename
        converter.to_obj(mesh, obj_path)

        job_service.update_progress(job_id, 98)

        # Compute analysis data
        bounds = mesh.bounds
        dimensions = bounds[1] - bounds[0]

        analysis_data = {
            "watertight": validation.get("watertight", False),
            "manifold": validation.get("manifold", False),
            "dimensions": {
                "x": round(float(dimensions[0]), 2),
                "y": round(float(dimensions[1]), 2),
                "z": round(float(dimensions[2]), 2),
            },
            "volume": round(float(mesh.volume) if mesh.is_watertight else 0, 2),
            "surface_area": round(float(mesh.area), 2),
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
        }

        # Set job to done
        job_service.set_done(
            job_id,
            stl_path=stl_filename,
            obj_path=obj_filename,
            analysis_data=analysis_data,
        )

        logger.info(f"Export complete for job {job_id}: STL={stl_path}, OBJ={obj_path}")

        return {
            "stl_path": stl_filename,
            "obj_path": obj_filename,
            "analysis_data": analysis_data,
        }

    except Exception as e:
        logger.error(f"Export failed for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "export")
        raise
