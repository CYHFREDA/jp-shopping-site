// router.js
import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import { useCustomerStore } from '@/stores/customerStore';

// 靜態導入常用頁面
import Home from '@/views/Home.vue';
import Cart from '@/views/Cart.vue';
import CustomerAuth from '@/views/CustomerAuth.vue';
import Return from '@/views/Return.vue';
import OrderHistory from '@/views/OrderHistory.vue';
import AdminLogin from '@/views/admin/Login.vue';
import AdminDashboard from '@/views/admin/Dashboard.vue';
import Products from '@/views/admin/Products.vue';
import Orders from '@/views/admin/Orders.vue';
import Shipments from '@/views/admin/Shipments.vue';
import Customers from '@/views/admin/Customers.vue';
import AdminUsers from '@/views/admin/Admins.vue';
import Settings from '@/views/admin/Settings.vue';
import NotFound from '@/views/ErrorPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Clevora 日本代購' }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: Cart,
    meta: { title: 'Clevora 購物車' }
  },
  {
    path: '/login',
    name: 'CustomerAuth',
    component: CustomerAuth,
    meta: { title: 'Clevora 會員登入 / 註冊' }
  },
  {
    path: '/pay/return',
    name: 'PaymentReturn',
    component: Return,
    meta: { title: 'Clevora 付款結果' }
  },
  {
    path: '/orderHistory',
    name: 'OrderHistory',
    component: OrderHistory,
    meta: {
      title: 'Clevora 我的訂單',
      requiresCustomerAuth: true
    }
  },
  {
    path: '/admin/login',
    name: 'AdminAuth',
    component: AdminLogin,
    meta: { title: 'Clevora 後台管理登入' }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: {
      requiresAuth: true,
      title: 'Clevora 後台管理 - 主控台'
    },
    children: [
      {
        path: '',
        redirect: 'orders'
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: Products,
        meta: { title: 'Clevora 後台管理 - 商品管理' }
      },
      {
        path: 'orders',
        name: 'AdminOrders',
        component: Orders,
        meta: { title: 'Clevora 後台管理 - 訂單管理' }
      },
      {
        path: 'shipments',
        name: 'AdminShipments',
        component: Shipments,
        meta: { title: 'Clevora 後台管理 - 出貨管理' }
      },
      {
        path: 'customers',
        name: 'AdminCustomers',
        component: Customers,
        meta: { title: 'Clevora 後台管理 - 客戶管理' }
      },
      {
        path: 'admins',
        name: 'AdminAdmins',
        component: AdminUsers,
        meta: { title: 'Clevora 後台管理 - 使用者管理' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: Settings,
        meta: { title: 'Clevora 後台管理 - 系統設定' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: 'Clevora 發生錯誤' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守衛
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const customerStore = useCustomerStore();

  const isAdminAuthenticated = userStore.isAuthenticated;
  const isCustomerAuthenticated = customerStore.isAuthenticated;

  if (to.meta.requiresAuth && !isAdminAuthenticated) {
    next('/admin/login');
  } else if (to.meta.requiresCustomerAuth && !isCustomerAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } });
  } else {
    document.title = to.meta.title ? to.meta.title : 'Clevora';
    next();
  }
});

export default router;