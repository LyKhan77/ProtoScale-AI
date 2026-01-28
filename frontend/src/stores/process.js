import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useProcessStore = defineStore('process', () => {
  // --- State ---
  const steps = ['Upload', 'Review', 'Preview', 'Export'];
  const currentStepIndex = ref(0);
  const isProcessing = ref(false);
  const progress = ref(0);
  const error = ref(null);
  const uploadedImage = ref(null);
  
  // Mock Data Containers
  const multiAngleImages = ref([]);
  const modelUrl = ref(null);
  const analysisData = ref(null);

  // --- Getters ---
  const currentStep = computed(() => steps[currentStepIndex.value]);

  // --- Actions ---
  
  // 1. Upload
  async function uploadImage(file) {
    isProcessing.value = true;
    error.value = null;
    
    // Simulate upload delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    uploadedImage.value = URL.createObjectURL(file);
    isProcessing.value = false;
    currentStepIndex.value = 1; // Move to Review
  }

  // 2. Generate Multi-Angle
  async function generateMultiAngle() {
    isProcessing.value = true;
    progress.value = 0;

    const interval = setInterval(() => {
      progress.value += 10;
      if (progress.value >= 100) clearInterval(interval);
    }, 300);

    await new Promise(resolve => setTimeout(resolve, 3500));

    // Mock 4 angles
    multiAngleImages.value = [
      uploadedImage.value, // Front (reuse original)
      uploadedImage.value, // Right (placeholder)
      uploadedImage.value, // Back (placeholder)
      uploadedImage.value  // Left (placeholder)
    ];

    isProcessing.value = false;
    progress.value = 0;
  }

  // 3. Generate 3D Mesh
  async function generateMesh() {
    isProcessing.value = true;
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // We will use a standard primitive or a public GLB if available, 
    // but for now we set a flag that the viewer component can read to load its placeholder.
    modelUrl.value = 'placeholder-cube'; 
    
    analysisData.value = {
      watertight: true,
      dimensions: { x: 45.2, y: 30.0, z: 12.5 },
      volume: 1205.4
    };

    isProcessing.value = false;
    currentStepIndex.value = 2; // Move to Preview
  }

  // 4. Confirm & Export
  function confirmModel() {
    currentStepIndex.value = 3; // Move to Export
  }

  function reset() {
    currentStepIndex.value = 0;
    uploadedImage.value = null;
    multiAngleImages.value = [];
    modelUrl.value = null;
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
    uploadImage,
    generateMultiAngle,
    generateMesh,
    confirmModel,
    reset
  };
});
