import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import jwt from 'jsonwebtoken';

export const useCustomerStore = defineStore('customer', () => {
  const customer = ref(null);
  const token = ref(null);
  const expireAt = ref(null);

  const isAuthenticated = computed(() => {
    return !!customer.value && !!token.value && !!expireAt.value && Date.now() < expireAt.value;
  });

  function setCustomer(data) {
    if (data) {
      // 生成 JWT 令牌
      const tokenData = {
        customer_id: data.customer_id,
        name: data.name,
        exp: Math.floor(Date.now() / 1000) + (30 * 60) // 30 分鐘過期
      };
      
      const newToken = jwt.sign(tokenData, 'your-secret-key'); // 請使用環境變數存儲密鑰
      
      customer.value = {
        ...data,
        customer_id: data.customer_id
      };
      token.value = newToken;
      expireAt.value = Date.now() + 30 * 60 * 1000; // 30 分鐘有效
      
      localStorage.setItem('customer', JSON.stringify(customer.value));
      localStorage.setItem('customer_token', newToken);
      localStorage.setItem('customer_expire_at', expireAt.value);
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
    setCustomer(null);
  }

  // 初始化時從 localStorage 載入資料
  function init() {
    const storedCustomer = localStorage.getItem('customer');
    const storedToken = localStorage.getItem('customer_token');
    const storedExpireAt = localStorage.getItem('customer_expire_at');
    
    if (storedCustomer && storedToken && storedExpireAt) {
      try {
        // 驗證令牌
        const decoded = jwt.verify(storedToken, 'your-secret-key');
        if (decoded.exp * 1000 > Date.now()) {
          customer.value = JSON.parse(storedCustomer);
          token.value = storedToken;
          expireAt.value = parseInt(storedExpireAt);
        } else {
          setCustomer(null);
        }
      } catch (error) {
        console.error('令牌驗證失敗：', error);
        setCustomer(null);
      }
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
