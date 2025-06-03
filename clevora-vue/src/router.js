import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import AdminLogin from './views/admin/Login.vue';
import AdminDashboard from './views/admin/Dashboard.vue';
import Products from './views/admin/Products.vue';
import Orders from './views/admin/Orders.vue';
import Cart from './views/Cart.vue';
import CustomerAuth from './views/CustomerAuth.vue';

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