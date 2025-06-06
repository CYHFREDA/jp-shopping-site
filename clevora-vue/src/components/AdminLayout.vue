<template>
  <div class="admin-layout d-flex">
    <!-- 側邊欄 -->
    <div class="sidebar d-flex flex-column flex-shrink-0 p-3 bg-light" style="width: 220px; min-height: 100vh;">
      <a href="/admin" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-dark text-decoration-none">
        <img src="/images/LOGO.png" alt="LOGO" style="height: 40px; margin-right: 8px;" />
        <span class="fs-5 fw-bold">Clevora 後台</span>
      </a>
      <hr />
      <ul class="nav nav-pills flex-column mb-auto mt-2">
        <li v-for="item in menu" :key="item.name" class="nav-item">
          <router-link :to="item.path" class="nav-link" :class="{ active: $route.name === item.name }">
            <i :class="item.icon" style="margin-right: 8px;"></i>{{ item.label }}
          </router-link>
        </li>
      </ul>
      <div class="mt-auto">
        <router-link to="/" class="btn btn-outline-secondary btn-sm w-100 mb-2" style="font-weight:bold;">
          <i class="bi bi-house-door" style="margin-right: 6px;"></i>返回Clevora首頁
        </router-link>
        <button class="btn btn-outline-danger btn-sm w-100" @click="handleLogout">登出</button>
      </div>
    </div>
    <!-- 主內容 -->
    <div class="flex-grow-1 p-4 main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const menu = [
  { name: 'AdminDashboard', label: '首頁總覽', path: '/admin', icon: 'bi bi-bar-chart' },
  { name: 'AdminProducts', label: '商品管理', path: '/admin/products', icon: 'bi bi-box-seam' },
  { name: 'AdminOrders', label: '訂單管理', path: '/admin/orders', icon: 'bi bi-receipt' },
  { name: 'AdminShipments', label: '出貨管理', path: '/admin/shipments', icon: 'bi bi-truck' },
  { name: 'AdminCustomers', label: '客戶管理', path: '/admin/customers', icon: 'bi bi-people' },
  { name: 'AdminAdmins', label: '管理員管理', path: '/admin/admins', icon: 'bi bi-person-badge' },
  { name: 'AdminSettings', label: '系統設定', path: '/admin/settings', icon: 'bi bi-gear' },
]

function handleLogout() {
  if (confirm('確定要登出嗎？')) {
    userStore.logout('manual')
    router.push('/admin/login')
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f8f9fa;
}
.sidebar {
  background: #f8f9fa;
  border-right: 1px solid #e9ecef;
}
.nav-link.active {
  background: #a18a7b !important;
  color: #fff !important;
}
.nav-link {
  color: #38302e;
}
.nav-link:hover {
  background: #c8a99a !important;
  color: #fff !important;
}
.main-content {
  min-width: 0;
}
</style> 