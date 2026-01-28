<script setup>
import { ref, computed } from 'vue';
import { useProcessStore } from '../stores/process';
import { useThemeStore } from '../stores/theme';
import { TresCanvas } from '@tresjs/core';
import { OrbitControls, Grid } from '@tresjs/cientos';

const store = useProcessStore();
const theme = useThemeStore();
const scale = ref(1);

const canvasColor = computed(() => theme.isDark ? '#111827' : '#F3F4F6'); // Gray-900 vs Gray-100
const gridColor = computed(() => theme.isDark ? '#374151' : '#CCCCCC');
const gridSectionColor = computed(() => theme.isDark ? '#6B7280' : '#888888');

function updateScale(e) {
  scale.value = parseFloat(e.target.value);
}
</script>

<template>
  <div class="h-[calc(100vh-160px)] w-full relative transition-colors duration-300">
    <!-- Loading Overlay -->
    <div v-if="store.isProcessing" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-white/90 dark:bg-gray-900/90 transition-colors duration-300">
      <div class="w-12 h-12 border-4 border-brand-teal border-t-transparent rounded-full animate-spin mb-6"></div>
      <div class="text-center">
        <h2 class="font-display text-xl font-bold mb-1 text-brand-dark dark:text-white transition-colors duration-300">Reconstructing Geometry</h2>
        <p class="font-mono text-sm text-gray-500 dark:text-gray-400">VOXELIZATION IN PROGRESS...</p>
      </div>
    </div>

    <!-- 3D Viewport -->
    <TresCanvas v-else window-size :clear-color="canvasColor">
      <TresPerspectiveCamera :position="[3, 3, 3]" :look-at="[0, 0, 0]" />
      <OrbitControls />
      
      <TresAmbientLight :intensity="1" />
      <TresDirectionalLight :position="[2, 5, 2]" :intensity="2" />
      
      <!-- Placeholder Mesh (Mocking the generated model) -->
      <TresMesh :scale="[scale, scale, scale]">
        <TresTorusKnotGeometry :args="[0.8, 0.3, 100, 16]" />
        <TresMeshStandardMaterial color="#564D4D" :roughness="0.3" :metalness="0.5" />
      </TresMesh>
      
      <Grid :args="[10, 10]" :cell-color="gridColor" :section-color="gridSectionColor" fade-distance="20" />
    </TresCanvas>

    <!-- HUD Controls -->
    <div v-if="!store.isProcessing" class="absolute top-4 right-4 bg-white/90 dark:bg-gray-800/90 backdrop-blur border border-gray-200 dark:border-gray-700 p-4 rounded-xl shadow-sm w-64 transition-colors duration-300">
      <h3 class="font-mono text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Model Properties</h3>
      
      <div class="mb-4 text-brand-dark dark:text-gray-200">
        <label class="flex justify-between text-sm font-medium mb-1">
          <span>Scale</span>
          <span class="font-mono text-xs">{{ scale.toFixed(2) }}x</span>
        </label>
        <input 
          type="range" 
          min="0.5" 
          max="2.0" 
          step="0.01" 
          v-model="scale"
          class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-brand-teal"
        />
      </div>

      <div class="border-t border-gray-100 dark:border-gray-700 pt-3 text-brand-dark dark:text-gray-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm">Watertight</span>
          <span class="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-0.5 rounded font-bold">YES</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm">Manifold</span>
          <span class="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-0.5 rounded font-bold">PASS</span>
        </div>
      </div>
    </div>

    <!-- Bottom Action Bar -->
    <div v-if="!store.isProcessing" class="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-4">
      <button 
        @click="store.confirmModel"
        class="bg-brand-teal text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 hover:scale-105 transition-all"
      >
        Export STL
      </button>
    </div>
  </div>
</template>
