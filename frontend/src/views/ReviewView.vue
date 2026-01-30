<script setup>
import { onMounted } from 'vue';
import { useProcessStore } from '../stores/process';
import Loader3D from '../components/Loader3D.vue';

const store = useProcessStore();

onMounted(() => {
  if (store.multiAngleImages.length === 0) {
    store.generateMultiAngle();
  }
});
</script>

<template>
  <div class="flex flex-col h-full animate-fade-in">
    <div class="text-center mb-6">
      <h1 class="font-display text-2xl font-bold text-brand-dark dark:text-white transition-colors duration-300">Multi-Angle Analysis</h1>
      <p class="text-gray-500 dark:text-gray-400 text-sm transition-colors duration-300">Review the generated perspectives before reconstruction.</p>
    </div>

    <!-- Error State -->
    <div v-if="store.error" class="flex-1 flex flex-col items-center justify-center min-h-[400px]">
      <div class="max-w-md w-full bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg p-6 transition-colors duration-300">
        <div class="flex items-start gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="font-semibold text-red-900 dark:text-red-200 mb-1">Processing Failed</h3>
            <p class="text-sm text-red-700 dark:text-red-300 mb-4">{{ store.error }}</p>
            <button
              @click="store.reset"
              class="px-4 py-2 bg-red-600 dark:bg-red-700 text-white rounded-lg hover:bg-red-700 dark:hover:bg-red-600 transition-colors text-sm font-medium"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="store.isProcessing" class="flex-1 flex flex-col items-center justify-center min-h-[400px]">
      <Loader3D class="mb-12" />

      <div class="w-64 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-4 transition-colors duration-300">
        <div
          class="h-full bg-brand-teal transition-all duration-300"
          :style="{ width: store.progress + '%' }"
        ></div>
      </div>
      <div class="text-center">
        <span class="font-mono text-xs text-brand-teal block mb-1">{{ store.statusMessage.toUpperCase() }}</span>
        <span class="font-mono text-xs text-gray-400">{{ store.progress }}%</span>
      </div>
    </div>

    <!-- Grid View -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto w-full mb-12">
      <div 
        v-for="(img, idx) in store.multiAngleImages" 
        :key="idx" 
        class="aspect-square bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden relative group transition-colors duration-300"
      >
        <img :src="img" class="w-full h-full object-contain p-4 mix-blend-multiply dark:mix-blend-normal" />
        <div class="absolute top-2 left-2 bg-brand-dark dark:bg-gray-700 text-white text-[10px] font-mono px-2 py-0.5 rounded transition-colors duration-300">
          VIEW {{ idx + 1 }}
        </div>
      </div>
    </div>

    <!-- Action Bar -->
    <div v-if="!store.isProcessing" class="w-full border-t border-gray-200 dark:border-gray-800 pt-6 mt-auto flex justify-center transition-colors duration-300">
      <div class="max-w-5xl w-full flex justify-end gap-4">
        <button 
          @click="store.reset"
          class="px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 font-medium transition-colors"
        >
          Back
        </button>
        <button 
          @click="store.generateMesh"
          class="px-8 py-3 rounded-lg bg-brand-dark dark:bg-gray-700 text-white font-medium hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors shadow-lg shadow-gray-200 dark:shadow-none flex items-center gap-2"
        >
          <span>Generate 3D Geometry</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
