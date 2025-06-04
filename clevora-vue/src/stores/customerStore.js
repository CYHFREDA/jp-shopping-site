import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(null);
  const expireAt = ref(null);

  const isAuthenticated = computed(() => {
    if (!customer.value || !expireAt.value) return false;
    return Date.now() < expireAt.value;
  });

  function setCustomer(customerData) {
    customer.value = customerData;
    if (customerData) {
      // 設定 30 分鐘後過期
      const expireTime = Date.now() + 30 * 60 * 1000;
      expireAt.value = expireTime;
      localStorage.setItem('customer', JSON.stringify(customerData));
      localStorage.setItem('customer_expire_at', expireTime);
    } else {
      customer.value = null;
      expireAt.value = null;
      localStorage.removeItem('customer');
      localStorage.removeItem('customer_expire_at');
    }
  }

  function loadCustomer() {
    const storedCustomer = localStorage.getItem('customer');
    const storedExpireAt = localStorage.getItem('customer_expire_at');
    
    if (storedCustomer && storedExpireAt) {
      const expireTime = parseInt(storedExpireAt);
      if (Date.now() < expireTime) {
        customer.value = JSON.parse(storedCustomer);
        expireAt.value = expireTime;
      } else {
        // 如果已過期，清除資料
        logout();
      }
    }
  }

  function logout() {
    alert('已閒置30分鐘，您的登入已過期，請重新登入。');
    setCustomer(null);
  }

  // 我們目前還沒有前台客戶登入的 API 請求邏輯，這部分後續再添加
  // async function login(credentials) { ... }

  return { 
    customer, 
    isAuthenticated, 
    setCustomer, 
    loadCustomer,
    logout 
  };
}); 