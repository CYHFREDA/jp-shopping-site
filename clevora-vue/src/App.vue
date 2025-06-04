<script setup>
import { onMounted } from 'vue';
import { clearCache } from './utils/cache';
import NavBar from '@/components/NavBar.vue';
import { useCartStore } from '@/stores/cartStore';
import { useCustomerStore } from '@/stores/customerStore';
import { useRoute } from 'vue-router';

const route = useRoute();
const cartStore = useCartStore();
const customerStore = useCustomerStore();

// 在應用啟動時初始化緩存清理和載入購物車
onMounted(() => {
  clearCache.init();
  cartStore.loadCart();
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
