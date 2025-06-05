import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export const useUserStore = defineStore('user', () => {
  const admin_token = ref('');
  const user = ref(null);

  let inactivityTimer = null;
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000;

  const router = useRouter();

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

  function startInactivityTimer() {
    console.log('Starting inactivity timer...');
    clearInactivityTimer();
    inactivityTimer = setTimeout(() => {
      console.log('Inactivity timer triggered. Logging out.');
      logout();
      router.push('/admin/login');
    }, INACTIVITY_TIMEOUT);
  }

  function resetInactivityTimer() {
    if (isAuthenticated.value) {
       startInactivityTimer();
    }
  }

  function clearInactivityTimer() {
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
      inactivityTimer = null;
    }
  }

  function addActivityListeners() {
      window.addEventListener('mousemove', resetInactivityTimer);
      window.addEventListener('keypress', resetInactivityTimer);
      window.addEventListener('click', resetInactivityTimer);
      window.addEventListener('scroll', resetInactivityTimer);
  }

  function removeActivityListeners() {
      window.removeEventListener('mousemove', resetInactivityTimer);
      window.removeEventListener('keypress', resetInactivityTimer);
      window.removeEventListener('click', resetInactivityTimer);
      window.removeEventListener('scroll', resetInactivityTimer);
  }

  function setToken(tokenValue, expireAtValue) {
    admin_token.value = tokenValue;
    localStorage.setItem('admin_token', tokenValue);
    localStorage.setItem('expire_at', expireAtValue);
    if (tokenValue) {
        startInactivityTimer();
        addActivityListeners();
    }
  }

  function logout() {
    console.log('Logging out admin user.');
    admin_token.value = '';
    user.value = null;
    localStorage.removeItem('admin_token');
    localStorage.removeItem('expire_at');
    clearInactivityTimer();
    removeActivityListeners();
  }

  const initialToken = localStorage.getItem('admin_token');
  const initialExpiry = localStorage.getItem('expire_at');
  const now = Date.now();
  const isInitialTokenValid = initialToken && initialExpiry && now < parseInt(initialExpiry, 10);

  if (isInitialTokenValid) {
      admin_token.value = initialToken;
      startInactivityTimer();
      addActivityListeners();
      console.log('Admin authenticated on load, starting timer and listeners.');
  } else if (initialToken) {
      logout();
      console.log('Expired or invalid admin token found on load, logging out.');
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