<script setup>
import { onMounted } from 'vue';
import { useProcessStore } from '../stores/process';
import Loader3D from '../components/Loader3D.vue';

const store = useProcessStore();

onMounted(() => {
  if (!store.isProcessing) {
    store.generate3D();
  }
});
</script>

<template>
  <div class="flex flex-col h-full animate-fade-in">
    <div class="text-center mb-6">
      <h1 class="font-display text-2xl font-bold text-brand-dark dark:text-white transition-colors duration-300">Generating 3D Model</h1>
      <p class="text-gray-500 dark:text-gray-400 text-sm transition-colors duration-300">Reconstructing geometry from your image. This may take a moment.</p>
    </div>

    <!-- Loading State -->
    <div class="flex-1 flex flex-col items-center justify-center min-h-[400px]">
      <Loader3D class="mb-12" />

      <div class="w-64 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-4 transition-colors duration-300">
        <div
          class="h-full bg-brand-teal transition-all duration-300"
          :style="{ width: store.progress + '%' }"
        ></div>
      </div>
      <span class="font-mono text-xs text-brand-teal">
        {{ store.progress > 0 ? `RECONSTRUCTING GEOMETRY ${store.progress}%` : 'INITIALIZING...' }}
      </span>

      <!-- Error State -->
      <div v-if="store.error" class="mt-8 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm max-w-md text-center">
        <p class="font-medium mb-2">Generation Failed</p>
        <p>{{ store.error }}</p>
        <button
          @click="store.reset"
          class="mt-4 px-6 py-2 rounded-lg border border-red-300 dark:border-red-700 text-red-600 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/50 font-medium transition-colors text-sm"
        >
          Try Again
        </button>
      </div>
    </div>
  </div>
</template>
