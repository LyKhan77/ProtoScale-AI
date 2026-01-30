import { defineStore } from 'pinia';
import { ref, computed, shallowRef } from 'vue';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8077';

export const useProcessStore = defineStore('process', () => {
  // --- State ---
  const steps = ['Upload', 'Generate', 'Preview', 'Export'];
  const currentStepIndex = ref(0);
  const isProcessing = ref(false);
  const progress = ref(0);
  const error = ref(null);
  const uploadedImage = ref(null);

  const jobId = ref(null);
  const modelUrl = ref(null);
  const modelScene = shallowRef(null);
  const analysisData = ref(null);
  const userScale = ref({ x: 1, y: 1, z: 1 });

  // --- Getters ---
  const currentStep = computed(() => steps[currentStepIndex.value]);

  // --- Helpers ---
  async function pollUntilDone(id, timeoutMs = 600000) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const res = await fetch(`${API_BASE}/api/jobs/${id}/status`);
      if (!res.ok) throw new Error(`Status check failed: ${res.status}`);
      const data = await res.json();

      progress.value = data.progress || 0;

      if (data.status === 'completed') return data;
      if (data.status === 'failed') throw new Error(data.error || 'Job failed');

      await new Promise(r => setTimeout(r, 1000));
    }
    throw new Error('Job timed out (10 minutes)');
  }

  // --- Actions ---

  // 1. Upload only — show preview, wait for user to click Generate
  async function uploadImage(file, options = {}) {
    isProcessing.value = true;
    error.value = null;

    try {
      uploadedImage.value = URL.createObjectURL(file);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('remove_bg', options.removeBackground ?? true);
      formData.append('enhanced_detail', options.enhancedDetail ?? false);

      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      const data = await res.json();
      jobId.value = data.job_id;

      isProcessing.value = false;
    } catch (e) {
      error.value = e.message;
      isProcessing.value = false;
    }
  }

  // 2. Navigate to progress view and trigger 3D generation
  async function generate3D() {
    if (!jobId.value) return;
    isProcessing.value = true;
    progress.value = 0;
    error.value = null;

    try {
      await fetch(`${API_BASE}/api/jobs/${jobId.value}/generate-3d`, {
        method: 'POST',
      });

      await pollUntilDone(jobId.value);

      modelUrl.value = `${API_BASE}/api/jobs/${jobId.value}/result/model.glb`;

      analysisData.value = {
        watertight: true,
        dimensions: { x: 0, y: 0, z: 0 },
        volume: 0,
      };

      isProcessing.value = false;
      progress.value = 0;
      currentStepIndex.value = 2; // Go to Preview
    } catch (e) {
      error.value = e.message;
      isProcessing.value = false;
      progress.value = 0;
    }
  }

  // Navigate to Generate step (ProgressView)
  function goToGenerate() {
    currentStepIndex.value = 1;
  }

  // 3. Confirm & Export
  function confirmModel() {
    currentStepIndex.value = 3;
  }

  function reset() {
    currentStepIndex.value = 0;
    jobId.value = null;
    uploadedImage.value = null;
    modelUrl.value = null;
    modelScene.value = null;
    analysisData.value = null;
    userScale.value = { x: 1, y: 1, z: 1 };
    error.value = null;
    progress.value = 0;
  }

  return {
    steps,
    currentStepIndex,
    currentStep,
    isProcessing,
    progress,
    error,
    uploadedImage,
    jobId,
    modelUrl,
    modelScene,
    analysisData,
    userScale,
    uploadImage,
    generate3D,
    goToGenerate,
    confirmModel,
    reset,
  };
});
