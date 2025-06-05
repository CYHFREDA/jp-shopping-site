<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-warning border-bottom shadow-sm">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold d-flex align-items-center" href="/">
        <img src="/images/LOGO.png" alt="LOGO" class="me-2" />
        <span>Clevora 首頁</span>
      </a>
      <button v-if="userStore.admin_token" class="btn btn-danger btn-sm" @click="handleLogout">登出</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';

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
  --accent-brown: #c8a99a; /* 介於深淺之間的強調棕色 */
}

.navbar {
  padding: 0.5rem 1rem;
  background-color: var(--dark-brown) !important; /* 導航列背景色 */
  border-bottom: 1px solid var(--light-brown); /* 底部邊框 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 微妙陰影 */
}

.navbar-brand {
  color: var(--white) !important; /* 品牌文字顏色 */
  font-weight: bold;
}

.navbar-brand:hover {
  color: var(--light-brown) !important; /* 懸停時顏色 */
}

.navbar-brand img {
  height: 40px;
  /* 可能需要調整 LOGO 在深色背景下的可見性 */
}

/* 登出按鈕樣式 */
.btn-danger {
  background-color: var(--light-brown); /* 按鈕背景色 */
  border-color: var(--light-brown); /* 按鈕邊框顏色 */
  color: var(--dark-brown); /* 按鈕文字顏色 */
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, color 0.15s ease-in-out;
}

.btn-danger:hover {
  background-color: var(--accent-brown); /* 懸停背景色 */
  border-color: var(--accent-brown); /* 懸停邊框顏色 */
  color: var(--white); /* 懸停文字顏色 */
}
</style> 