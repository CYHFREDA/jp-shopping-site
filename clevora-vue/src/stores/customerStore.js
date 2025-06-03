import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(null);

  const isAuthenticated = computed(() => !!customer.value);

  function setCustomer(customerData) {
    customer.value = customerData;
    if (customerData) {
      localStorage.setItem('customer', JSON.stringify(customerData));
    } else {
      localStorage.removeItem('customer');
    }
  }

  function loadCustomer() {
    const storedCustomer = localStorage.getItem('customer');
    if (storedCustomer) {
      customer.value = JSON.parse(storedCustomer);
    }
  }

  function logout() {
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