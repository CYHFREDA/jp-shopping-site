import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '');
  const user = ref(null);

  const isAuthenticated = computed(() => !!token.value);

  async function login(credentials) {
    try {
      const response = await axios.post('/api/admin/login', credentials);
      if (response.data.token) {
        token.value = response.data.token;
        user.value = response.data.user;
        localStorage.setItem('token', response.data.token);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  }

  function logout() {
    token.value = '';
    user.value = null;
    localStorage.removeItem('token');
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout
  };
}); 