import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// API base URL - configurable via environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Polling interval in milliseconds
const POLL_INTERVAL = 1000;

export const useProcessStore = defineStore('process', () => {
  // --- State ---
  const steps = ['Upload', 'Preview', 'Export'];
  const currentStepIndex = ref(0);
  const isProcessing = ref(false);
  const progress = ref(0);
  const error = ref(null);
  const uploadedImage = ref(null);

  // Job tracking
  const jobId = ref(null);
  const jobStatus = ref(null);

  // Data Containers
  const modelUrl = ref(null);
  const analysisData = ref(null);
  const modelDimensions = ref(null);
  const stlDownloadUrl = ref(null);
  const objDownloadUrl = ref(null);

  // --- Getters ---
  const currentStep = computed(() => steps[currentStepIndex.value]);

  const statusMessage = computed(() => {
    const statusMap = {
      'uploaded': 'Initializing...',
      'preprocessing': 'Removing background',
      'reconstructing_3d': 'Reconstructing 3D geometry',
      'mesh_repairing': 'Repairing mesh',
      'exporting_stl': 'Exporting files',
      'done': 'Complete',
      'error': 'Failed'
    };
    return statusMap[jobStatus.value] || 'Processing...';
  });

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

      // Stay on Upload view but show processing state
      // Will navigate to Preview when done
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

      // Fetch result to get latest data
      if (status.status !== 'uploaded') {
        await fetchResult();
      }

      // Navigate to Preview when done
      if (status.status === 'done') {
        isProcessing.value = false;
        currentStepIndex.value = 1; // Preview
      }

      // Continue polling if not done
      if (status.status !== 'done' && status.status !== 'error') {
        setTimeout(pollJobStatus, POLL_INTERVAL);
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

      // Update mesh dimensions if available
      if (result.mesh_dimensions) {
        modelDimensions.value = result.mesh_dimensions;
      }

      // Update model URL for preview if available
      if (result.preview_obj) {
        modelUrl.value = `${API_BASE_URL.replace('/api', '')}${result.preview_obj}`;
      }

    } catch (err) {
      console.error('Fetch result error:', err);
    }
  }

  // Confirm & Export
  function confirmModel() {
    currentStepIndex.value = 2; // Move to Export
  }

  // Download STL
  async function downloadStl() {
    if (stlDownloadUrl.value) {
      window.open(stlDownloadUrl.value, '_blank');
    } else if (jobId.value) {
      window.open(`${API_BASE_URL}/download/${jobId.value}/stl`, '_blank');
    }
  }

  // Download OBJ
  async function downloadObj() {
    if (objDownloadUrl.value) {
      window.open(objDownloadUrl.value, '_blank');
    } else if (jobId.value) {
      window.open(`${API_BASE_URL}/download/${jobId.value}/obj`, '_blank');
    }
  }

  // Export scaled STL
  async function exportScaledStl(scale) {
    if (!jobId.value) {
      throw new Error('No job ID available');
    }

    try {
      const response = await fetchApi(`/dimension/update/${jobId.value}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scale })
      });

      // Open download URL in new tab
      const downloadUrl = `${API_BASE_URL.replace('/api', '')}${response.download_url}`;
      window.open(downloadUrl, '_blank');

      return response;
    } catch (err) {
      console.error('Export scaled STL failed:', err);
      throw err;
    }
  }

  // Validate dimensions
  async function validateDimensions(dimensions) {
    if (!jobId.value) {
      throw new Error('No job ID available');
    }

    try {
      const response = await fetchApi(`/dimension/validate/${jobId.value}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dimensions })
      });

      return response;
    } catch (err) {
      console.error('Validate dimensions failed:', err);
      throw err;
    }
  }

  function reset() {
    currentStepIndex.value = 0;
    uploadedImage.value = null;
    modelUrl.value = null;
    analysisData.value = null;
    modelDimensions.value = null;
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
    statusMessage,
    isProcessing,
    progress,
    error,
    uploadedImage,
    modelUrl,
    analysisData,
    modelDimensions,
    jobId,
    jobStatus,
    stlDownloadUrl,
    objDownloadUrl,
    uploadImage,
    confirmModel,
    downloadStl,
    downloadObj,
    exportScaledStl,
    validateDimensions,
    reset
  };
});
