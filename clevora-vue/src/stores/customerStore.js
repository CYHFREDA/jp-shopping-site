import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(null);
  const token = ref(null);
  const expireAt = ref(null);

  const isAuthenticated = computed(() => {
    return !!customer.value && !!token.value && !!expireAt.value && Date.now() < expireAt.value;
  });

  function setCustomer(data, token, expireAtValue) {
    if (data && token && expireAtValue) {
      customer.value = {
        ...data,
        customer_id: data.customer_id
      };
      token.value = token;
      expireAt.value = expireAtValue;
      
      localStorage.setItem('customer', JSON.stringify(customer.value));
      localStorage.setItem('customer_token', token);
      localStorage.setItem('customer_expire_at', expireAtValue);
    } else {
      customer.value = null;
      token.value = null;
      expireAt.value = null;
      localStorage.removeItem('customer');
      localStorage.removeItem('customer_token');
      localStorage.removeItem('customer_expire_at');
    }
  }

  function logout() {
    alert('登入已過期，請重新登入');
    setCustomer(null, null, null);
  }

  // 初始化時從 localStorage 載入資料
  function init() {
    const storedCustomer = localStorage.getItem('customer');
    const storedToken = localStorage.getItem('customer_token');
    const storedExpireAt = localStorage.getItem('customer_expire_at');
    
    if (storedCustomer && storedToken && storedExpireAt) {
      try {
        const expireTime = parseInt(storedExpireAt);
        if (expireTime > Date.now()) {
          customer.value = JSON.parse(storedCustomer);
          token.value = storedToken;
          expireAt.value = expireTime;
        } else {
          console.log('Token 已過期');
          setCustomer(null, null, null);
        }
      } catch (error) {
        console.error('載入本地儲存資料錯誤：', error);
        setCustomer(null, null, null);
      }
    } else {
       console.log('本地儲存無用戶資料或token');
    }
  }

  // 在 store 創建時初始化
  init();

  return {
    customer,
    token,
    expireAt,
    isAuthenticated,
    setCustomer,
    logout,
    init
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
