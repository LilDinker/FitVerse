// stores/auth.ts
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: '' // Initialize with an empty string or null
  }),
  actions: {
    setAccessToken(token: string) {
      this.accessToken = token;
      localStorage.setItem('accessToken', token); // Optional: persist to localStorage
    },
    loadAccessToken() {
      const token = localStorage.getItem('accessToken');
      if (token) this.accessToken = token;
    },
    clearAccessToken() {
      this.accessToken = '';
      localStorage.removeItem('accessToken');
    }
  }
});
