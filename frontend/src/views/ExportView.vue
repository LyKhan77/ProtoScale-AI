<script setup>
import { useProcessStore } from '../stores/process';

const store = useProcessStore();

function downloadFile(ext) {
  // Mock download
  alert(`Downloading ${ext} file...`);
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
    <div class="w-20 h-20 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-6 text-green-600 dark:text-green-300 transition-colors duration-300">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
    </div>

    <h1 class="font-display text-3xl font-bold mb-2 text-brand-dark dark:text-white transition-colors duration-300">Processing Complete</h1>
    <p class="text-gray-500 dark:text-gray-400 mb-8 text-center max-w-sm transition-colors duration-300">
      Your geometry is ready for manufacturing.
    </p>

    <div class="grid gap-4 w-full max-w-md">
      <button 
        @click="downloadFile('STL')"
        class="flex items-center justify-between w-full p-4 bg-brand-dark dark:bg-gray-700 text-white rounded-xl shadow-lg hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors group"
      >
        <div class="flex items-center gap-3">
          <div class="bg-white/10 p-2 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <div class="text-left">
            <div class="font-bold">Download .STL</div>
            <div class="text-xs text-gray-400">Binary format • ~12MB</div>
          </div>
        </div>
        <span class="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
      </button>

      <button 
        @click="downloadFile('OBJ')"
        class="flex items-center justify-between w-full p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-brand-dark dark:text-white rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="flex items-center gap-3">
          <div class="bg-gray-100 dark:bg-gray-900 p-2 rounded-lg transition-colors duration-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <div class="text-left">
            <div class="font-bold">Download .OBJ</div>
            <div class="text-xs text-gray-500 dark:text-gray-400">Source mesh • ~14MB</div>
          </div>
        </div>
      </button>
    </div>

    <button 
      @click="store.reset"
      class="mt-12 text-sm text-gray-400 dark:text-gray-500 hover:text-brand-teal dark:hover:text-brand-teal transition-colors"
    >
      Start New Project
    </button>
  </div>
</template>
