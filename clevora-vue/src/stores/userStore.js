import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';

export const useUserStore = defineStore('user', () => {
  const admin_token = ref(localStorage.getItem('admin_token') || '');
  const expire_at = ref(parseInt(localStorage.getItem('expire_at'), 10) || null);
  const user = ref(null);

  let inactivityTimer = null;
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000;

  const router = useRouter();
  const route = ref(null);

  const isAuthenticated = computed(() => {
    const token = admin_token.value;
    const expiry = expire_at.value;
    const now = Date.now();
    const isExpired = !expiry || now >= expiry;

    console.log('isAuthenticated check:');
    console.log('  admin_token.value:', token ? '存在' : '不存在');
    console.log('  expire_at.value:', expiry);
    console.log('  目前時間 (ms):', now);
    console.log('  過期時間 (ms):', expiry);
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
    } else {
       clearInactivityTimer();
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
    expire_at.value = expireAtValue;
    if (tokenValue) {
        addActivityListeners();
        if (route.value) {
            resetInactivityTimer();
        }
    }
  }

  function logout() {
    console.log('Logging out admin user.');
    admin_token.value = '';
    expire_at.value = null;
    user.value = null;
    clearInactivityTimer();
    removeActivityListeners();
  }

  if (isAuthenticated.value) {
      console.log('Admin authenticated on load (via initial state), starting timer and listeners.');
      addActivityListeners();
  } else if (localStorage.getItem('admin_token')) {
      console.log('Expired or invalid admin token found in localStorage on load.');
  }

  watch(() => router.currentRoute.value, (newRoute) => {
    if (newRoute) {
      route.value = newRoute;
      console.log('Route changed to:', newRoute.path);
      resetInactivityTimer();
    }
  }, { immediate: true });

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
        paths: ['admin_token', 'expire_at']
      }
    ]
  }
}); 