import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(null);
  const token = ref(null);
  const expireAt = ref(null);
  let inactivityTimer = null;
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30分鐘

  const isAuthenticated = computed(() => {
    return !!customer.value && !!token.value && !!expireAt.value && Date.now() < expireAt.value;
  });

  function setCustomer(userData, authToken, expireTime) {
    customer.value = userData;
    token.value = authToken;
    expireAt.value = expireTime;
    console.log('CustomerStore: setCustomer 被呼叫。');
    console.log('新 customer:', customer.value);
    console.log('新 token:', token.value);
    console.log('新 expireAt:', expireAt.value);
  }

  function startInactivityTimer() {
    clearInactivityTimer();
    inactivityTimer = setTimeout(() => {
      logout('inactivity');
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

  // 登入時呼叫
  watch(isAuthenticated, (val) => {
    if (val) {
      addActivityListeners();
      startInactivityTimer();
    } else {
      removeActivityListeners();
      clearInactivityTimer();
    }
  }, { immediate: true });

  function logout(source = 'unknown') {
    const now = new Date().toISOString();
    console.log(`CustomerStore: logout 被呼叫。來源: ${source}, 時間: ${now}。狀態已清空。`);
    customer.value = null;
    token.value = '';
    expireAt.value = '';
    localStorage.removeItem('customer');
    localStorage.removeItem('customer_token');
    localStorage.removeItem('customer_expire_at');
    removeActivityListeners();
    clearInactivityTimer();
  }

  // 新增日誌用於偵錯
  console.log('CustomerStore 初始化。目前狀態：');
  console.log('customer:', customer.value);
  console.log('token:', token.value);
  console.log('expireAt:', expireAt.value);
  console.log('isAuthenticated:', isAuthenticated.value);

  return {
    customer,
    token,
    expireAt,
    isAuthenticated,
    setCustomer,
    logout,
  };
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'customer',
        storage: localStorage,
        paths: ['customer', 'token', 'expireAt']
      }
    ]
  }
});
