<script setup>
import { ref } from 'vue';
import { useProcessStore } from '../stores/process';
import CyberCheckbox from '../components/CyberCheckbox.vue';

const store = useProcessStore();
const isDragging = ref(false);
const fileInput = ref(null);
const removeBackground = ref(true);
const enhancedDetail = ref(false);

function handleDrop(e) {
  isDragging.value = false;
  const files = e.dataTransfer.files;
  if (files.length > 0) processFile(files[0]);
}

function handleFileSelect(e) {
  const files = e.target.files;
  if (files.length > 0) processFile(files[0]);
}

function processFile(file) {
  if (file.type.startsWith('image/')) {
    store.uploadImage(file);
  } else {
    alert('Please upload an image file (JPG/PNG).');
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[50vh] animate-fade-in">
    <div class="text-center mb-8">
      <h1 class="font-display text-4xl font-bold mb-2 text-brand-dark dark:text-white transition-colors duration-300">Upload Source Image</h1>
      <p class="text-gray-500 dark:text-gray-400 max-w-md mx-auto transition-colors duration-300">
        Select a high-resolution image of the object you wish to convert into 3D geometry.
      </p>
    </div>

    <div
      class="w-full max-w-2xl aspect-[16/9] border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group relative overflow-hidden bg-brand-gray/30 dark:bg-gray-800/50"
      :class="isDragging ? 'border-brand-teal bg-brand-teal/5 dark:bg-brand-teal/10' : 'border-gray-300 dark:border-gray-700 hover:border-brand-dark dark:hover:border-gray-500'"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="fileInput.click()"
    >
      <input 
        type="file" 
        ref="fileInput" 
        class="hidden" 
        accept="image/png, image/jpeg" 
        @change="handleFileSelect"
      />
      
      <div v-if="store.isProcessing" class="absolute inset-0 bg-white/80 dark:bg-gray-900/80 z-10 flex flex-col items-center justify-center backdrop-blur-sm transition-colors duration-300">
        <div class="w-8 h-8 border-4 border-brand-teal border-t-transparent rounded-full animate-spin mb-4"></div>
        <span class="font-mono text-sm animate-pulse text-brand-dark dark:text-white">ANALYZING INPUT...</span>
      </div>

      <div class="flex flex-col items-center gap-4 group-hover:scale-105 transition-transform duration-300">
        <div class="w-16 h-16 rounded-full bg-white dark:bg-gray-700 flex items-center justify-center shadow-sm transition-colors duration-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-brand-dark dark:text-white transition-colors duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </div>
        <div class="text-center">
          <p class="font-medium text-lg text-brand-dark dark:text-white transition-colors duration-300">Click to upload or drag & drop</p>
          <p class="text-sm text-gray-400 mt-1 font-mono">JPG or PNG (Max 10MB)</p>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="store.error" class="mt-6 max-w-2xl w-full bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg p-4 transition-colors duration-300">
      <div class="flex items-start gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <h3 class="font-semibold text-red-900 dark:text-red-200 text-sm mb-1">Upload Failed</h3>
          <p class="text-sm text-red-700 dark:text-red-300">{{ store.error }}</p>
        </div>
        <button
          @click="store.error = null"
          class="text-red-400 hover:text-red-600 dark:hover:text-red-300 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Settings Toggles -->
    <div class="mt-8 flex gap-8">
      <CyberCheckbox 
        v-model="removeBackground" 
        label="Remove Background" 
      />
      <CyberCheckbox 
        v-model="enhancedDetail" 
        label="Enhanced Detail (Slow)" 
      />
    </div>
  </div>
</template>
