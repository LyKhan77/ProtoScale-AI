import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// API base URL - configurable via environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Polling interval in milliseconds
const POLL_INTERVAL = 1000;

export const useProcessStore = defineStore('process', () => {
  // --- State ---
  const steps = ['Upload', 'Review', 'Preview', 'Export'];
  const currentStepIndex = ref(0);
  const isProcessing = ref(false);
  const progress = ref(0);
  const error = ref(null);
  const uploadedImage = ref(null);

  // Job tracking
  const jobId = ref(null);
  const jobStatus = ref(null);

  // Data Containers
  const multiAngleImages = ref([]);
  const modelUrl = ref(null);
  const analysisData = ref(null);
  const stlDownloadUrl = ref(null);
  const objDownloadUrl = ref(null);

  // --- Getters ---
  const currentStep = computed(() => steps[currentStepIndex.value]);

  // --- API Helper ---
  async function fetchApi(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
      },
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || `API error: ${response.status}`);
    }

    return response.json();
  }

  // --- Actions ---

  // 1. Upload Image
  async function uploadImage(file) {
    isProcessing.value = true;
    error.value = null;

    try {
      // Create form data
      const formData = new FormData();
      formData.append('image', file);

      // Upload to API
      const response = await fetchApi('/upload', {
        method: 'POST',
        body: formData,
      });

      jobId.value = response.job_id;
      jobStatus.value = response.status;

      // Store local preview
      uploadedImage.value = URL.createObjectURL(file);

      isProcessing.value = false;
      currentStepIndex.value = 1; // Move to Review

      // Start polling for multi-angle generation
      pollJobStatus();

    } catch (err) {
      error.value = err.message;
      isProcessing.value = false;
      throw err;
    }
  }

  // Poll job status
  async function pollJobStatus() {
    if (!jobId.value) return;

    try {
      const status = await fetchApi(`/job/${jobId.value}`);
      jobStatus.value = status.status;
      progress.value = status.progress || 0;

      // Check for error
      if (status.status === 'error') {
        error.value = status.error_message || 'Processing failed';
        isProcessing.value = false;
        return;
      }

      // Check if multi-angle generation is complete
      if (status.status === 'preprocessing' ||
          status.status === 'reconstructing_3d' ||
          status.status === 'mesh_repairing' ||
          status.status === 'exporting_stl' ||
          status.status === 'done') {
        // Fetch result to get images
        await fetchResult();
      }

      // Continue polling if not done
      if (status.status !== 'done' && status.status !== 'error') {
        setTimeout(pollJobStatus, POLL_INTERVAL);
      } else if (status.status === 'done') {
        isProcessing.value = false;
      }

    } catch (err) {
      console.error('Polling error:', err);
      // Retry on network errors
      setTimeout(pollJobStatus, POLL_INTERVAL * 2);
    }
  }

  // Fetch job result
  async function fetchResult() {
    if (!jobId.value) return;

    try {
      const result = await fetchApi(`/result/${jobId.value}`);

      // Update multi-angle images if available
      if (result.multi_angle_images && result.multi_angle_images.length > 0) {
        multiAngleImages.value = result.multi_angle_images.map(
          path => `${API_BASE_URL.replace('/api', '')}${path}`
        );
      }

      // Update download URLs if available
      if (result.stl_download_url) {
        stlDownloadUrl.value = `${API_BASE_URL.replace('/api', '')}${result.stl_download_url}`;
      }
      if (result.obj_download_url) {
        objDownloadUrl.value = `${API_BASE_URL.replace('/api', '')}${result.obj_download_url}`;
      }

      // Update analysis data if available
      if (result.analysis_data) {
        analysisData.value = result.analysis_data;
      }

      // Update model URL for preview if available
      if (result.preview_obj) {
        modelUrl.value = `${API_BASE_URL.replace('/api', '')}${result.preview_obj}`;
      }

    } catch (err) {
      console.error('Fetch result error:', err);
    }
  }

  // 2. Generate Multi-Angle (now handled by backend, this just triggers UI update)
  async function generateMultiAngle() {
    // Multi-angle generation starts automatically after upload
    // This function can be used to refresh/re-poll if needed
    isProcessing.value = true;
    progress.value = 0;

    if (jobId.value) {
      await pollJobStatus();
    }
  }

  // 3. Generate 3D Mesh (triggers move to preview once ready)
  async function generateMesh() {
    isProcessing.value = true;

    // The backend pipeline already generates the mesh
    // Poll until done
    if (jobId.value) {
      const checkStatus = async () => {
        const status = await fetchApi(`/job/${jobId.value}`);

        if (status.status === 'done') {
          await fetchResult();
          isProcessing.value = false;
          currentStepIndex.value = 2; // Move to Preview
        } else if (status.status === 'error') {
          error.value = status.error_message || 'Mesh generation failed';
          isProcessing.value = false;
        } else {
          progress.value = status.progress || 0;
          setTimeout(checkStatus, POLL_INTERVAL);
        }
      };

      await checkStatus();
    } else {
      // Fallback for development without backend
      await new Promise(resolve => setTimeout(resolve, 3000));

      modelUrl.value = 'placeholder-cube';
      analysisData.value = {
        watertight: true,
        dimensions: { x: 45.2, y: 30.0, z: 12.5 },
        volume: 1205.4
      };

      isProcessing.value = false;
      currentStepIndex.value = 2;
    }
  }

  // 4. Confirm & Export
  function confirmModel() {
    currentStepIndex.value = 3; // Move to Export
  }

  // Download STL
  async function downloadStl() {
    if (stlDownloadUrl.value) {
      window.open(stlDownloadUrl.value, '_blank');
    } else if (jobId.value) {
      window.open(`${API_BASE_URL}/download/${jobId.value}/stl`, '_blank');
    } else {
      alert('STL file not available yet');
    }
  }

  // Download OBJ
  async function downloadObj() {
    if (objDownloadUrl.value) {
      window.open(objDownloadUrl.value, '_blank');
    } else if (jobId.value) {
      window.open(`${API_BASE_URL}/download/${jobId.value}/obj`, '_blank');
    } else {
      alert('OBJ file not available yet');
    }
  }

  function reset() {
    currentStepIndex.value = 0;
    uploadedImage.value = null;
    multiAngleImages.value = [];
    modelUrl.value = null;
    analysisData.value = null;
    jobId.value = null;
    jobStatus.value = null;
    progress.value = 0;
    error.value = null;
    stlDownloadUrl.value = null;
    objDownloadUrl.value = null;
  }

  return {
    steps,
    currentStepIndex,
    currentStep,
    isProcessing,
    progress,
    error,
    uploadedImage,
    multiAngleImages,
    modelUrl,
    analysisData,
    jobId,
    jobStatus,
    stlDownloadUrl,
    objDownloadUrl,
    uploadImage,
    generateMultiAngle,
    generateMesh,
    confirmModel,
    downloadStl,
    downloadObj,
    reset
  };
});
