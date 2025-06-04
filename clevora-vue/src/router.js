import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import AdminLogin from './views/admin/Login.vue';
import AdminDashboard from './views/admin/Dashboard.vue';
import Products from './views/admin/Products.vue';
import Orders from './views/admin/Orders.vue';
import Shipments from './views/admin/Shipments.vue';
import Customers from './views/admin/Customers.vue';
import AdminUsers from './views/admin/Admins.vue';
import Cart from './views/Cart.vue';
import CustomerAuth from './views/CustomerAuth.vue';
import Return from './views/Return.vue';
import OrderHistory from './views/OrderHistory.vue';
import { useCustomerStore } from './stores/customerStore';
import { useUserStore } from './stores/userStore';

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
    path: '/orderHistory',
    component: OrderHistory,
    meta: { requiresCustomerAuth: true }
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
        path: '', // 當路徑為 /admin 時，預設重定向到 orders
        redirect: 'orders'
      },
      { 
        path: 'products', 
        component: Products 
      },
      { 
        path: 'orders', 
        component: Orders 
      },
      { 
        path: 'shipments', 
        component: Shipments 
      },
      { 
        path: 'customers', 
        component: Customers 
      },
      { 
        path: 'admin_users', 
        component: AdminUsers 
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
  const userStore = useUserStore(); // 獲取 userStore 實例

  // 如果用戶已登入且嘗試訪問登入頁面，則重定向到首頁
  if (to.path === '/login' && customerStore.isAuthenticated) {
    console.log('已登入用戶嘗試訪問登入頁面，重定向到首頁。');
    next('/');
    return;
  }

  // 新增客戶登入驗證
  if (to.meta.requiresCustomerAuth && !customerStore.isAuthenticated) {
    console.log('未登入客戶嘗試訪問需要客戶登入的頁面，重定向到登入頁。');
    localStorage.setItem('redirectAfterLogin', to.fullPath); // 儲存目標路徑，登入後可跳回
    next('/login');
    return;
  }

  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      next('/admin/login');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;