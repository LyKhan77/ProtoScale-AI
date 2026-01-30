# 🚀 Start Services Guide - TripoSR-Only Pipeline

> **Version**: 1.0 (Phase 1 Complete)
> **Date**: 2026-01-30
> **Pipeline**: TripoSR-only (5 stages)

---

## 📋 Overview

Guide ini menjelaskan cara menjalankan **ProtoScale backend services** setelah migrasi ke TripoSR-only pipeline.

**Services yang diperlukan:**
1. **Redis** - Message broker untuk Celery
2. **Flask API** - REST API server
3. **Celery GPU Worker** - TripoSR reconstruction
4. **Celery CPU Worker** - Preprocessing, mesh repair, export
5. **Frontend Dev Server** - Vue 3 + Vite (opsional)

---

## 🔧 Prerequisites Check

Sebelum memulai, pastikan:

```bash
# Python version
python3 --version
# Expected: Python 3.9+ (recommended: 3.11+)

# Redis availability
redis-cli ping
# Expected: PONG

# GPU availability (opsional tapi recommended)
nvidia-smi
# Expected: GPU info jika NVIDIA GPU available

# Node.js (untuk frontend)
node --version
# Expected: v18+ (recommended: v20+)
```

---

## 🐳 Method 1: Docker Compose (Recommended)

### **Keuntungan:**
- ✅ Semua services dalam satu command
- ✅ Isolated environment
- ✅ Easy cleanup
- ✅ Production-ready

### **Start semua services:**

```bash
cd backend

# Start semua services (Redis + API + 2 workers)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop semua services
docker-compose down
```

### **Service endpoints:**
- Flask API: `http://localhost:5000`
- Redis: `localhost:6352`

---

## 💻 Method 2: Local Development (Manual)

### **Keuntungan:**
- ✅ Live code editing tanpa rebuild
- ✅ Debugging lebih mudah
- ✅ Faster iteration

### **Step-by-step:**

#### **Terminal 1: Redis**

```bash
# Start Redis pada port 6352
redis-server --port 6352

# Atau dengan Docker
docker run -d -p 6352:6379 redis:7-alpine

# Verify Redis running
redis-cli -p 6352 ping
# Expected: PONG
```

#### **Terminal 2: Flask API**

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Set environment (optional)
export FLASK_ENV=development
export FLASK_APP=app

# Start Flask API server
flask run --host=0.0.0.0 --port=5000

# Atau dengan Python directly
python -m flask run --host=0.0.0.0 --port=5000
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

#### **Terminal 3: Celery GPU Worker**

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Start GPU worker (untuk TripoSR)
celery -A app.tasks worker -Q gpu --concurrency=1 --loglevel=info
```

**Expected output:**
```
 -------------- celery@xxx v5.x.x
---- **** ----- 
--- * ***  * -- Linux/Darwin- [config]
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app.tasks.pipeline:        *  app.tasks.reconstruction: *  app.tasks.preprocessing: *
- ** ---------- .> app.tasks.mesh_repair:     *  app.tasks.export:          *  app.tasks.pipeline: *
- ** ---------- .> app.tasks.reconstruction:  *  app.tasks.preprocessing:  *  app.tasks.mesh_repair: *
- ** ---------- .> app.tasks.export:          *  app.tasks.reconstruction:  *  app.tasks.preprocessing: *
-- * ----- ****--- .> app.tasks.mesh_repair:  *  app.tasks.export:          *  app.tasks.pipeline: *
-- * ----- ****--- .> app.tasks.export:          *  app.tasks.reconstruction:  *  app.tasks.preprocessing: *

[tasks]
. app.tasks.pipeline.start_pipeline
. app.tasks.preprocess ing.preprocess_image
. app.tasks.reconstruction.reconstruct_3d
. app.tasks.mesh_repair.repair_mesh
. app.tasks.export.export_mesh
. app.tasks.triposr_pipeline.render_previews

[queues]
. gpu> app.tasks.preprocessing.*, app.tasks.reconstruction.*
. cpu> app.tasks.mesh_repair.*, app.tasks.export.*, app.tasks.pipeline.*

[2026-01-30 10:00:00,123: INFO/MainProcess] Connected to redis://localhost:6352/0
[2026-01-30 10:00:00,124: INFO/MainProcess] celery@xxx ready.
```

**Key points:**
- ✅ `render_previews` task terdaftar
- ✅ GPU queue menerima preprocessing dan reconstruction tasks
- ✅ CPU queue menerima mesh repair, export, dan pipeline tasks

#### **Terminal 4: Celery CPU Worker**

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Start CPU worker (4 concurrency)
celery -A app.tasks worker -Q cpu --concurrency=4 --loglevel=info
```

**Expected output:**
```
 -------------- celery@xxx v5.x.x
---- **** ----- 
--- * ***  * -- Linux/Darwin- [config]
-- * - **** --- 

[queues]
. gpu> (untuk preprocessing, reconstruction)
. cpu> app.tasks.mesh_repair.*, app.tasks.export.*, app.tasks.pipeline.*, app.tasks.triposr_pipeline.*

[2026-01-30 10:00:00,123: INFO/MainProcess] Connected to redis://localhost:6352/0
[2026-01-30 10:00:00,124: INFO/MainProcess] celery@xxx ready.
```

#### **Terminal 5: Frontend (Optional)**

```bash
cd frontend

# Install dependencies (jika belum)
npm install

# Start dev server
npm run dev
```

**Expected output:**
```
VITE v5.x.x ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## ✅ Verification Steps

### **1. Check Redis**

```bash
redis-cli -p 6352 ping
# Expected: PONG
```

### **2. Check Flask API**

```bash
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "gpu_available": true
}
```

### **3. Check Celery Workers**

```bash
# Inspect active workers
celery -A app.tasks inspect active

# Check registered tasks
celery -A app.tasks inspect registered
```

**Expected tasks:**
- ✅ `app.tasks.pipeline.start_pipeline`
- ✅ `app.tasks.preprocessing.preprocess_image`
- ✅ `app.tasks.reconstruction.reconstruct_3d`
- ✅ `app.tasks.triposr_pipeline.render_previews` ← **NEW!**
- ✅ `app.tasks.mesh_repair.repair_mesh`
- ✅ `app.tasks.export.export_mesh`

### **4. Check Frontend**

Buka browser: `http://localhost:5173`

**Expected:**
- ✅ Upload view muncul
- ✅ No errors di browser console

---

## 🎯 Pipeline Flow Verification

Setelah semua services berjalan, pipeline seharusnya:

```
Upload Image
    ↓
[Preprocessing] - GPU worker - Background removal (rembg)
    ↓
[Reconstruction] - GPU worker - TripoSR 3D reconstruction
    ↓
[Render Previews] - CPU worker - Multi-angle preview generation ← NEW!
    ↓
[Mesh Repair] - CPU worker - Trimesh validation & repair
    ↓
[Export] - CPU worker - STL/OBJ conversion
    ↓
DONE
```

**Task routing:**
- **GPU queue**: `preprocessing.*`, `reconstruction.*`
- **CPU queue**: `triposr_pipeline.*`, `mesh_repair.*`, `export.*`, `pipeline.*`

---

## 🔍 Troubleshooting

### **Issue 1: Redis connection refused**

**Symptom:**
```
Error 111 connecting to localhost:6352: Connection refused
```

**Solution:**
```bash
# Check Redis running
redis-cli -p 6352 ping

# Start Redis jika belum running
redis-server --port 6352

# Atau dengan Docker
docker run -d -p 6352:6379 redis:7-alpine
```

---

### **Issue 2: Celery worker tidak menerima tasks**

**Symptom:**
```
Task queue tidak terprocessed
```

**Solution:**
```bash
# Check worker connectivity
celery -A app.tasks inspect active

# Verify queue configuration
celery -A app.tasks inspect conf

# Pastikan worker listening ke correct queue:
# GPU worker harus listening ke: gpu
# CPU worker harus listening ke: cpu
```

---

### **Issue 3: TripoSR model tidak ter-load**

**Symptom:**
```
Error loading TripoSR model
```

**Solution:**
```bash
# Check GPU availability
nvidia-smi

# Verify CUDA PyTorch installed
python -c "import torch; print(torch.cuda.is_available())"
# Expected: True

# Check model download cache
ls -lh ~/.cache/huggingface/hub/
# Pastikan TripoSR model terdownload
```

---

### **Issue 4: Preview rendering gagal**

**Symptom:**
```
Failed to render angle X°
```

**Solution:**
```bash
# Verify trimesh installed
python -c "import trimesh; print(trimesh.__version__)"

# Check PIL/Pillow
python -c "from PIL import Image; print(Image.__version__)"

# Test render manually
python -c "
from app.ai.triposr_renderer import render_multi_angle_previews
import trimesh

mesh = trimesh.creation.icosphere()
images = render_multi_angle_previews(mesh)
print(f'Rendered {len(images)} angles')
"
```

---

## 📊 Performance Expectations

### **Processing Time (per job)**

| Stage | Queue | Time | VRAM |
|-------|-------|------|------|
| Preprocessing | GPU | 1-2s | ~200MB |
| Reconstruction | GPU | 0.5-1s | ~6GB |
| Render Previews | CPU | 1-2s | - |
| Mesh Repair | CPU | 2-3s | - |
| Export | CPU | 1s | - |
| **TOTAL** | | **5-10s** | **~6.2GB peak** |

### **Worker Concurrency**

- **GPU worker**: `--concurrency=1` (satu job pada satu waktu untuk VRAM management)
- **CPU worker**: `--concurrency=4` (4 parallel jobs untuk CPU-bound tasks)

---

## 🧪 Quick Test

Setelah semua services berjalan, test pipeline:

```bash
# 1. Upload test image
curl -X POST \
  -F "image=@test.jpg" \
  http://localhost:5000/api/upload

# Response:
# {"job_id": "xxx", "status": "uploaded"}

# 2. Poll status (ganti JOB_ID)
curl http://localhost:5000/api/job/JOB_ID

# Expected stages:
# uploaded → preprocessing → reconstructing_3d → rendering_previews → mesh_repairing → exporting_stl → done

# 3. Get result
curl http://localhost:5000/api/result/JOB_ID

# Expected:
# {
#   "mesh_dimensions": {"x_mm": 45.2, "y_mm": 30.0, "z_mm": 12.5, ...},
#   "stl_download_url": "/download/JOB_ID/stl",
#   "obj_download_url": "/download/JOB_ID/obj"
# }
```

---

## 📝 Environment Variables

**Backend (.env):**
```bash
FLASK_ENV=development
REDIS_URL=redis://localhost:6352/0
CELERY_BROKER_URL=redis://localhost:6352/0
CELERY_RESULT_BACKEND=redis://localhost:6352/0
GPU_DEVICE=cuda  # atau "cpu" untuk CPU-only mode
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:5000/api
```

---

## 🎯 Summary

### **Docker Compose (Recommended untuk production/testing)**
```bash
cd backend
docker-compose up -d
```

### **Local Development (Recommended untuk development)**
```bash
# Terminal 1
redis-server --port 6352

# Terminal 2
cd backend && source venv/bin/activate
flask run --host=0.0.0.0 --port=5000

# Terminal 3
cd backend && source venv/bin/activate
celery -A app.tasks worker -Q gpu --concurrency=1 --loglevel=info

# Terminal 4
cd backend && source venv/bin/activate
celery -A app.tasks worker -Q cpu --concurrency=4 --loglevel=info

# Terminal 5 (opsional)
cd frontend && npm run dev
```

---

**Version**: 1.0 (Phase 1 Complete)  
**Last Updated**: 2026-01-30  
**Status**: ✅ Ready for Testing
