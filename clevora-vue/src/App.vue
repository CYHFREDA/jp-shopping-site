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
    <footer class="mt-5">
      <div class="container">
        <div class="row">
          <div class="col-12">
            &copy; 2025 Clevora 日本代購
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
body {
  background-color: #f8f9fa;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

footer {
  margin-top: auto;
}
</style>
