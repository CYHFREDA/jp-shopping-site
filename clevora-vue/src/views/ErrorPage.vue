<template>
  <div class="error-page">
    <div class="card bg-white">
      <h1>發生錯誤</h1>
      <p>抱歉，您要查看的頁面目前無法使用。<br/>請稍後再試一次。</p>
      <p>如果您是系統管理員，請查看錯誤日誌以獲取詳細資訊。</p>
      <p><em>Faithfully yours.</em></p>
      <button @click="goHome" class="btn btn-primary mt-3">返回首頁</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

function goHome() {
  router.push('/');
}
</script>

<style scoped>
/* 可以在這裡添加 ErrorPage.vue 特有的樣式 */
.error-page {
  background-color: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - var(--navbar-height, 0px) - var(--footer-height, 0px)); /* 考慮 NavBar 和 Footer 高度 */
  padding: 20px;
}

.card {
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 500px;
  width: 90%;
}

h1 {
  font-size: 32px;
  color: #dc3545; /* Bootstrap danger color */
  margin-bottom: 20px;
}

p {
  color: #555;
  margin-bottom: 20px;
}

em {
  color: #888;
}

.btn-primary {
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.btn-primary:hover {
  transform: translateY(-2px);
}

/* Removed general layout styles that were moved to main.css */
/*
body {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

#app {
  flex: 1;
  display: flex;
  flex-direction: column;
}

main {
  flex-grow: 1;
}
*/
</style> 