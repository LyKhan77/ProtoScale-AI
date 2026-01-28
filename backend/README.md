# AI 3D Miniature Generator - Backend

Flask-based asynchronous backend for the image-to-3D-STL pipeline with Celery workers for GPU inference.

## Architecture

```
Frontend (Vue 3) → Flask REST API → Celery + Redis → GPU Workers → Storage
```

## Quick Start

### Prerequisites

- Python 3.11+
- Redis
- CUDA-capable GPU (optional, for AI models)

### Local Development

1. **Start Redis:**
   ```bash
   docker run -d -p 6352:6379 redis:7-alpine
   ```

2. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

5. **Start Flask API:**
   ```bash
   flask run --debug
   ```

6. **Start Celery workers (in separate terminals):**
   ```bash
   # GPU worker
   celery -A app.tasks worker -Q gpu --concurrency=1 --loglevel=info

   # CPU worker
   celery -A app.tasks worker -Q cpu --concurrency=4 --loglevel=info
   ```

### Docker Development

```bash
docker-compose up -d
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload image, start processing pipeline |
| GET | `/api/job/{job_id}` | Get job status and progress |
| GET | `/api/result/{job_id}` | Get complete job results |
| GET | `/api/download/{job_id}/stl` | Download STL file |
| GET | `/api/download/{job_id}/obj` | Download OBJ file |
| GET | `/api/health` | Health check (GPU, Redis status) |

## Processing Pipeline

1. **Multi-angle Generation** (GPU) - Uses Qwen Image Edit with LoRA
2. **Preprocessing** (CPU) - Background removal with rembg
3. **3D Reconstruction** (GPU) - TripoSR from Stability AI
4. **Mesh Repair** (CPU) - Trimesh validation and repair
5. **Export** (CPU) - STL/OBJ conversion

## Configuration

See `.env.example` for available environment variables.

## Testing

```bash
# Test upload
curl -X POST -F "image=@test.jpg" http://localhost:5000/api/upload

# Check status
curl http://localhost:5000/api/job/{job_id}

# Get result
curl http://localhost:5000/api/result/{job_id}

# Health check
curl http://localhost:5000/api/health
```
