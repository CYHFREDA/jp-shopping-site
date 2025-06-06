<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { clearCache } from './utils/cache';
import NavBar from '@/components/NavBar.vue';
import { useCartStore } from '@/stores/cartStore';
import { useCustomerStore } from '@/stores/customerStore';
import { useUserStore } from '@/stores/userStore';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const cartStore = useCartStore();
const customerStore = useCustomerStore();
const userStore = useUserStore();

// 返回頂部按鈕
const showBackToTop = ref(false);
function handleScroll() {
  showBackToTop.value = window.scrollY > 300;
}
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

const showInactivityAlert = ref(false);
const inactivityType = ref('customer');

function handleInactivityLogout(e) {
  inactivityType.value = e.detail?.type || 'customer';
  showInactivityAlert.value = true;
}

// 在應用啟動時初始化緩存清理、載入購物車，並設定自動登出計時器
onMounted(() => {
  clearCache.init();
  cartStore.loadCart();
  window.addEventListener('scroll', handleScroll);
  window.addEventListener('inactivity-logout', handleInactivityLogout);
});

// 在組件卸載時清除事件監聽器
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('inactivity-logout', handleInactivityLogout);
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
    <button v-if="showBackToTop" class="back-to-top-btn" @click="scrollToTop" aria-label="返回最上面">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="12" fill="#a18a7b"/>
        <path d="M12 8L8 12H11V16H13V12H16L12 8Z" fill="white"/>
      </svg>
    </button>
    <div v-if="showInactivityAlert" class="inactivity-alert">
      <span>⏰ 已閒置 30 分鐘，自動登出！請重新登入。</span>
      <button class="inactivity-confirm-btn" @click="showInactivityAlert = false">確認</button>
    </div>
  </div>
</template>

<style>
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

.back-to-top-btn {
  position: fixed;
  right: 32px;
  bottom: 48px;
  z-index: 9999;
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 50%;
  background: #a18a7b;
  box-shadow: 0 2px 8px rgba(56,48,46,0.13);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
  opacity: 0.92;
}
.back-to-top-btn:hover {
  background: #38302e;
  box-shadow: 0 4px 16px rgba(56,48,46,0.18);
  transform: translateY(-4px) scale(1.08);
  opacity: 1;
}
@media (max-width: 768px) {
  .back-to-top-btn {
    right: 16px;
    bottom: 24px;
    width: 44px;
    height: 44px;
  }
  .back-to-top-btn svg {
    width: 22px;
    height: 22px;
  }
}

.inactivity-alert {
  position: fixed;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  background: #a18a7b;
  color: #fff;
  padding: 18px 32px;
  border-radius: 32px;
  font-size: 1.1rem;
  box-shadow: 0 4px 16px rgba(161,138,123,0.18);
  z-index: 9999;
  animation: fadeInUp 0.4s;
  display: flex;
  align-items: center;
  gap: 16px;
}
.inactivity-confirm-btn {
  margin-left: 16px;
  padding: 6px 22px;
  background: #fff;
  color: #a18a7b;
  border: none;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(56,48,46,0.10);
}
.inactivity-confirm-btn:hover {
  background: #38302e;
  color: #fff;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
