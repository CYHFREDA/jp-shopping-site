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
/* 使用新的棕色調 */
:root {
  --dark-brown: #38302e; /* 深棕色 */
  --light-brown: #a18a7b; /* 淺棕色/米色 */
  --white: #ffffff; /* 白色 */
  --light-grey: #f8f9fa; /* 淺灰色，用於背景或邊框 */
  --medium-grey: #e9ecef; /* 中等灰色 */
}

.navbar {
  padding: 0.5rem 1rem;
}

.navbar-brand img {
  height: 40px;
}

.nav-tabs {
  border-bottom: 1px solid var(--light-brown); /* 調整底部邊框顏色 */
}

.nav-tabs .nav-link {
  color: var(--dark-brown); /* 非激活鏈接文字顏色 */
  border: none;
  padding: 0.75rem 1.25rem;
  margin-right: 0.5rem;
  transition: color 0.3s ease, background-color 0.3s ease;
}

.nav-tabs .nav-link.active {
  color: var(--white); /* 激活鏈接文字顏色 */
  border-bottom: 2px solid var(--light-brown); /* 激活底部邊框顏色 */
  background-color: var(--light-brown); /* 激活背景色 */
  font-weight: bold;
}

.nav-tabs .nav-link:hover {
  color: var(--light-brown); /* 懸停時文字顏色 */
  background-color: var(--light-grey); /* 懸停時淺色背景 */
  border-color: transparent;
}

/* 可以針對整個 Dashboard 容器添加一些基礎樣式 */
/* 例如：背景色、字體等 */
/* body { font-family: 'Arial', sans-serif; } */
/* .container { background-color: #fff; } */
</style> 