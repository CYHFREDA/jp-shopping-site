<script setup>
import { onMounted, onUnmounted } from 'vue';
import { clearCache } from './utils/cache';
import NavBar from '@/components/NavBar.vue';
import { useCartStore } from '@/stores/cartStore';
import { useCustomerStore } from '@/stores/customerStore';
import { useRoute } from 'vue-router';

const route = useRoute();
const cartStore = useCartStore();
const customerStore = useCustomerStore();

let inactivityTimer;
const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 分鐘 (毫秒)

function resetInactivityTimer() {
  clearTimeout(inactivityTimer);
  if (customerStore.isAuthenticated) { // Only set timer if user is authenticated
    inactivityTimer = setTimeout(() => {
      console.log('使用者閒置，自動登出...');
      customerStore.logout();
      alert('已閒置30分鐘自動登出');
    }, INACTIVITY_TIMEOUT);
  }
}

function setupActivityListeners() {
  window.addEventListener('mousemove', resetInactivityTimer);
  window.addEventListener('keydown', resetInactivityTimer);
  window.addEventListener('click', resetInactivityTimer);
  window.addEventListener('scroll', resetInactivityTimer);
}

function removeActivityListeners() {
  clearTimeout(inactivityTimer);
  window.removeEventListener('mousemove', resetInactivityTimer);
  window.removeEventListener('keydown', resetInactivityTimer);
  window.removeEventListener('click', resetInactivityTimer);
  window.removeEventListener('scroll', resetInactivityTimer);
}

// 在應用啟動時初始化緩存清理、載入購物車，並設定自動登出計時器
onMounted(() => {
  clearCache.init();
  cartStore.loadCart();
  setupActivityListeners();
  resetInactivityTimer(); // Initial call to start the timer
});

// 在組件卸載時清除事件監聽器
onUnmounted(() => {
  removeActivityListeners();
});
</script>

<template>
  <div class="app-container">
    <NavBar v-if="!route.path.startsWith('/admin')" />
    <router-view></router-view>
    <footer class="app-footer">
      <div class="container">
        <div class="row">
          <div class="col-12 text-center">
            &copy; 2025 Clevora 日本代購
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
/* 使用新的棕色調 */
:root {
  --dark-brown: #38302e; /* 深棕色 */
  --light-brown: #a18a7b; /* 淺棕色/米色 */
  --white: #ffffff; /* 白色 */
  --light-grey: #f8f9fa; /* 淺灰色，用於背景或邊框 */
  --medium-grey: #e9ecef; /* 中等灰色 */
  --accent-brown: #c8a99a; /* 介於深淺之間的強調棕色 */
  --disabled-text: #6c757d; /* 用於禁用文字的顏色 */
}

body {
  background-color: var(--light-grey); /* 使用淺灰色背景，與其他頁面協調 */
  margin: 0;
  padding: 0;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.app-footer {
  margin-top: auto; /* 將 footer 推到底部 */
  padding: 20px 0; /* 內邊距 */
  background-color: var(--dark-brown); /* footer 背景色 */
  color: var(--white); /* footer 文字顏色 */
  text-align: center;
  font-size: 0.9rem;
  border-top: 1px solid var(--light-brown); /* 添加頂部邊框 */
}
</style>
