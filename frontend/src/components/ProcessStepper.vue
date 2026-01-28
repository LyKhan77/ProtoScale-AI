<script setup>
import { useProcessStore } from '../stores/process';
import { storeToRefs } from 'pinia';

const store = useProcessStore();
const { steps, currentStepIndex } = storeToRefs(store);
</script>

<template>
  <div class="w-full max-w-3xl mx-auto py-8">
    <div class="relative flex justify-between items-center">
      <!-- Connecting Line -->
      <div class="absolute top-1/2 left-0 w-full h-0.5 bg-gray-200 dark:bg-gray-800 -z-10 transform -translate-y-1/2 transition-colors duration-300"></div>
      
      <!-- Steps -->
      <div 
        v-for="(step, index) in steps" 
        :key="step"
        class="flex flex-col items-center bg-brand-white dark:bg-gray-950 px-2 transition-colors duration-300"
      >
        <div 
          class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono border-2 transition-all duration-300"
          :class="[
            index < currentStepIndex 
              ? 'bg-brand-teal border-brand-teal text-white' 
              : index === currentStepIndex
                ? 'border-brand-teal text-brand-teal bg-white dark:bg-gray-900'
                : 'border-gray-300 dark:border-gray-700 text-gray-300 dark:text-gray-700 bg-white dark:bg-gray-900'
          ]"
        >
          <span v-if="index < currentStepIndex">✓</span>
          <span v-else>{{ index + 1 }}</span>
        </div>
        
        <span 
          class="mt-2 text-xs font-medium uppercase tracking-wider transition-colors duration-300"
          :class="index <= currentStepIndex ? 'text-brand-dark dark:text-gray-200' : 'text-gray-300 dark:text-gray-700'"
        >
          {{ step }}
        </span>
      </div>
    </div>
  </div>
</template>
