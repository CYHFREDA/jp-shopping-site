<template>
  <nav class="admin-header navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
      <router-link to="/admin" class="navbar-brand">
        <img src="/images/logo.png" alt="Clevora Logo" class="admin-logo me-2">
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
.admin-header {
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  background-color: #343a40 !important; /* 深色背景 */
}

.navbar-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff; /* 白色文字 */
}

.admin-logo {
  height: 30px; /* 您可以根據需要調整 Logo 的高度 */
  vertical-align: middle;
}
</style> 