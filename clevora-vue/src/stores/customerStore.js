import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(JSON.parse(localStorage.getItem('customer')) || null);
  const token = ref(localStorage.getItem('customer_token') || null);
  const expireAt = ref(parseInt(localStorage.getItem('customer_expire_at')) || null);
  let inactivityTimer = null;
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30分鐘

  const isAuthenticated = computed(() => {
    const now = Date.now();
    const hasValidToken = token.value && expireAt.value && now < expireAt.value;
    const hasValidCustomer = customer.value && customer.value.customer_id;
    return hasValidToken && hasValidCustomer;
  });

  // 新增：支付相關的狀態
  const paymentInProgress = ref(false);
  const paymentOrderId = ref(null);
  const paymentToken = ref(null);

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

  // 新增：開始支付流程
  function startPayment(orderId) {
    paymentInProgress.value = true;
    paymentOrderId.value = orderId;
    paymentToken.value = token.value;
    
    // 保存支付狀態到 sessionStorage（這樣重整頁面也不會遺失）
    sessionStorage.setItem('payment_in_progress', 'true');
    sessionStorage.setItem('payment_order_id', orderId);
    sessionStorage.setItem('payment_token', token.value);
  }

  // 新增：結束支付流程
  function endPayment() {
    paymentInProgress.value = false;
    paymentOrderId.value = null;
    paymentToken.value = null;
    
    // 清除 sessionStorage 中的支付狀態
    sessionStorage.removeItem('payment_in_progress');
    sessionStorage.removeItem('payment_order_id');
    sessionStorage.removeItem('payment_token');
  }

  // 新增：嘗試重新連接
  async function tryReconnect() {
    // 如果是支付過程中
    if (sessionStorage.getItem('payment_in_progress') === 'true') {
      const savedToken = sessionStorage.getItem('payment_token');
      if (savedToken) {
        try {
          // 使用保存的 token 嘗試重新驗證
          const response = await fetch('/api/customers/verify-token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${savedToken}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            setCustomer(data.customer, savedToken, Date.now() + 30 * 60 * 1000); // 重新設置 30 分鐘
            return true;
          }
        } catch (error) {
          console.error('重新連接失敗:', error);
        }
      }
    }
    return false;
  }

  function startInactivityTimer() {
    // 如果正在支付中，不啟動計時器
    if (isAuthenticated.value && !paymentInProgress.value) {
      inactivityTimer = setTimeout(() => {
        console.log('CustomerStore: 檢測到 30 分鐘無活動，執行自動登出');
        logout('inactivity');
        window.alert('由於長時間未操作，系統已自動登出。');
        window.location.href = '/login';
      }, INACTIVITY_TIMEOUT);
    }
  }

  function resetInactivityTimer() {
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
    }
    startInactivityTimer();
  }

  function addActivityListeners() {
    if (typeof window !== 'undefined') {
      ['mousemove', 'keydown', 'click', 'touchstart'].forEach(event => {
        window.addEventListener(event, resetInactivityTimer);
      });
    }
  }

  function removeActivityListeners() {
    if (typeof window !== 'undefined') {
      ['mousemove', 'keydown', 'click', 'touchstart'].forEach(event => {
        window.removeEventListener(event, resetInactivityTimer);
      });
    }
  }

  function clearInactivityTimer() {
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
      inactivityTimer = null;
    }
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

  function logout(reason = '') {
    console.log(`CustomerStore: 執行登出，原因: ${reason}`);
    customer.value = null;
    token.value = null;
    expireAt.value = null;
    
    // 清除 localStorage
    localStorage.removeItem('customer');
    localStorage.removeItem('customer_token');
    localStorage.removeItem('customer_expire_at');
    
    // 移除活動監聽器
    removeActivityListeners();
    
    // 清除計時器
    if (inactivityTimer) {
      clearTimeout(inactivityTimer);
      inactivityTimer = null;
    }
  }

  // 初始化時檢查登入狀態
  if (token.value && expireAt.value) {
    const now = Date.now();
    if (now >= expireAt.value) {
      console.log('CustomerStore: 檢測到過期的登入狀態，執行自動登出');
      logout('expired');
    } else {
      console.log('CustomerStore: 檢測到有效的登入狀態，啟動活動監聽');
      addActivityListeners();
      startInactivityTimer();
    }
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
    paymentInProgress,
    paymentOrderId,
    setCustomer,
    logout,
    startPayment,
    endPayment,
    tryReconnect
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
