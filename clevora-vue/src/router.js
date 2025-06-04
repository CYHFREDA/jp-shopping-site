import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import AdminLogin from './views/admin/Login.vue';
import AdminDashboard from './views/admin/Dashboard.vue';
import Products from './views/admin/Products.vue';
import Orders from './views/admin/Orders.vue';
import Cart from './views/Cart.vue';
import CustomerAuth from './views/CustomerAuth.vue';
import Return from './views/Return.vue';
import { useCustomerStore } from './stores/customerStore';

const routes = [
  { 
    path: '/', 
    component: Home 
  },
  {
    path: '/cart',
    component: Cart
  },
  {
    path: '/login',
    component: CustomerAuth
  },
  {
    path: '/pay/return',
    component: Return
  },
  { 
    path: '/admin/login', 
    component: AdminLogin 
  },
  { 
    path: '/admin', 
    component: AdminDashboard,
    meta: { requiresAuth: true },
    children: [
      { 
        path: 'products', 
        component: Products 
      },
      { 
        path: 'orders', 
        component: Orders 
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守衛
router.beforeEach((to, from, next) => {
  // 設定頁面標題
  document.title = 'Clevora';

  const customerStore = useCustomerStore(); // 獲取 customerStore 實例

  // 如果用戶已登入且嘗試訪問登入頁面，則重定向到首頁
  if (to.path === '/login' && customerStore.isAuthenticated) {
    console.log('已登入用戶嘗試訪問登入頁面，重定向到首頁。');
    next('/');
    return;
  }

  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('basic_token');
    const expireAt = localStorage.getItem('expire_at');
    if (!token || !expireAt || Date.now() > parseInt(expireAt)) {
      next('/admin/login');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;