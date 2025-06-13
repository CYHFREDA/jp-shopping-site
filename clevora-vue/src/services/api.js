import axios from 'axios';
import { useCustomerStore } from '@/stores/customerStore';
import { useUserStore } from '@/stores/userStore';

const api = axios.create({
  baseURL: '/',
  timeout: 15000
});

// 請求攔截器
api.interceptors.request.use(
  config => {
    const customerStore = useCustomerStore();
    const userStore = useUserStore();

    // 優先使用管理員令牌（如果存在且已認證）
    if (config.url.startsWith('/api/admin') && userStore.isAuthenticated) {
      config.headers.Authorization = `Bearer ${userStore.admin_token}`;
    }
    // 否則使用客戶令牌（如果存在且已認證）
    else if (!config.url.startsWith('/api/admin') && customerStore.isAuthenticated) {
      config.headers.Authorization = `Bearer ${customerStore.token}`;
    }
    // 如果兩者都不存在，則不附加 Authorization 頭

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 響應攔截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      const userStore = useUserStore();
      const customerStore = useCustomerStore();
      const detail = error.response.data?.detail;
      
      // 處理「後踢前」
      if (detail === 'KICKED') {
        if (error.config.url.startsWith('/api/admin')) {
          userStore.logout('kicked');
          window.alert('您的管理員帳號已在其他地方登入，請重新登入。');
          window.location.href = '/admin/login';
        } else {
          customerStore.logout('kicked');
          window.alert('您的會員帳號已在其他地方登入，請重新登入。');
          window.location.href = '/login';
        }
      } 
      // 處理令牌過期
      else if (detail === '認證令牌已過期') {
        if (error.config.url.startsWith('/api/admin')) {
          userStore.logout('expired');
          window.alert('管理員登入已過期，請重新登入。');
          window.location.href = '/admin/login';
        } else {
          customerStore.logout('expired');
          window.alert('會員登入已過期，請重新登入。');
          window.location.href = '/login';
        }
      }
      // 處理其他 401 錯誤
      else {
        if (error.config.url.startsWith('/api/admin')) {
          userStore.logout('unauthorized');
        } else {
          customerStore.logout('unauthorized');
        }
      }
    }
    return Promise.reject(error);
  }
);

// 商品相關 API
export const productsAPI = {
  getProducts() {
    return api.get('/api/products');
  },
  addProduct(data) {
    return api.post('/api/products', data);
  },
  updateProduct(id, data) {
    return api.put(`/api/products/${id}`, data);
  },
  deleteProduct(id) {
    return api.delete(`/api/products/${id}`);
  }
};

// 訂單相關 API
export const ordersAPI = {
  getOrders() {
    return api.get('/api/orders');
  },
  updateOrder(id, data) {
    return api.put(`/api/orders/${id}`, data);
  },
  getCustomerOrders(customerId, page = 1, limit = 10) {
    return api.get(`/api/customers/${customerId}/orders`, {
      params: { page, limit }
    });
  }
};

// 會員相關 API
export const membersAPI = {
  getMembers() {
    return api.get('/api/members');
  },
  updateMember(id, data) {
    return api.put(`/api/members/${id}`, data);
  }
};

// 登入相關 API
export const authAPI = {
  login(credentials) {
    return api.post('/api/admin/login', credentials);
  },
  logout() {
    return api.post('/api/admin/logout');
  }
};

export default api; 