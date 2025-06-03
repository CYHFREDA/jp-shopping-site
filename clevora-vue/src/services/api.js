import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 5000
});

// 請求攔截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('admin_token');
    if (token && config.url.startsWith('/admin')) {
      config.headers.Authorization = `Basic ${token}`;
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
    if (error.response?.status === 401 && error.config.url.startsWith('/admin')) {
      localStorage.removeItem('admin_token');
      alert('後台認證失敗，請重新登入！');
      window.location.href = '/admin/login';
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