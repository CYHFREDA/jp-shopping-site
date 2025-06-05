<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-warning border-bottom shadow-sm">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold d-flex align-items-center" href="/">
        <img src="/images/LOGO.png" alt="LOGO" class="me-2" />
        <span>Clevora 首頁</span>
      </a>
      <button class="btn btn-danger btn-sm" @click="handleLogout">登出</button>
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
.navbar {
  padding: 0.5rem 1rem;
}

.navbar-brand img {
  height: 40px;
}
</style> 