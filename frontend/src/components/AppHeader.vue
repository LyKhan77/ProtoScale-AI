<script setup>
import ThemeToggle from './ThemeToggle.vue';
</script>

<template>
  <header class="w-full h-20 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-8 bg-brand-white dark:bg-gray-900 sticky top-0 z-50 transition-colors duration-300">
    <div class="flex items-center gap-4">
      <img src="/logoProtoScale.png" alt="ProtoScale" class="h-12 w-auto" />
      <span class="font-display font-bold text-2xl tracking-tight text-brand-dark dark:text-white transition-colors duration-300">ProtoScale</span>
    </div>
    
    <div class="flex items-center gap-4">
      <ThemeToggle />
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-brand-teal animate-pulse"></div>
        <span class="text-xs font-mono text-gray-500 dark:text-gray-400 uppercase tracking-wider">System Operational</span>
      </div>
    </div>
  </header>
</template>
