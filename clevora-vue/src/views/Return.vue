<template>
  <div class="return-page d-flex align-items-center justify-content-center py-5">
    <div class="card bg-white p-4 p-md-5 shadow-lg text-center">
      <div class="icon-container mb-4">
        <i :class="iconClass"></i>
      </div>
      <h1 class="mb-3">{{ message }}</h1>
      <p v-if="subMessage" class="text-muted mb-4">{{ subMessage }}</p>
      <button @click="goHome" class="btn btn-primary btn-lg">返回Clevora首頁</button>
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

  // 假設金流服務回傳一個參數 `RtnCode` 表示結果，`1` 為成功，其他為失敗
  const rtnCode = queryParams.RtnCode;
  const rtnMsg = queryParams.RtnMsg;
  
  if (rtnCode === '1') { // 假設 1 表示成功 (綠界)
    message.value = '付款成功！';
    subMessage.value = '感謝您的訂購。您的訂單已成立。';
    status.value = 'success';
    cartStore.clearCart(); // 支付成功則清空購物車
    
    // TODO: 可能需要呼叫後端 API 來最終確認訂單狀態
    // 例如：fetch('/api/confirm-order', { method: 'POST', body: JSON.stringify(queryParams) });

  } else { // 處理失敗或其他情況
    message.value = '付款失敗！';
    // 顯示金流回傳的錯誤訊息，如果沒有則顯示預設訊息
    subMessage.value = rtnMsg || '請檢查您的支付資訊或聯繫客服。'; 
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
.return-page {
  background-color: #f0f2f5; /* 淺灰色背景 */
  min-height: calc(100vh - var(--navbar-height, 0px) - var(--footer-height, 0px)); /* 考慮 NavBar 和 Footer 高度 */
  padding: 20px;
}

.card {
  border-radius: 16px; /* 更圓潤的邊角 */
  /* box-shadow: 0 4px 12px rgba(0,0,0,0.1); */ /* 使用 Bootstrap 的 shadow-lg */
  max-width: 450px; /* 稍微放寬最大寬度 */
  width: 90%;
}

.icon-container {
  font-size: 72px; /* 加大圖標尺寸 */
  margin-bottom: 24px; /* 增加圖標下方的間距 */
}

.check-icon {
  color: #28a745; /* Bootstrap success color */
  animation: scaleAndFadeIn 0.8s ease-out;
}

.fail-icon {
  color: #dc3545; /* Bootstrap danger color */
  animation: shake 0.5s ease-in-out, scaleAndFadeIn 0.8s ease-out;
}

.fa-spinner {
  color: #0d6efd; /* Bootstrap primary color */
  animation: spin 1.5s linear infinite;
}

@keyframes scaleAndFadeIn {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-8px); }
  40%, 80% { transform: translateX(8px); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

h1 {
  margin-top: 0; /* 移除默認的 margin-top */
  margin-bottom: 12px; /* 增加標題下方的間距 */
  font-size: 1.8rem; /* 加大標題字體 */
  color: #333; /* 預設文字顏色 */
}

.check-icon ~ h1 {
  color: #28a745; /* 成功時標題顏色 */
}

.fail-icon ~ h1 {
  color: #dc3545; /* 失敗時標題顏色 */
}

p {
  color: #555; /* 子訊息文字顏色 */
  margin-bottom: 30px; /* 增加子訊息下方的間距 */
  font-size: 1.1rem;
}

.btn-primary {
  padding: 12px 30px; /* 加大按鈕內邊距 */
  font-size: 1.1rem; /* 加大按鈕字體 */
  border-radius: 8px; /* 圓潤按鈕邊角 */
  transition: all 0.3s ease; /* 添加過渡效果 */
}

.btn-primary:hover {
  transform: translateY(-3px); /* 滑鼠懸停時上移 */
  box-shadow: 0 6px 12px rgba(0,0,0,0.2); /* 滑鼠懸停時陰影變大 */
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