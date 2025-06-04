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
        // 驗證令牌 - 前端只需檢查過期時間
        const expireTime = parseInt(storedExpireAt);

        // 添加對解析後的 customer 資料的檢查
        let parsedCustomer = null;
        try {
          parsedCustomer = JSON.parse(storedCustomer);
        } catch (parseError) {
          console.error('解析本地儲存的 customer 資料錯誤：', parseError);
          setCustomer(null, null, null); // 解析錯誤則清除本地儲存
          return; // 終止 init 函數執行
        }

        if (expireTime > Date.now() && parsedCustomer) { // 檢查token是否過期且customer資料存在
          customer.value = parsedCustomer;
          token.value = storedToken;
          expireAt.value = expireTime;
           console.log('從本地儲存成功載入用戶資料和token'); // 添加成功日誌
        } else {
          console.log('Token 已過期或本地儲存的 customer 資料無效'); // 調整日誌
          setCustomer(null, null, null); // Token 過期或資料無效則清除本地儲存
        }
      } catch (error) {
        console.error('載入本地儲存資料錯誤：', error);
        setCustomer(null, null, null); // 錯誤則清除本地儲存
      }
    } else {
       console.log('本地儲存無用戶資料或token');
       // 在這裡不需要 setCustomer(null, null, null)，因為初始值就是null
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
