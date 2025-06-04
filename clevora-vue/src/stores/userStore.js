import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useUserStore = defineStore('user', () => {
  const admin_token = ref(localStorage.getItem('admin_token') || '');
  const user = ref(null);

  const isAuthenticated = computed(() => !!admin_token.value);

  function setToken(tokenValue, expireAtValue) {
    admin_token.value = tokenValue;
    localStorage.setItem('admin_token', tokenValue);
    localStorage.setItem('expire_at', expireAtValue);
  }

  function logout() {
    admin_token.value = '';
    user.value = null;
    localStorage.removeItem('admin_token');
    localStorage.removeItem('expire_at');
  }

  return {
    admin_token,
    user,
    isAuthenticated,
    setToken,
    logout
  };
}); 