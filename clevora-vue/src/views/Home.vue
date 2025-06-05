<template>
  <div>
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container d-flex flex-column justify-content-center align-items-center text-center">
        <h1 class="hero-title">探索日本好物，盡在 Clevora</h1>
        <p class="hero-subtitle">我們為您精選最新、最熱門的日本商品</p>
        <router-link to="/products" class="btn btn-lg btn-light-brown mt-3">立即選購</router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { useCartStore } from '@/stores/cartStore';
import { useCustomerStore } from '@/stores/customerStore';
import { useRoute, useRouter } from 'vue-router';

// 這些變數現在只與英雄區塊相關
const router = useRouter();

</script>

<style scoped>
/* 英雄區域樣式 */
.hero-section {
  background: linear-gradient(rgba(56, 48, 46, 0.7), rgba(56, 48, 46, 0.7)), url('/images/hero-bg.jpg'); /* 深棕色半透明疊加圖片背景 */
  background-size: cover;
  background-position: center;
  color: var(--white); /* 白色文字 */
  padding: 80px 15px; /* 內邊距 */
  margin-bottom: 2rem; /* 底部間距 */
  min-height: 400px; /* 最小高度 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
}

.btn-light-brown {
  background-color: var(--light-brown);
  border-color: var(--light-brown);
  color: var(--white);
  font-weight: bold;
  padding: 12px 30px;
  border-radius: 30px;
  transition: all 0.3s ease;
}

.btn-light-brown:hover {
  background-color: var(--accent-brown);
  border-color: var(--accent-brown);
}

/* RWD 調整 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  .hero-subtitle {
    font-size: 1rem;
  }
}

@media (max-width: 576px) {
  .hero-title {
    font-size: 2rem;
  }
  .hero-subtitle {
    font-size: 0.9rem;
  }
}
</style>
