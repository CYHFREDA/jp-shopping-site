<template>
  <div>
    <!-- 導覽列 -->
     <nav class="navbar navbar-expand-lg navbar-light bg-warning border-bottom shadow-sm">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold d-flex align-items-center" href="/">
          <img src="/images/LOGO.png" alt="LOGO" class="me-2" />
          <span>Clevora 後台管理</span>
        </a>
        <button class="btn btn-danger btn-sm" @click="handleLogout">登出</button>
      </div>
    </nav>

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
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';

const router = useRouter();
const userStore = useUserStore();

onMounted(() => {
  const adminToken = localStorage.getItem('admin_token');
  if (!adminToken) {
    router.push('/admin/login');
  }
});

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
  color: #495057;
  border: none;
  padding: 0.5rem 1rem;
  margin-right: 0.5rem;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-bottom: 2px solid #0d6efd;
  background: none;
}

.nav-tabs .nav-link:hover {
  border-color: transparent;
  color: #0d6efd;
}
</style> 