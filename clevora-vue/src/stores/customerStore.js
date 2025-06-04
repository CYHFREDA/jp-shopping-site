import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(null);
  const expireAt = ref(null);

  const isAuthenticated = computed(() => {
    return !!customer.value && !!expireAt.value && Date.now() < expireAt.value;
  });

  function setCustomer(data) {
    customer.value = data;
    if (data) {
      expireAt.value = Date.now() + 30 * 60 * 1000; // 30 分鐘有效
    } else {
      customer.value = null;
      expireAt.value = null;
    }
  }

  function logout() {
    alert('登入已過期，請重新登入');
    setCustomer(null);
  }

  return {
    customer,
    expireAt,
    isAuthenticated,
    setCustomer,
    logout
  };
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'customer',
        storage: localStorage,
        paths: ['customer', 'expireAt']
      }
    ]
  }
});
