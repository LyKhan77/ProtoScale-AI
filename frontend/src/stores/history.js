import { defineStore } from 'pinia';
import { ref } from 'vue';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8077';
const STORAGE_KEY = 'protoscale-history';

export const useHistoryStore = defineStore('history', () => {
  const items = ref([]);

  function getLocalData() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch {
      return [];
    }
  }

  function saveLocalData(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  async function loadHistory() {
    try {
      const res = await fetch(`${API_BASE}/api/jobs`);
      if (!res.ok) return;
      const jobs = await res.json();
      const local = getLocalData();
      const localMap = Object.fromEntries(local.map(l => [l.jobId, l]));

      items.value = jobs.map(job => ({
        jobId: job.job_id,
        name: localMap[job.job_id]?.name || job.job_id.slice(0, 8),
        thumbnailUrl: `${API_BASE}/api/jobs/${job.job_id}/thumbnail`,
        createdAt: job.created_at,
      }));
    } catch (e) {
      console.warn('Failed to load history:', e);
    }
  }

  function saveToHistory(jobId) {
    const local = getLocalData();
    if (!local.find(l => l.jobId === jobId)) {
      local.unshift({ jobId, name: jobId.slice(0, 8) });
      saveLocalData(local);
    }
    // Reload to sync with backend
    loadHistory();
  }

  function deleteFromHistory(jobId) {
    const local = getLocalData().filter(l => l.jobId !== jobId);
    saveLocalData(local);
    items.value = items.value.filter(i => i.jobId !== jobId);
  }

  return { items, loadHistory, saveToHistory, deleteFromHistory };
});
