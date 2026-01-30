<script setup>
import { computed } from 'vue';
import { useProcessStore } from './stores/process';
import { useThemeStore } from './stores/theme';
import AppHeader from './components/AppHeader.vue';
import ProcessStepper from './components/ProcessStepper.vue';
import GravityStars from './components/GravityStars.vue';
import UploadView from './views/UploadView.vue';
import PreviewView from './views/PreviewView.vue';
import ExportView from './views/ExportView.vue';

const store = useProcessStore();
const theme = useThemeStore(); // Initialize theme

const currentView = computed(() => {
  switch (store.currentStepIndex) {
    case 0: return UploadView;
    case 1: return PreviewView;
    case 2: return ExportView;
    default: return UploadView;
  }
});
</script>

<template>
  <div class="min-h-screen bg-brand-white dark:bg-gray-950 text-brand-dark dark:text-gray-100 font-sans selection:bg-brand-teal selection:text-white flex flex-col transition-colors duration-300 relative overflow-hidden">
    <!-- Background Effect -->
    <GravityStars />

    <AppHeader class="relative z-10" />

    <main class="flex-1 flex flex-col relative z-10">
      <ProcessStepper />

      <div class="flex-1 relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="transform opacity-0 translate-y-4"
          enter-to-class="transform opacity-100 translate-y-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="transform opacity-100 translate-y-0"
          leave-to-class="transform opacity-0 -translate-y-4"
          mode="out-in"
        >
          <component :is="currentView" />
        </Transition>
      </div>
    </main>

    <footer class="py-6 text-center text-xs text-gray-400 dark:text-gray-600 font-mono border-t border-gray-100 dark:border-gray-800 transition-colors duration-300 relative z-10">
      PROTOSCALE SYSTEMS v0.1.0-ALPHA • LOCAL COMPUTE NODE
    </footer>
  </div>
</template>
