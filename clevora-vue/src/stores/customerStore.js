import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(JSON.parse(localStorage.getItem('customer')) || null);
  const token = ref(localStorage.getItem('customer_token') || null);
  const expireAt = ref(parseInt(localStorage.getItem('customer_expire_at')) || null);
  let inactivityTimer = null;
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30分鐘

  const isAuthenticated = computed(() => {
    return !!customer.value && !!token.value && !!expireAt.value && Date.now() < expireAt.value;
  });

  function setCustomer(userData, authToken, expireTime) {
    customer.value = userData;
    token.value = authToken;
    expireAt.value = expireTime;
    
    // 保存到 localStorage
    localStorage.setItem('customer', JSON.stringify(userData));
    localStorage.setItem('customer_token', authToken);
    localStorage.setItem('customer_expire_at', expireTime);
    
    console.log('CustomerStore: setCustomer 被呼叫。');
    console.log('新 customer:', customer.value);
    console.log('新 token:', token.value);
    console.log('新 expireAt:', expireAt.value);
    
    // 如果有效的登录，启动活动监听和计时器
    if (userData && authToken && expireTime) {
      addActivityListeners();
      startInactivityTimer();
    }
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
    if (source === 'inactivity') {
      window.dispatchEvent(new CustomEvent('inactivity-logout', { detail: { type: 'customer' } }));
    } else if (source === 'kicked') {
      window.dispatchEvent(new CustomEvent('kicked-logout', { detail: { type: 'customer' } }));
    }
  }

  // 初始化时检查是否需要自动登出
  if (expireAt.value && Date.now() >= expireAt.value) {
    console.log('CustomerStore: 檢測到過期的登入狀態，執行自動登出');
    customer.value = null;
    token.value = null;
    expireAt.value = null;
    localStorage.removeItem('customer');
    localStorage.removeItem('customer_token');
    localStorage.removeItem('customer_expire_at');
  } else if (customer.value && token.value && expireAt.value) {
    console.log('CustomerStore: 檢測到有效的登入狀態，啟動活動監聽');
    addActivityListeners();
    startInactivityTimer();
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
