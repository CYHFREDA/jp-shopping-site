import { createRouter, createWebHistory } from 'vue-router';

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
      }
    ]
  },
  {
    path: '/orderHistory',
    name: 'OrderHistory',
    component: () => import('@/views/OrderHistory.vue'),
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
  const isAdminAuthenticated = localStorage.getItem('admin_token');
  const isCustomerAuthenticated = localStorage.getItem('customer_token');
  
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