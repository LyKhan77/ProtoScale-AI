<script setup>
import { useProcessStore } from '../stores/process';
import ThemeToggle from './ThemeToggle.vue';

const store = useProcessStore();
</script>

<template>
  <header class="w-full h-20 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-8 bg-brand-white dark:bg-gray-900 sticky top-0 z-50 transition-colors duration-300">
    <div 
      class="flex items-center gap-4 cursor-pointer hover:opacity-80 transition-opacity"
      @click="store.reset"
    >
      <img src="/logoProtoScale.png" alt="ProtoScale" class="h-12 w-auto" />
      <span class="font-display font-bold text-2xl tracking-tight text-brand-dark dark:text-white transition-colors duration-300">ProtoScale</span>
    </div>
    
    <div class="flex items-center gap-4">
      <ThemeToggle />
    </div>
  </header>
</template>
