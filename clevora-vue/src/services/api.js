import axios from 'axios';
import { useCustomerStore } from '@/stores/customerStore';
import { useUserStore } from '@/stores/userStore';

const api = axios.create({
  baseURL: '/',
  timeout: 10000
});

// 請求攔截器
api.interceptors.request.use(
  config => {
    const customerStore = useCustomerStore();
    const userStore = useUserStore();

    // 優先使用管理員令牌（如果存在且已認證）
    if (userStore.isAuthenticated) {
      config.headers.Authorization = `Bearer ${userStore.admin_token}`;
    }
    // 否則檢查客戶令牌（如果存在且已認證）
    else if (customerStore.isAuthenticated) {
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
      
      // 如果是管理員請求返回 401，清除管理員登錄狀態
      if (error.config.url.startsWith('/api/admin')) {
        userStore.logout();
      } else {
        // 如果是客戶請求返回 401，清除客戶登錄狀態
        customerStore.logout();
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
  getCustomerOrders(customerId) {
    return api.get(`/api/customers/${customerId}/orders`);
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