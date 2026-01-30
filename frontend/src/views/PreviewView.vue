<script setup>
import { ref, computed, watch } from 'vue';
import { useProcessStore } from '../stores/process';
import { useThemeStore } from '../stores/theme';
import { TresCanvas } from '@tresjs/core';
import { OrbitControls, Grid } from '@tresjs/cientos';

const store = useProcessStore();
const theme = useThemeStore();

// Scale state
const uniformScale = ref(1);
const scaleX = ref(1);
const scaleY = ref(1);
const scaleZ = ref(1);
const lockUniform = ref(true);

const canvasColor = computed(() => theme.isDark ? '#111827' : '#F3F4F6');
const gridColor = computed(() => theme.isDark ? '#374151' : '#CCCCCC');
const gridSectionColor = computed(() => theme.isDark ? '#6B7280' : '#888888');

// Base dimensions from API (or defaults)
const baseDims = computed(() => {
  const d = store.modelDimensions;
  return {
    x: d?.x_mm || 45.20,
    y: d?.y_mm || 30.00,
    z: d?.z_mm || 12.50,
  };
});

// Scaled dimensions
const dimX = computed(() => +(baseDims.value.x * scaleX.value).toFixed(2));
const dimY = computed(() => +(baseDims.value.y * scaleY.value).toFixed(2));
const dimZ = computed(() => +(baseDims.value.z * scaleZ.value).toFixed(2));

const volume = computed(() => {
  const baseVol = store.modelDimensions?.volume_mm3 || 0;
  return +(baseVol * scaleX.value * scaleY.value * scaleZ.value).toFixed(1);
});

const isWatertight = computed(() => store.modelDimensions?.watertight ?? store.analysisData?.watertight ?? true);
const isManifold = computed(() => store.modelDimensions?.manifold ?? store.analysisData?.manifold ?? true);

// Uniform scale syncs all axes
watch(uniformScale, (val) => {
  if (lockUniform.value) {
    scaleX.value = val;
    scaleY.value = val;
    scaleZ.value = val;
  }
});

// When individual axis changes while locked, update uniform
function onAxisChange() {
  if (lockUniform.value) {
    uniformScale.value = scaleX.value;
    scaleY.value = scaleX.value;
    scaleZ.value = scaleX.value;
  }
}

// Direct dimension input
function setDimX(val) {
  const v = parseFloat(val);
  if (!isNaN(v) && v > 0) {
    scaleX.value = +(v / baseDims.value.x).toFixed(4);
    if (lockUniform.value) { uniformScale.value = scaleX.value; scaleY.value = scaleX.value; scaleZ.value = scaleX.value; }
  }
}
function setDimY(val) {
  const v = parseFloat(val);
  if (!isNaN(v) && v > 0) {
    scaleY.value = +(v / baseDims.value.y).toFixed(4);
    if (lockUniform.value) { uniformScale.value = scaleY.value; scaleX.value = scaleY.value; scaleZ.value = scaleY.value; }
  }
}
function setDimZ(val) {
  const v = parseFloat(val);
  if (!isNaN(v) && v > 0) {
    scaleZ.value = +(v / baseDims.value.z).toFixed(4);
    if (lockUniform.value) { uniformScale.value = scaleZ.value; scaleX.value = scaleZ.value; scaleY.value = scaleZ.value; }
  }
}
</script>

<template>
  <div class="h-[calc(100vh-160px)] w-full relative transition-colors duration-300">
    <!-- Error Overlay -->
    <div v-if="store.error" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-white/95 dark:bg-gray-900/95 transition-colors duration-300">
      <div class="max-w-md w-full bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg p-6 mx-4">
        <div class="flex items-start gap-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="font-semibold text-red-900 dark:text-red-200 mb-1">Reconstruction Failed</h3>
            <p class="text-sm text-red-700 dark:text-red-300 mb-4">{{ store.error }}</p>
            <button
              @click="store.reset"
              class="px-4 py-2 bg-red-600 dark:bg-red-700 text-white rounded-lg hover:bg-red-700 dark:hover:bg-red-600 transition-colors text-sm font-medium"
            >
              Start Over
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-else-if="store.isProcessing" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-white/90 dark:bg-gray-900/90 transition-colors duration-300">
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

      <!-- Placeholder Mesh (scaled per axis) -->
      <TresMesh :scale="[scaleX, scaleY, scaleZ]">
        <TresTorusKnotGeometry :args="[0.8, 0.3, 100, 16]" />
        <TresMeshStandardMaterial color="#564D4D" :roughness="0.3" :metalness="0.5" />
      </TresMesh>

      <Grid :args="[10, 10]" :cell-color="gridColor" :section-color="gridSectionColor" fade-distance="20" />
    </TresCanvas>

    <!-- HUD Controls - Model Properties Panel -->
    <div v-if="!store.isProcessing && !store.error" class="absolute top-4 right-4 bg-white/90 dark:bg-gray-800/90 backdrop-blur border border-gray-200 dark:border-gray-700 p-4 rounded-xl shadow-sm w-72 transition-colors duration-300 max-h-[calc(100vh-220px)] overflow-y-auto">
      <h3 class="font-mono text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Model Properties</h3>

      <!-- Scale Section -->
      <div class="mb-4 text-brand-dark dark:text-gray-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold uppercase tracking-wider text-gray-400">Scale</span>
          <button
            @click="lockUniform = !lockUniform"
            class="text-xs px-2 py-0.5 rounded border transition-colors"
            :class="lockUniform
              ? 'border-brand-teal text-brand-teal bg-brand-teal/10'
              : 'border-gray-300 dark:border-gray-600 text-gray-400'"
          >
            {{ lockUniform ? 'Uniform' : 'Free' }}
          </button>
        </div>

        <!-- Uniform slider -->
        <div class="mb-3">
          <label class="flex justify-between text-sm font-medium mb-1">
            <span>Uniform</span>
            <span class="font-mono text-xs">{{ uniformScale.toFixed(2) }}x</span>
          </label>
          <input
            type="range"
            min="0.1"
            max="5.0"
            step="0.01"
            v-model.number="uniformScale"
            class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-brand-teal"
          />
        </div>

        <!-- Per-axis sliders -->
        <div class="space-y-2">
          <div>
            <label class="flex justify-between text-sm mb-1">
              <span class="text-red-500 font-bold">X</span>
              <span class="font-mono text-xs">{{ scaleX.toFixed(2) }}x</span>
            </label>
            <input
              type="range" min="0.1" max="5.0" step="0.01"
              v-model.number="scaleX"
              @input="onAxisChange"
              :disabled="lockUniform"
              class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-red-500 disabled:opacity-40"
            />
          </div>
          <div>
            <label class="flex justify-between text-sm mb-1">
              <span class="text-green-500 font-bold">Y</span>
              <span class="font-mono text-xs">{{ scaleY.toFixed(2) }}x</span>
            </label>
            <input
              type="range" min="0.1" max="5.0" step="0.01"
              v-model.number="scaleY"
              :disabled="lockUniform"
              class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-green-500 disabled:opacity-40"
            />
          </div>
          <div>
            <label class="flex justify-between text-sm mb-1">
              <span class="text-blue-500 font-bold">Z</span>
              <span class="font-mono text-xs">{{ scaleZ.toFixed(2) }}x</span>
            </label>
            <input
              type="range" min="0.1" max="5.0" step="0.01"
              v-model.number="scaleZ"
              :disabled="lockUniform"
              class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500 disabled:opacity-40"
            />
          </div>
        </div>
      </div>

      <!-- Dimensions Section -->
      <div class="border-t border-gray-100 dark:border-gray-700 pt-3 mb-4 text-brand-dark dark:text-gray-200">
        <span class="text-xs font-bold uppercase tracking-wider text-gray-400 block mb-2">Dimensions (mm)</span>
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-red-500 font-bold text-sm w-4">X</span>
            <input
              type="number"
              :value="dimX"
              @change="setDimX($event.target.value)"
              step="0.1"
              min="0.1"
              class="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded px-2 py-1 text-sm font-mono text-right w-20"
            />
            <span class="text-xs text-gray-400">mm</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-green-500 font-bold text-sm w-4">Y</span>
            <input
              type="number"
              :value="dimY"
              @change="setDimY($event.target.value)"
              step="0.1"
              min="0.1"
              class="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded px-2 py-1 text-sm font-mono text-right w-20"
            />
            <span class="text-xs text-gray-400">mm</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-blue-500 font-bold text-sm w-4">Z</span>
            <input
              type="number"
              :value="dimZ"
              @change="setDimZ($event.target.value)"
              step="0.1"
              min="0.1"
              class="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded px-2 py-1 text-sm font-mono text-right w-20"
            />
            <span class="text-xs text-gray-400">mm</span>
          </div>
        </div>
      </div>

      <!-- Properties Section -->
      <div class="border-t border-gray-100 dark:border-gray-700 pt-3 text-brand-dark dark:text-gray-200">
        <span class="text-xs font-bold uppercase tracking-wider text-gray-400 block mb-2">Properties</span>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-sm">Watertight</span>
            <span
              class="text-xs px-2 py-0.5 rounded font-bold"
              :class="isWatertight
                ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'"
            >
              {{ isWatertight ? 'YES' : 'NO' }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm">Manifold</span>
            <span
              class="text-xs px-2 py-0.5 rounded font-bold"
              :class="isManifold
                ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'"
            >
              {{ isManifold ? 'PASS' : 'FAIL' }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm">Volume</span>
            <span class="text-xs font-mono text-gray-500 dark:text-gray-400">{{ volume }} mm&sup3;</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Action Bar -->
    <div v-if="!store.isProcessing && !store.error" class="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-4">
      <button
        @click="store.confirmModel"
        class="bg-brand-teal text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 hover:scale-105 transition-all"
      >
        Export Scaled STL
      </button>
    </div>
  </div>
</template>
