<template>
  <div class="error-page">
    <div class="card bg-white error-card">
      <h1 class="error-title">發生錯誤</h1>
      <p class="error-message">抱歉，您要查看的頁面目前無法使用。<br/>請稍後再試一次。</p>
      <p class="error-message">如果您是系統管理員，請查看錯誤日誌以獲取詳細資訊。</p>
      <p class="error-signature"><em>Faithfully yours.</em></p>
      <button @click="goHome" class="btn btn-primary mt-3 error-home-btn">返回首頁</button>
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
.error-page {
  background-color: var(--light-grey); /* 淺灰色背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 60px); /* 確保覆蓋視窗高度，扣除 footer 高度 */
  padding: 20px;
}

.error-card {
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 500px;
  width: 90%;
  background-color: var(--white); /* 白色背景 */
  border: 1px solid var(--medium-grey); /* 添加邊框 */
}

.error-title {
  font-size: 2.5rem; /* 調整字體大小 */
  color: var(--dark-brown); /* 標題使用深棕色 */
  margin-bottom: 20px;
  font-weight: bold;
}

.error-message {
  color: var(--dark-brown); /* 段落文字使用深棕色 */
  margin-bottom: 15px; /* 調整下方間距 */
  font-size: 1.1rem;
}

.error-signature {
  color: var(--disabled-text); /* 簽名字使用禁用文字顏色 */
  margin-bottom: 30px; /* 增加下方間距 */
  font-style: italic;
}

/* 返回首頁按鈕 - 應用 main.css 中的 .btn-primary 樣式 */
.error-home-btn {
  /* 繼承 main.css */
}

/* RWD 調整 */
@media (max-width: 576px) {
  .error-card {
    padding: 20px; /* 小螢幕調整內邊距 */
  }

  .error-title {
    font-size: 1.8rem; /* 小螢幕調整字體大小 */
  }

  .error-message {
    font-size: 1rem; /* 小螢幕調整字體大小 */
  }
}
</style> 