import { createRouter, createWebHistory } from 'vue-router';
import OrderHistory from '@/views/OrderHistory.vue'; 
import Shipments from '@/views/admin/Shipments.vue';
import Customers from '@/views/admin/Customers.vue';
import Admins from '@/views/admin/Admins.vue'; 
import Settings from '@/views/admin/Settings.vue'; 
import { useUserStore } from '@/stores/userStore';
import { useCustomerStore } from '@/stores/customerStore';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: 'Clevora 日本代購' }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/views/Cart.vue'),
    meta: { title: 'Clevora 購物車' }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('@/views/ProductDetail.vue'),
    meta: { title: 'Clevora 商品詳細' }
  },
  {
    path: '/login',
    name: 'CustomerAuth',
    component: () => import('@/views/CustomerAuth.vue'),
    meta: { title: 'Clevora 會員登入 / 註冊' }
  },
  {
    path: '/checkout/return',
    name: 'PaymentReturn',
    component: () => import('@/views/Return.vue'),
    meta: { title: 'Clevora 付款結果' }
  },
  {
    path: '/admin/login',
    name: 'AdminAuth',
    component: () => import('@/views/admin/Login.vue'),
    meta: { title: 'Clevora 後台管理登入' }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      title: 'Clevora 後台管理 - 主控台'
    },
    children: [
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import('@/views/admin/Products.vue'),
        meta: { title: 'Clevora 後台管理 - 商品管理' }
      },
      {
        path: 'orders',
        name: 'AdminOrders',
        component: () => import('@/views/admin/Orders.vue'),
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
        component: () => import('@/views/admin/Admins.vue'),
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
    path: '/orderHistory',
    name: 'OrderHistory',
    component: OrderHistory,
    meta: { 
      title: 'Clevora 我的訂單',
      requiresCustomerAuth: true
    }
  }
];

// 捕獲所有未匹配的路由
const notFoundRoute = {
  path: '/:pathMatch(.*)*',
  name: 'NotFound',
  component: () => import('@/views/ErrorPage.vue'),
  meta: { title: 'Clevora 發生錯誤' }
};

routes.push(notFoundRoute);

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