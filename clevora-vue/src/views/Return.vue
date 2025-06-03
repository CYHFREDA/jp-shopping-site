<template>
  <div class="return-page">
    <div class="card bg-white">
      <div class="icon-container mb-3">
        <i :class="iconClass"></i>
      </div>
      <h1>{{ message }}</h1>
      <p v-if="subMessage">{{ subMessage }}</p>
      <button @click="goHome" class="btn btn-primary">返回Clevora首頁</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCartStore } from '@/stores/cartStore';

const route = useRoute();
const router = useRouter();
const cartStore = useCartStore();

const message = ref('處理中...');
const subMessage = ref('');
const status = ref('processing'); // possible values: 'processing', 'success', 'failed'

const iconClass = computed(() => {
  if (status.value === 'success') return 'fas fa-check-circle check-icon';
  if (status.value === 'failed') return 'fas fa-times-circle fail-icon';
  return 'fas fa-spinner fa-spin'; // 處理中的圖標
});

// TODO: 根據金流服務的回傳參數解析支付結果
// 這是一個示意性的函數，你需要根據實際的金流服務回傳格式來實作
async function processPaymentResult() {
  const queryParams = route.query; // 獲取 URL 中的查詢參數
  console.log('支付回傳參數：', queryParams);

  // 假設金流服務回傳一個參數 `RtnCode` 表示結果，0 為成功，其他為失敗
  const rtnCode = queryParams.RtnCode;
  
  if (rtnCode === '1') { // 假設 1 表示成功 (綠界)
    message.value = '付款成功！';
    subMessage.value = '感謝您的訂購。您的訂單已成立。';
    status.value = 'success';
    cartStore.clearCart(); // 支付成功則清空購物車
    
    // TODO: 可能需要呼叫後端 API 來最終確認訂單狀態
    // 例如：fetch('/api/confirm-order', { method: 'POST', body: JSON.stringify(queryParams) });

  } else { // 處理失敗或其他情況
    message.value = '付款失敗！';
    subMessage.value = queryParams.RtnMsg || '請檢查您的支付資訊或聯繫客服。'; // 顯示金流回傳的錯誤訊息
    status.value = 'failed';
  }
}

function goHome() {
  router.push('/');
}

onMounted(() => {
  processPaymentResult();
});
</script>

<style scoped>
/* 可以在這裡添加 Return.vue 特有的樣式 */
.return-page {
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
  max-width: 400px;
  width: 90%;
}

.icon-container {
  font-size: 64px;
}

.check-icon {
  color: #28a745; /* Bootstrap success color */
  animation: pop 0.6s ease;
}

.fail-icon {
  color: #dc3545; /* Bootstrap danger color */
  animation: pop 0.6s ease;
}

.fa-spinner {
  color: #0d6efd; /* Bootstrap primary color */
}

@keyframes pop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); }
}

h1 {
  margin-top: 20px;
  /* 標題顏色根據狀態變化 */
  color: #28a745; /* default success */
}

.fail-icon ~ h1 {
  color: #dc3545; /* if failed */
}

p {
  color: #555;
  margin-bottom: 30px;
}

.btn-primary {
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.btn-primary:hover {
  transform: translateY(-2px);
}

/* 確保頁面內容不會被 NavBar 和 Footer 遮擋 */
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
</style> 