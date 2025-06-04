import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useUserStore = defineStore('user', () => {
  const admin_token = ref('');
  const user = ref(null);

  const isAuthenticated = computed(() => {
    const token = admin_token.value;
    const expiry = localStorage.getItem('expire_at');
    const now = Date.now();
    const isExpired = !expiry || now >= parseInt(expiry, 10);

    console.log('isAuthenticated check:');
    console.log('  admin_token.value:', token ? '存在' : '不存在');
    console.log('  localStorage expire_at:', expiry);
    console.log('  目前時間 (ms):', now);
    console.log('  過期時間 (ms):', parseInt(expiry, 10));
    console.log('  是否過期:', isExpired);
    console.log('  最終 isAuthenticated:', !!token && !isExpired);

    return !!token && !isExpired;
  });

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
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user',
        storage: localStorage,
        paths: ['admin_token']
      }
    ]
  }
}); 