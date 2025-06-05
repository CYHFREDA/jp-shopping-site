<template>
  <div class="return-page d-flex align-items-center justify-content-center py-5">
    <div class="card bg-white p-4 p-md-5 shadow-lg text-center return-card">
      <div class="icon-container mb-4">
        <i :class="iconClass"></i>
      </div>
      <h1 class="mb-3 return-title">{{ message }}</h1>
      <p v-if="subMessage" class="text-muted mb-4 return-submessage">{{ subMessage }}</p>
      <button @click="goHome" class="btn btn-primary btn-lg return-home-btn">返回Clevora首頁</button>
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
  const apiUrl = `/api/orders/${orderId}/status`;
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
/* 使用新的棕色調 */
:root {
  --dark-brown: #38302e; /* 深棕色 */
  --light-brown: #a18a7b; /* 淺棕色/米色 */
  --white: #ffffff; /* 白色 */
  --light-grey: #f8f9fa; /* 淺灰色，用於背景或邊框 */
  --medium-grey: #e9ecef; /* 中等灰色 */
  --accent-brown: #c8a99a; /* 介於深淺之間的強調棕色 */
  --disabled-text: #6c757d; /* 用於禁用文字的顏色 */
  --success-color: #28a745; /* 保留成功的綠色 */
  --danger-color: #dc3545; /* 保留失敗的紅色 */
  --primary-color: var(--dark-brown); /* 主按鈕使用深棕色 */
}

.return-page {
  background-color: var(--light-grey); /* 淺灰色背景，與其他頁面協調 */
  min-height: calc(100vh - 60px); /* 確保覆蓋視窗高度，扣除 footer 高度 */
  padding: 20px;
  display: flex; /* 確保內容居中 */
  justify-content: center;
  align-items: center;
}

.return-card {
  border-radius: 8px; /* 圓角 */
  /* box-shadow: 0 4px 12px rgba(0,0,0,0.1); */ /* 使用 Bootstrap 的 shadow-lg */
  max-width: 450px; /* 稍微放寬最大寬度 */
  width: 90%;
  background-color: var(--white); /* 白色背景 */
  border: 1px solid var(--medium-grey); /* 添加邊框 */
  padding: 30px; /* 內邊距 */
}

.icon-container {
  font-size: 72px; /* 加大圖標尺寸 */
  margin-bottom: 24px; /* 增加圖標下方的間距 */
}

.check-icon {
  color: var(--success-color); /* 使用定義的成功顏色 */
  animation: scaleAndFadeIn 0.8s ease-out;
}

.fail-icon {
  color: var(--danger-color); /* 使用定義的失敗顏色 */
  animation: shake 0.5s ease-in-out, scaleAndFadeIn 0.8s ease-out;
}

.fa-spinner {
  color: var(--accent-brown); /* 處理中圖標使用強調棕色 */
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

.return-title {
  margin-top: 0; /* 移除默認的 margin-top */
  margin-bottom: 12px; /* 增加標題下方的間距 */
  font-size: 2rem; /* 加大標題字體 */
  color: var(--dark-brown); /* 標題使用深棕色 */
  font-weight: bold; /* 加粗 */
}

/* 根據圖標類別應用標題顏色 */
.check-icon ~ .return-title {
  color: var(--success-color); /* 成功時標題顏色 */
}

.fail-icon ~ .return-title {
  color: var(--danger-color); /* 失敗時標題顏色 */
}

.return-submessage {
  color: var(--disabled-text); /* 子訊息文字顏色使用禁用文字顏色 */
  margin-bottom: 30px; /* 增加子訊息下方的間距 */
  font-size: 1.1rem;
}

/* 返回首頁按鈕 - 應用 main.css 中的 .btn-primary 樣式 */
.return-home-btn {
  /* 繼承 main.css 中的 .btn 和 .btn-primary 樣式 */
  padding: 10px 30px; /* 調整內邊距 */
  font-size: 1.2rem; /* 調整字體大小 */
}

/* 確保頁面內容不會被 NavBar 和 Footer 遮擋 - 已在 App.vue 或 main.css 中處理 */
/*
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
*/

/* RWD 調整 */
@media (max-width: 576px) {
  .return-card {
    padding: 20px; /* 小螢幕調整內邊距 */
  }

  .icon-container {
      font-size: 60px; /* 小螢幕調整圖標大小 */
  }

  .return-title {
    font-size: 1.6rem; /* 小螢幕調整標題字體大小 */
  }

  .return-submessage {
    font-size: 1rem; /* 小螢幕調整字體大小 */
  }

  .return-home-btn {
      font-size: 1rem; /* 小螢幕調整按鈕字體大小 */
      padding: 8px 20px; /* 小螢幕調整按鈕內邊距 */
  }
}
</style> 