<template>
  <nav class="admin-header navbar navbar-expand-lg">
    <div class="container-fluid">
      <router-link to="/admin" class="navbar-brand">
        <img src="/images/LOGO.png" alt="Clevora Logo" class="admin-logo me-2">
        後台管理
      </router-link>
      <div class="d-flex">
        <!-- 您可以在這裡添加其他後台相關的導航項目或資訊，例如登出按鈕等 -->
        <!-- 例如：<button @click="logout" class="btn btn-outline-light">登出</button> -->
      </div>
    </div>
  </nav>
</template>

<script setup>
// 如果需要任何邏輯（例如登出功能），可以在這裡添加
// import { useRouter } from 'vue-router';
// import { useUserStore } from '@/stores/userStore';

// const router = useRouter();
// const userStore = useUserStore();

// const logout = () => {
//   userStore.logout();
//   router.push('/admin/login');
// };
</script>

<style scoped>
/* 使用新的棕色調 */
:root {
  --dark-brown: #38302e; /* 深棕色 */
  --light-brown: #a18a7b; /* 淺棕色/米色 */
  --white: #ffffff; /* 白色 */
  --light-grey: #f8f9fa; /* 淺灰色，用於背景或邊框 */
  --medium-grey: #e9ecef; /* 中等灰色 */
  --accent-brown: #c8a99a; /* 介於深淺之間的強調棕色 */
}

.admin-header {
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  background-color: var(--dark-brown) !important; /* 深棕色背景 */
  border-bottom: 1px solid var(--light-brown); /* 底部邊框 */
}

.navbar-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--white) !important; /* 白色文字 */
  display: flex; /* 使 Logo 和文字對齊 */
  align-items: center; /* 垂直居中對齊 */
}

.admin-logo {
  height: 30px; /* 您可以根據需要調整 Logo 的高度 */
  vertical-align: middle;
  margin-right: 0.5rem; /* 添加 Logo 與文字間距 */
}
</style> 