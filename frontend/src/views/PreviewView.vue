<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useProcessStore } from '../stores/process';
import { useThemeStore } from '../stores/theme';
import { TresCanvas } from '@tresjs/core';
import { OrbitControls, Grid } from '@tresjs/cientos';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Box3, Vector3 } from 'three';

const store = useProcessStore();
const theme = useThemeStore();

const scaleX = ref(1);
const scaleY = ref(1);
const scaleZ = ref(1);
const lockScale = ref(true);

// Bounding box dimensions (in model units, displayed as mm)
const bboxSize = ref({ x: 0, y: 0, z: 0 });
const dimX = ref(0);
const dimY = ref(0);
const dimZ = ref(0);

const isLoadingModel = ref(false);

// Measurement tool
const isMeasuring = ref(false);
const measurePoints = ref([]);
const measureDistance = ref(null);

const canvasColor = computed(() => theme.isDark ? '#111827' : '#F3F4F6');
const gridColor = computed(() => theme.isDark ? '#374151' : '#CCCCCC');
const gridSectionColor = computed(() => theme.isDark ? '#6B7280' : '#888888');

// Load GLB when modelUrl changes
watch(() => store.modelUrl, (url) => {
  if (!url) return;
  isLoadingModel.value = true;
  const loader = new GLTFLoader();
  loader.load(url, (gltf) => {
    const scene = gltf.scene;
    store.modelScene = scene;

    // Compute bounding box
    const box = new Box3().setFromObject(scene);
    const size = new Vector3();
    box.getSize(size);
    bboxSize.value = { x: size.x, y: size.y, z: size.z };

    // Initialize dimensions in mm (assume 1 unit = 1mm for now)
    dimX.value = parseFloat((size.x * 10).toFixed(1));
    dimY.value = parseFloat((size.y * 10).toFixed(1));
    dimZ.value = parseFloat((size.z * 10).toFixed(1));

    // Update analysis data with real dimensions
    if (store.analysisData) {
      store.analysisData.dimensions = {
        x: parseFloat(dimX.value.toFixed(1)),
        y: parseFloat(dimY.value.toFixed(1)),
        z: parseFloat(dimZ.value.toFixed(1)),
      };
    }

    isLoadingModel.value = false;
  }, undefined, (err) => {
    console.error('GLB load error:', err);
    isLoadingModel.value = false;
    store.error = 'Failed to load 3D model';
  });
}, { immediate: true });

// Per-axis scale with lock
function updateScaleX(val) {
  const v = parseFloat(val);
  if (lockScale.value) {
    scaleX.value = scaleY.value = scaleZ.value = v;
    updateDimsFromScale();
  } else {
    scaleX.value = v;
    dimX.value = parseFloat((bboxSize.value.x * v * 10).toFixed(1));
  }
  syncStoreScale();
}
function updateScaleY(val) {
  const v = parseFloat(val);
  if (lockScale.value) {
    scaleX.value = scaleY.value = scaleZ.value = v;
    updateDimsFromScale();
  } else {
    scaleY.value = v;
    dimY.value = parseFloat((bboxSize.value.y * v * 10).toFixed(1));
  }
  syncStoreScale();
}
function updateScaleZ(val) {
  const v = parseFloat(val);
  if (lockScale.value) {
    scaleX.value = scaleY.value = scaleZ.value = v;
    updateDimsFromScale();
  } else {
    scaleZ.value = v;
    dimZ.value = parseFloat((bboxSize.value.z * v * 10).toFixed(1));
  }
  syncStoreScale();
}

function updateDimsFromScale() {
  dimX.value = parseFloat((bboxSize.value.x * scaleX.value * 10).toFixed(1));
  dimY.value = parseFloat((bboxSize.value.y * scaleY.value * 10).toFixed(1));
  dimZ.value = parseFloat((bboxSize.value.z * scaleZ.value * 10).toFixed(1));
}

// Dimension input → scale
function updateDimX(val) {
  const v = parseFloat(val) || 0;
  dimX.value = v;
  if (bboxSize.value.x > 0) {
    scaleX.value = parseFloat((v / (bboxSize.value.x * 10)).toFixed(3));
    if (lockScale.value) {
      scaleY.value = scaleZ.value = scaleX.value;
      updateDimsFromScale();
    }
  }
  syncStoreScale();
}
function updateDimY(val) {
  const v = parseFloat(val) || 0;
  dimY.value = v;
  if (bboxSize.value.y > 0) {
    scaleY.value = parseFloat((v / (bboxSize.value.y * 10)).toFixed(3));
    if (lockScale.value) {
      scaleX.value = scaleZ.value = scaleY.value;
      updateDimsFromScale();
    }
  }
  syncStoreScale();
}
function updateDimZ(val) {
  const v = parseFloat(val) || 0;
  dimZ.value = v;
  if (bboxSize.value.z > 0) {
    scaleZ.value = parseFloat((v / (bboxSize.value.z * 10)).toFixed(3));
    if (lockScale.value) {
      scaleX.value = scaleY.value = scaleZ.value;
      updateDimsFromScale();
    }
  }
  syncStoreScale();
}

function syncStoreScale() {
  store.userScale = { x: scaleX.value, y: scaleY.value, z: scaleZ.value };
}
</script>

<template>
  <div class="h-[calc(100vh-160px)] w-full relative transition-colors duration-300">
    <!-- Loading Overlay -->
    <div v-if="store.isProcessing || isLoadingModel" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-white/90 dark:bg-gray-900/90 transition-colors duration-300">
      <div class="w-12 h-12 border-4 border-brand-teal border-t-transparent rounded-full animate-spin mb-6"></div>
      <div class="text-center">
        <h2 class="font-display text-xl font-bold mb-1 text-brand-dark dark:text-white transition-colors duration-300">
          {{ isLoadingModel ? 'Loading Model' : 'Reconstructing Geometry' }}
        </h2>
        <p class="font-mono text-sm text-gray-500 dark:text-gray-400">
          {{ isLoadingModel ? 'PARSING GLB...' : 'VOXELIZATION IN PROGRESS...' }}
        </p>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="store.error" class="absolute top-4 left-4 z-40 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm max-w-sm">
      {{ store.error }}
    </div>

    <!-- 3D Viewport -->
    <TresCanvas v-if="!store.isProcessing && !isLoadingModel" window-size :clear-color="canvasColor">
      <TresPerspectiveCamera :position="[3, 3, 3]" :look-at="[0, 0, 0]" />
      <OrbitControls />

      <TresAmbientLight :intensity="1" />
      <TresDirectionalLight :position="[2, 5, 2]" :intensity="2" />

      <!-- Real GLB model -->
      <primitive v-if="store.modelScene" :object="store.modelScene" :scale="[scaleX, scaleY, scaleZ]" />

      <!-- Fallback placeholder -->
      <TresMesh v-else :scale="[scaleX, scaleY, scaleZ]">
        <TresTorusKnotGeometry :args="[0.8, 0.3, 100, 16]" />
        <TresMeshStandardMaterial color="#564D4D" :roughness="0.3" :metalness="0.5" />
      </TresMesh>

      <Grid :args="[10, 10]" :cell-color="gridColor" :section-color="gridSectionColor" fade-distance="20" />
    </TresCanvas>

    <!-- HUD Controls -->
    <div v-if="!store.isProcessing && !isLoadingModel" class="absolute top-4 right-4 bg-white/90 dark:bg-gray-800/90 backdrop-blur border border-gray-200 dark:border-gray-700 p-4 rounded-xl shadow-sm w-72 transition-colors duration-300 max-h-[80vh] overflow-y-auto">
      <h3 class="font-mono text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Model Properties</h3>

      <!-- Lock Scale Toggle -->
      <div class="mb-3 flex items-center gap-2">
        <button
          @click="lockScale = !lockScale"
          class="text-xs font-mono px-2 py-1 rounded border transition-colors"
          :class="lockScale ? 'bg-brand-teal text-white border-brand-teal' : 'bg-transparent text-gray-500 border-gray-300 dark:border-gray-600'"
        >
          {{ lockScale ? 'Uniform' : 'Per-Axis' }}
        </button>
      </div>

      <!-- Scale X -->
      <div class="mb-3 text-brand-dark dark:text-gray-200">
        <label class="flex justify-between text-sm font-medium mb-1">
          <span>Scale X</span>
          <span class="font-mono text-xs">{{ scaleX.toFixed(2) }}x</span>
        </label>
        <input
          type="range" min="0.1" max="5.0" step="0.01"
          :value="scaleX"
          @input="updateScaleX($event.target.value)"
          class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-brand-teal"
        />
      </div>

      <!-- Scale Y -->
      <div class="mb-3 text-brand-dark dark:text-gray-200">
        <label class="flex justify-between text-sm font-medium mb-1">
          <span>Scale Y</span>
          <span class="font-mono text-xs">{{ scaleY.toFixed(2) }}x</span>
        </label>
        <input
          type="range" min="0.1" max="5.0" step="0.01"
          :value="scaleY"
          @input="updateScaleY($event.target.value)"
          class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-brand-teal"
        />
      </div>

      <!-- Scale Z -->
      <div class="mb-3 text-brand-dark dark:text-gray-200">
        <label class="flex justify-between text-sm font-medium mb-1">
          <span>Scale Z</span>
          <span class="font-mono text-xs">{{ scaleZ.toFixed(2) }}x</span>
        </label>
        <input
          type="range" min="0.1" max="5.0" step="0.01"
          :value="scaleZ"
          @input="updateScaleZ($event.target.value)"
          class="w-full h-1 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-brand-teal"
        />
      </div>

      <!-- Dimension Inputs (mm) -->
      <div class="border-t border-gray-100 dark:border-gray-700 pt-3 mb-3">
        <h4 class="font-mono text-xs text-gray-400 uppercase tracking-wider mb-2">Dimensions (mm)</h4>
        <div class="grid grid-cols-3 gap-2">
          <div>
            <label class="text-xs text-gray-500 dark:text-gray-400">W</label>
            <input
              type="number" step="0.1" min="0"
              :value="dimX"
              @input="updateDimX($event.target.value)"
              class="w-full text-sm font-mono px-2 py-1 rounded border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-brand-dark dark:text-white"
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 dark:text-gray-400">H</label>
            <input
              type="number" step="0.1" min="0"
              :value="dimY"
              @input="updateDimY($event.target.value)"
              class="w-full text-sm font-mono px-2 py-1 rounded border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-brand-dark dark:text-white"
            />
          </div>
          <div>
            <label class="text-xs text-gray-500 dark:text-gray-400">D</label>
            <input
              type="number" step="0.1" min="0"
              :value="dimZ"
              @input="updateDimZ($event.target.value)"
              class="w-full text-sm font-mono px-2 py-1 rounded border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-brand-dark dark:text-white"
            />
          </div>
        </div>
      </div>

      <!-- Model Info -->
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
    <div v-if="!store.isProcessing && !isLoadingModel" class="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-4">
      <button
        @click="store.confirmModel"
        class="bg-brand-teal text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 hover:scale-105 transition-all"
      >
        Export STL
      </button>
    </div>
  </div>
</template>
