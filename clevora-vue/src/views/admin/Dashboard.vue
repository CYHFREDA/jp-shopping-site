<template>
  <div>
    <!-- 導覽列 -->
    <AdminNavbar />

    <!-- 主要內容區域 -->
    <div class="container mt-4">
      <!-- 上方橫向選單 -->
      <ul class="nav nav-tabs mb-3">
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/orders" active-class="active">📦 訂單管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/shipments" active-class="active">🚚 出貨管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/customers" active-class="active">👥 客戶管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/products" active-class="active">🛍️ 商品管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/admins" active-class="active">👤 使用者管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/settings" active-class="active">⚙️ 系統設定</router-link>
        </li>
      </ul>

      <!-- 路由視圖 -->
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import AdminNavbar from '@/components/AdminNavbar.vue';

const router = useRouter();
const userStore = useUserStore();

function handleLogout() {
  if (confirm('確定要登出嗎？')) {
    userStore.logout();
    router.push('/admin/login');
  }
}
</script>

<style scoped>
.navbar {
  padding: 0.5rem 1rem;
}

.navbar-brand img {
  height: 40px;
}

.nav-tabs .nav-link {
  color: #6c757d;
  border: none;
  padding: 0.75rem 1.25rem;
  margin-right: 0.5rem;
  transition: color 0.3s ease;
}

.nav-tabs .nav-link.active {
  color: #007bff;
  border-bottom: 2px solid #007bff;
  background-color: #e9ecef;
  font-weight: bold;
  transition: all 0.3s ease;
}

.nav-tabs .nav-link:hover {
  color: #0056b3;
  background-color: #f8f9fa;
  border-color: transparent;
}
</style> 