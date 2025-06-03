<script setup>
import { onMounted } from 'vue';
import { clearCache } from './utils/cache';
import NavBar from '@/components/NavBar.vue';
import { useCartStore } from '@/stores/cartStore';

const cartStore = useCartStore();

// 在應用啟動時初始化緩存清理和載入購物車
onMounted(() => {
  clearCache.init();
  cartStore.loadCart();
});
</script>

<template>
  <div class="app-container">
    <NavBar />
    <router-view></router-view>
    <footer class="mt-5">
      <div class="container">
        <div class="row">
          <div class="col-12">
            &copy; 2025 Clevora 日本代購商城管理系統
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
