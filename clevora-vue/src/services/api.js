import axios from 'axios';
import { useCustomerStore } from '@/stores/customerStore';

const api = axios.create({
  baseURL: '/',
  timeout: 10000
});

// 請求攔截器
api.interceptors.request.use(
  config => {
    const customerStore = useCustomerStore();
    if (customerStore.isAuthenticated) {
      config.headers.Authorization = `Bearer ${customerStore.token}`;
    }
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
      const customerStore = useCustomerStore();
      customerStore.logout();
    }
    return Promise.reject(error);
  }
);

// 商品相關 API
export const productsAPI = {
  getProducts() {
    return api.get('/products');
  },
  addProduct(data) {
    return api.post('/products', data);
  },
  updateProduct(id, data) {
    return api.put(`/products/${id}`, data);
  },
  deleteProduct(id) {
    return api.delete(`/products/${id}`);
  }
};

// 訂單相關 API
export const ordersAPI = {
  getOrders() {
    return api.get('/orders');
  },
  updateOrder(id, data) {
    return api.put(`/orders/${id}`, data);
  }
};

// 會員相關 API
export const membersAPI = {
  getMembers() {
    return api.get('/members');
  },
  updateMember(id, data) {
    return api.put(`/members/${id}`, data);
  }
};

// 登入相關 API
export const authAPI = {
  login(credentials) {
    return api.post('/admin/login', credentials);
  },
  logout() {
    return api.post('/admin/logout');
  }
};

export default api; 