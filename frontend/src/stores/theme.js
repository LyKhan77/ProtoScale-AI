import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  // Initialize from localStorage or system preference
  const isDark = ref(
    localStorage.theme === 'dark' || 
    (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
  );

  function toggleTheme() {
    isDark.value = !isDark.value;
    updateDOM();
  }

  function updateDOM() {
    if (isDark.value) {
      document.documentElement.classList.add('dark');
      localStorage.theme = 'dark';
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.theme = 'light';
    }
  }

  // Initial apply
  updateDOM();

  return {
    isDark,
    toggleTheme
  };
});
