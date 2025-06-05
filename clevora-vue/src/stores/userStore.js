import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';

export const useUserStore = defineStore('user', () => {
  const admin_token = ref(localStorage.getItem('admin_token') || '');
  console.log('[UserStore Init] localStorage admin_token:', localStorage.getItem('admin_token'));
  console.log('[UserStore Init] admin_token.value initialized to:', admin_token.value);

  const storedExpireAtString = localStorage.getItem('expire_at');
  let initialExpireAtValue = null; // Default to null if not found or invalid

  if (storedExpireAtString) {
    if (storedExpireAtString === 'null' || storedExpireAtString === 'undefined') {
      // If the string is "null" or "undefined", treat it as actual null
      initialExpireAtValue = null;
      console.log('[UserStore Init] localStorage expire_at string is "null" or "undefined", treating as null.');
    } else {
      const parsedValue = parseInt(storedExpireAtString, 10);
      if (!isNaN(parsedValue)) {
        initialExpireAtValue = parsedValue;
        console.log('[UserStore Init] localStorage expire_at successfully parsed to number:', parsedValue);
      } else {
        console.warn('[UserStore Init] localStorage expire_at is a non-numeric string (and not "null"/"undefined"):', storedExpireAtString);
        initialExpireAtValue = null; // Fallback to null if it's a garbage string
      }
    }
  } else {
    console.log('[UserStore Init] localStorage expire_at is empty or null.');
  }

  const expire_at = ref(initialExpireAtValue);
  console.log('[UserStore Init] expire_at.value initialized to:', expire_at.value);

  const user = ref(null);

  let inactivityTimer = null;
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000;

  const router = useRouter();
  const route = ref(null);

  const isAuthenticated = computed(() => {
    const token = admin_token.value;
    const expiry = expire_at.value;
    const now = Date.now();
    
    console.log('[isAuthenticated check]:');
    console.log('  admin_token.value:', token ? '存在' : '不存在');
    console.log('  expire_at.value:', expiry);
    console.log('  目前時間 (ms):', now);
    
    // Check if token exists AND expiry is a valid number AND current time is less than expiry
    const isActuallyAuthenticated = !!token && expiry !== null && !isNaN(expiry) && now < expiry;
    
    console.log('  是否過期 (calculated):', !isActuallyAuthenticated && !!token); // More descriptive
    console.log('  最終 isAuthenticated:', isActuallyAuthenticated);

    return isActuallyAuthenticated;
  });

  function startInactivityTimer() {
    console.log('[UserStore] Starting inactivity timer...');
    clearInactivityTimer();
    inactivityTimer = setTimeout(() => {
      console.log('[UserStore] Inactivity timer triggered. Logging out.');
      logout();
      // No need to push here, logout already pushes
    }, INACTIVITY_TIMEOUT);
  }

  function resetInactivityTimer() {
    console.log('[UserStore] resetInactivityTimer called. isAuthenticated:', isAuthenticated.value);
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
      console.log('[UserStore] Inactivity timer cleared.');
    }
  }

  function addActivityListeners() {
      console.log('[UserStore] Adding activity listeners.');
      window.addEventListener('mousemove', resetInactivityTimer);
      window.addEventListener('keypress', resetInactivityTimer);
      window.addEventListener('click', resetInactivityTimer);
      window.addEventListener('scroll', resetInactivityTimer);
  }

  function removeActivityListeners() {
      console.log('[UserStore] Removing activity listeners.');
      window.removeEventListener('mousemove', resetInactivityTimer);
      window.removeEventListener('keypress', resetInactivityTimer);
      window.removeEventListener('click', resetInactivityTimer);
      window.removeEventListener('scroll', resetInactivityTimer);
  }

  function setToken(tokenValue, expireAtValue) {
    console.log('[UserStore] setToken called. tokenValue type:', typeof tokenValue, 'expireAtValue type:', typeof expireAtValue, 'expireAtValue:', expireAtValue);
    admin_token.value = tokenValue;
    expire_at.value = expireAtValue;
    console.log('[UserStore] admin_token.value after setToken:', admin_token.value);
    console.log('[UserStore] expire_at.value after setToken:', expire_at.value);
    if (tokenValue) {
        addActivityListeners();
        // Only reset timer if a route is already established. This prevents immediate logout on refresh if route isn't ready.
        if (route.value) {
            console.log('[UserStore] setToken: route is present, resetting inactivity timer.');
            resetInactivityTimer();
        } else {
            console.log('[UserStore] setToken: route is not yet present, timer not reset.');
        }
    } else {
        console.log('[UserStore] setToken: tokenValue is empty, clearing inactivity timer and removing listeners.');
        clearInactivityTimer();
        removeActivityListeners();
    }
  }

  function logout() {
    console.log('[UserStore] Logging out admin user.');
    admin_token.value = '';
    expire_at.value = null; // Set to null on explicit logout
    user.value = null;
    clearInactivityTimer();
    removeActivityListeners();
    router.push('/admin/login'); // Explicitly push to login on logout
  }

  // Initial setup on store creation
  if (admin_token.value && expire_at.value && Date.now() < expire_at.value) {
      console.log('[UserStore] Admin authenticated on store load, starting timer and listeners.');
      addActivityListeners();
  } else if (localStorage.getItem('admin_token') && (!expire_at.value || Date.now() >= expire_at.value)) {
      console.log('[UserStore] Expired or invalid admin token found in localStorage on load. Performing explicit logout.');
      logout(); // Perform an immediate logout to clear any lingering invalid state
  } else {
      console.log('[UserStore] No valid admin token found on store load.');
  }

  watch(() => router.currentRoute.value, (newRoute) => {
    if (newRoute) {
      route.value = newRoute;
      console.log('[UserStore] Route changed to:', newRoute.path);
      // Only reset timer if current route is within admin paths AND authenticated
      if (newRoute.path.startsWith('/admin') && isAuthenticated.value) {
        console.log('[UserStore] Route is admin path and authenticated, resetting inactivity timer.');
        resetInactivityTimer();
      } else {
        console.log('[UserStore] Route is not admin path or not authenticated, clearing inactivity timer.');
        clearInactivityTimer();
      }
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