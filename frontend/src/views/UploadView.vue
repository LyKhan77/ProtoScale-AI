<script setup>
import { ref, onMounted } from 'vue';
import { useProcessStore } from '../stores/process';
import { useHistoryStore } from '../stores/history';
import CyberCheckbox from '../components/CyberCheckbox.vue';

const store = useProcessStore();
const historyStore = useHistoryStore();

onMounted(() => {
  historyStore.loadHistory();
});
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
    store.uploadImage(file, {
      removeBackground: removeBackground.value,
      enhancedDetail: enhancedDetail.value,
    });
  } else {
    alert('Please upload an image file (JPG/PNG).');
  }
}

function reupload() {
  store.reset();
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[50vh] animate-fade-in">
    <!-- Error Banner -->
    <div v-if="store.error" class="w-full max-w-2xl mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm">
      {{ store.error }}
    </div>

    <!-- State: No image uploaded yet -->
    <template v-if="!store.uploadedImage">
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
          <span class="font-mono text-sm animate-pulse text-brand-dark dark:text-white">UPLOADING...</span>
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
    </template>

    <!-- State: Image uploaded, show preview + Generate button -->
    <template v-else-if="store.uploadedImage && store.jobId">
      <div class="text-center mb-6">
        <h1 class="font-display text-3xl font-bold mb-2 text-brand-dark dark:text-white transition-colors duration-300">Image Ready</h1>
        <p class="text-gray-500 dark:text-gray-400 transition-colors duration-300">
          Review your image and click Generate to create a 3D model.
        </p>
      </div>

      <div class="w-full max-w-md aspect-square bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden mb-8">
        <img :src="store.uploadedImage" class="w-full h-full object-contain p-6" />
      </div>

      <div class="flex gap-4">
        <button
          @click="reupload"
          class="px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 font-medium transition-colors"
        >
          Re-upload
        </button>
        <button
          @click="store.goToGenerate"
          class="px-8 py-3 rounded-lg bg-brand-teal text-white font-bold hover:bg-teal-600 transition-colors shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 flex items-center gap-2"
        >
          <span>Generate 3D Model</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </template>

    <!-- Recent Models History -->
    <div v-if="!store.uploadedImage && historyStore.items.length > 0" class="w-full max-w-2xl mt-12">
      <h2 class="font-display text-xl font-bold mb-4 text-brand-dark dark:text-white transition-colors duration-300">Recent Models</h2>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div
          v-for="item in historyStore.items"
          :key="item.jobId"
          @click="store.loadFromHistory(item.jobId)"
          class="group cursor-pointer rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden hover:border-brand-teal dark:hover:border-brand-teal transition-all duration-200 hover:shadow-lg hover:shadow-teal-500/10"
        >
          <div class="aspect-square bg-gray-50 dark:bg-gray-900 overflow-hidden">
            <img
              :src="item.thumbnailUrl"
              :alt="item.name"
              class="w-full h-full object-contain p-3 group-hover:scale-105 transition-transform duration-200"
              loading="lazy"
            />
          </div>
          <div class="p-3">
            <p class="text-sm font-medium text-brand-dark dark:text-white truncate">{{ item.name }}</p>
            <p class="text-xs text-gray-400 font-mono mt-1">{{ new Date(item.createdAt).toLocaleDateString() }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
