# ProtoScale-AI Backend

FastAPI backend for image-to-3D generation using Hunyuan3D-2.

## Requirements

- Python 3.10
- NVIDIA GPU with CUDA 12.x
- 16GB+ VRAM (shape + texture), 6GB minimum (shape only)

## Quickstart

### 1. Setup Environment

```bash
cd backend
python3.10 -m venv venv
source venv/bin/activate
```

### 2. Install PyTorch (CUDA 12.8)

Install PyTorch **before** other dependencies. Sesuaikan dengan CUDA version server (`nvcc --version`).

```bash
# CUDA 12.8 (RTX 4090 / RTX 5080)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

Untuk CUDA version lain, cek: https://pytorch.org/get-started/locally/

### 3. Install Hunyuan3D-2

```bash
git clone https://github.com/Tencent/Hunyuan3D-2.git /opt/Hunyuan3D-2
cd /opt/Hunyuan3D-2

# Install dependencies + package
pip install -r requirements.txt
pip install -e .

# Build custom CUDA renderers (required for texture generation)
cd ~/Hunyuan3D-2/hy3dgen/texgen/custom_rasterizer
python3 setup.py install
cd ../../..

cd ~/Hunyuan3D-2/hy3dgen/texgen/differentiable_renderer
python3 setup.py install
cd ../../..
```

### 4. Install Backend Dependencies

```bash
cd /path/to/ProtoScale-AI/backend
pip install -r requirements.txt
```

### 5. Download Model Weights

Weights auto-download on first run (~5-10GB from HuggingFace). Atau pre-download:

```bash
huggingface-cli download tencent/Hunyuan3D-2 --local-dir ./models/Hunyuan3D-2
```

### 6. Run

```bash
export CORS_ORIGINS="http://localhost:5177"  # frontend origin
export HUNYUAN_DEVICE="cuda:0"               # GPU device
# export HUNYUAN_MODEL_PATH=./models/Hunyuan3D-2  # if pre-downloaded

uvicorn app.main:app --host 0.0.0.0 --port 8077 --reload
```

Without Hunyuan3D-2 installed, the server runs in **mock mode** (placeholder outputs).

### 7. Verify

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
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000,http://localhost:5177` | Comma-separated allowed origins |
| `HUNYUAN_DEVICE` | `cuda:0` | PyTorch device |
| `HUNYUAN_MODEL_PATH` | `tencent/Hunyuan3D-2` | HuggingFace model ID or local path |
| `REMBG_MODEL` | `u2net` | rembg model for background removal |

## GPU Strategy

| GPU | Device | Role |
|-----|--------|------|
| RTX 4090 (24GB) | `cuda:1` | Primary — 3D shape generation |
| RTX 5080 (16GB) | `cuda:0` | Fallback / texture generation |
