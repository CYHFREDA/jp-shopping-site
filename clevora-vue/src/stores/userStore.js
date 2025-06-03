import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useUserStore = defineStore('user', () => {
  const basic_token = ref(localStorage.getItem('basic_token') || '');
  const user = ref(null);

  const isAuthenticated = computed(() => !!basic_token.value);

  function setToken(tokenValue) {
    basic_token.value = tokenValue;
    localStorage.setItem('basic_token', tokenValue);
    const expireAt = Date.now() + 7 * 24 * 60 * 60 * 1000; // 7 天後過期
    localStorage.setItem('expire_at', expireAt);
  }

  function logout() {
    basic_token.value = '';
    user.value = null;
    localStorage.removeItem('basic_token');
    localStorage.removeItem('expire_at');
  }

  return {
    basic_token,
    user,
    isAuthenticated,
    setToken,
    logout
  };
}); 