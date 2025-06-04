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

// 根據訂單狀態更新頁面顯示
function updatePageBasedOnStatus(orderStatus) {
  if (orderStatus === 'success') {
    message.value = '付款成功！';
    subMessage.value = '感謝您的訂購。您的訂單已成立。';
    status.value = 'success';
    cartStore.clearCart(); // 支付成功則清空購物車
  } else if (orderStatus === 'fail') {
    message.value = '付款失敗！';
    subMessage.value = '請檢查您的支付資訊或聯繫客服。';
    status.value = 'failed';
  } else { // 其他狀態，例如 pending 或找不到訂單
    message.value = '訂單狀態查詢中...';
    subMessage.value = '';
    status.value = 'processing';
  }
}

function goHome() {
  router.push('/');
}

onMounted(async () => {
  // 從 localStorage 獲取 order_id
  const orderId = localStorage.getItem('latest_order_id');

  if (!orderId) {
    // 如果沒有找到 order_id，顯示錯誤或導回首頁
    message.value = '無法獲取訂單資訊！';
    subMessage.value = '請直接前往首頁查詢訂單狀態或聯繫客服。';
    status.value = 'failed';
    console.error('無法從 localStorage 獲取 order_id');
    return;
  }

  // 構建查詢訂單狀態的 API URL
  const apiUrl = `/orders/${orderId}/status`;
  console.log('查詢訂單狀態 API URL:', apiUrl);

  try {
    // 調用後端 API 查詢訂單狀態
    const res = await fetch(apiUrl);
    const data = await res.json();

    if (res.ok) {
      // 根據後端回傳的狀態更新頁面
      updatePageBasedOnStatus(data.status);
      // 清理 localStorage 中的 order_id
      localStorage.removeItem('latest_order_id');
    } else {
      // 處理 API 錯誤，例如訂單不存在
      console.error('查詢訂單狀態 API 錯誤：', data.error || res.statusText);
      message.value = '查詢訂單狀態失敗！';
      subMessage.value = data.error || '請稍後再試或聯繫客服。';
      status.value = 'failed';
    }

  } catch (error) {
    // 處理網路錯誤或其他異常
    console.error('調用查詢訂單狀態 API 時發生錯誤：', error);
    message.value = '連接錯誤！';
    subMessage.value = '無法查詢訂單狀態，請檢查網路或聯繫客服。';
    status.value = 'failed';
  }
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