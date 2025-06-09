import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';

export const useUserStore = defineStore('user', () => {
  const admin_token = ref(localStorage.getItem('admin_token') || '');
  console.log('[UserStore Init] localStorage admin_token:', localStorage.getItem('admin_token'));
  console.log('[UserStore Init] admin_token.value initialized to:', admin_token.value);

  const expire_at = ref(parseInt(localStorage.getItem('expire_at')) || null);
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
    
    //console.log('[isAuthenticated check]:');
    //console.log('  admin_token.value:', token ? '存在' : '不存在');
    //console.log('  expire_at.value:', expiry);
    //console.log('  目前時間 (ms):', now);
    
    // Check if token exists AND expiry is a valid number AND current time is less than expiry
    const isActuallyAuthenticated = !!token && expiry !== null && !isNaN(expiry) && now < expiry;
    
    //console.log('  是否過期 (calculated):', !isActuallyAuthenticated && !!token); // More descriptive
    //console.log('  最終 isAuthenticated:', isActuallyAuthenticated);

    return isActuallyAuthenticated;
  });

  function startInactivityTimer() {
    //console.log('[UserStore] Starting inactivity timer...');
    clearInactivityTimer();
    inactivityTimer = setTimeout(() => {
      //console.log('[UserStore] Inactivity timer triggered. Logging out.');
      logout();
      // No need to push here, logout already pushes
    }, INACTIVITY_TIMEOUT);
  }

  function resetInactivityTimer() {
    //console.log('[UserStore] resetInactivityTimer called. isAuthenticated:', isAuthenticated.value);
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
      //onsole.log('[UserStore] Inactivity timer cleared.');
    }
  }

  function addActivityListeners() {
      //console.log('[UserStore] Adding activity listeners.');
      window.addEventListener('mousemove', resetInactivityTimer);
      window.addEventListener('keypress', resetInactivityTimer);
      window.addEventListener('click', resetInactivityTimer);
      window.addEventListener('scroll', resetInactivityTimer);
  }

  function removeActivityListeners() {
      //console.log('[UserStore] Removing activity listeners.');
      window.removeEventListener('mousemove', resetInactivityTimer);
      window.removeEventListener('keypress', resetInactivityTimer);
      window.removeEventListener('click', resetInactivityTimer);
      window.removeEventListener('scroll', resetInactivityTimer);
  }

  function setToken(tokenValue, expireAtValue) {
    //console.log('[UserStore] setToken called. tokenValue type:', typeof tokenValue, 'expireAtValue type:', typeof expireAtValue, 'expireAtValue:', expireAtValue);
    admin_token.value = tokenValue;
    // 如果沒有提供 expireAtValue，則設定為 24 小時後過期
    expire_at.value = expireAtValue || Date.now() + 24 * 60 * 60 * 1000;
    //console.log('[UserStore] admin_token.value after setToken:', admin_token.value);
    //console.log('[UserStore] expire_at.value after setToken:', expire_at.value);
    if (tokenValue) {
        addActivityListeners();
        if (route.value) {
            //console.log('[UserStore] setToken: route is present, resetting inactivity timer.');
            resetInactivityTimer();
        } else {
            //console.log('[UserStore] setToken: route is not yet present, timer not reset.');
        }
        localStorage.setItem('admin_token', tokenValue);
        localStorage.setItem('expire_at', expire_at.value.toString());
    } else {
        //console.log('[UserStore] setToken: tokenValue is empty, clearing inactivity timer and removing listeners.');
        clearInactivityTimer();
        removeActivityListeners();
        localStorage.removeItem('admin_token');
        localStorage.removeItem('expire_at');
    }
  }

  function logout(source = 'unknown') {
    const now = new Date().toISOString();
    //console.log(`[UserStore] Logging out admin user. 來源: ${source}, 時間: ${now}`);
    admin_token.value = '';
    expire_at.value = null;
    user.value = null;
    clearInactivityTimer();
    removeActivityListeners();
    localStorage.removeItem('admin_token');
    localStorage.removeItem('expire_at');
    if (source === 'inactivity') {
      window.dispatchEvent(new CustomEvent('inactivity-logout', { detail: { type: 'admin' } }));
    }
    router.push('/admin/login'); // Explicitly push to login on logout
  }

  // Initial setup on store creation
  if (admin_token.value && expire_at.value && Date.now() < expire_at.value) {
      //console.log('[UserStore] Admin authenticated on store load, starting timer and listeners.');
      addActivityListeners();
  } else if (localStorage.getItem('admin_token') && (!expire_at.value || Date.now() >= expire_at.value)) {
      //console.log('[UserStore] Expired or invalid admin token found in localStorage on load. Performing explicit logout.');
      logout(); // Perform an immediate logout to clear any lingering invalid state
  } else {
      //console.log('[UserStore] No valid admin token found on store load.');
  }

  watch(() => router.currentRoute.value, (newRoute) => {
    if (newRoute) {
      route.value = newRoute;
      //console.log('[UserStore] Route changed to:', newRoute.path);
      if (newRoute.path.startsWith('/admin') && isAuthenticated.value) {
        //console.log('[UserStore] Route is admin path and authenticated, resetting inactivity timer.');
        resetInactivityTimer();
      } else {
        //console.log('[UserStore] Route is not admin path or not authenticated, clearing inactivity timer.');
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