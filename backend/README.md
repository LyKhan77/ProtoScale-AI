# ProtoScale-AI Backend

FastAPI backend for image-to-3D generation using Hunyuan3D-2.

## Quickstart

### 1. Setup Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Hunyuan3D-2

```bash
git clone https://github.com/Tencent/Hunyuan3D-2.git /opt/Hunyuan3D-2
cd /opt/Hunyuan3D-2
pip install -e .
```

Model weights auto-download on first run (~5-10GB from HuggingFace).

To pre-download:
```bash
huggingface-cli download tencent/Hunyuan3D-2 --local-dir ./models/Hunyuan3D-2
```

### 3. Run

```bash
export CORS_ORIGINS="http://localhost:5177"  # frontend origin
export HUNYUAN_DEVICE="cuda:0"               # GPU device
# export HUNYUAN_MODEL_PATH=./models/Hunyuan3D-2  # if pre-downloaded

uvicorn app.main:app --host 0.0.0.0 --port 8077 --reload
```

Without Hunyuan3D-2 installed, the server runs in **mock mode** (placeholder outputs).

### 4. Verify

```bash
curl http://localhost:8077/health
# {"status":"ok"}
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload` | Upload image (multipart form: `file`, `remove_bg`, `enhanced_detail`) |
| POST | `/api/jobs/{id}/generate-multiangle` | Trigger 4-angle generation |
| POST | `/api/jobs/{id}/generate-3d` | Trigger 3D mesh generation |
| GET | `/api/jobs/{id}/status` | Poll job status + progress (0-100) |
| GET | `/api/jobs/{id}/result/{asset}` | Download `view_0.png`...`view_3.png` or `model.glb` |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated allowed origins |
| `HUNYUAN_DEVICE` | `cuda:0` | PyTorch device |
| `HUNYUAN_MODEL_PATH` | `tencent/Hunyuan3D-2` | HuggingFace model ID or local path |
| `REMBG_MODEL` | `u2net` | rembg model for background removal |
