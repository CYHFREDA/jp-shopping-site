import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(null);
  const token = ref(null);
  const expireAt = ref(null);

  const isAuthenticated = computed(() => {
    return !!customer.value && !!token.value && !!expireAt.value && Date.now() < expireAt.value;
  });

  function setCustomer(userData, authToken, expireTime) {
    customer.value = userData;
    token.value = authToken;
    expireAt.value = expireTime;
  }

  function logout() {
    customer.value = null;
    token.value = '';
    expireAt.value = '';
    localStorage.removeItem('customer');
    localStorage.removeItem('customer_token');
    localStorage.removeItem('customer_expire_at');
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
