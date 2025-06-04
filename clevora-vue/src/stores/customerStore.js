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
    localStorage.setItem('customer', JSON.stringify(userData));
    localStorage.setItem('customer_token', authToken);
    localStorage.setItem('customer_expire_at', expireTime);
  }

  function logout() {
    customer.value = null;
    token.value = '';
    expireAt.value = '';
    localStorage.removeItem('customer');
    localStorage.removeItem('customer_token');
    localStorage.removeItem('customer_expire_at');
  }

  function init() {
    const storedCustomer = localStorage.getItem('customer');
    const storedToken = localStorage.getItem('customer_token');
    const storedExpireAt = localStorage.getItem('customer_expire_at');

    if (storedCustomer && storedToken && storedExpireAt) {
      try {
        const expireTime = parseInt(storedExpireAt);
        let parsedCustomer = null;

        try {
          parsedCustomer = JSON.parse(storedCustomer);
        } catch (parseError) {
          console.error('解析本地儲存的 customer 資料錯誤：', parseError);
          logout(); // ❗改用 logout 清除資料
          return;
        }

        if (expireTime > Date.now() && parsedCustomer) {
          customer.value = parsedCustomer;
          token.value = storedToken;
          expireAt.value = expireTime;
          console.log('✅ 從本地儲存成功載入用戶資料和 token');
        } else {
          console.log('⚠️ Token 已過期或客戶資料無效');
          logout(); // ❗改用 logout 清除
        }
      } catch (error) {
        console.error('🚫 載入本地儲存資料錯誤：', error);
        logout(); // ❗改用 logout 清除
      }
    } else {
      console.log('📭 本地儲存沒有登入資訊');
    }
  }

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
