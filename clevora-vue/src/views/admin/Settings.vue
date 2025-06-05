<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">⚙️ 系統設定</h5>
    
    <!-- 訊息提示 -->
    <div v-if="displayMessage" class="alert text-center mb-3" :class="{ 'alert-success': displayMessage.includes('✅'), 'alert-danger': displayMessage.includes('❌') }">
      {{ displayMessage }}
    </div>

    <div v-if="settings">
      <div class="mb-3">
        <label for="siteTitle" class="form-label">網站標題：</label>
        <input type="text" id="siteTitle" v-model="settings.site_title" class="form-control">
      </div>
      <div class="mb-3">
        <label for="contactEmail" class="form-label">聯絡 Email：</label>
        <input type="email" id="contactEmail" v-model="settings.contact_email" class="form-control">
      </div>
      <div class="mb-3">
        <label for="itemsPerPage" class="form-label">每頁商品數量：</label>
        <input type="number" id="itemsPerPage" v-model.number="settings.items_per_page" class="form-control">
      </div>
      
      <!-- 更多設定項目可以根據需要添加 -->

      <button class="btn btn-primary mt-3" @click="saveSettings">保存設定</button>
    </div>
    <div v-else class="text-center text-muted">
      載入設定中...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api'; // 引入 api 實例

const settings = ref(null);
const userStore = useUserStore();
const displayMessage = ref(''); // 新增響應式變數用於顯示訊息

onMounted(() => {
  loadSettings();
  displayMessage.value = ''; // 在組件載入時清除訊息
});

async function loadSettings() {
  displayMessage.value = ''; // 清除之前的訊息
  const token = userStore.admin_token; // 使用 userStore 中的 admin_token
  if (!token) {
    console.error('未找到認證 token！');
    displayMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    // 使用 api 實例發送請求
    const res = await api.get('/admin/settings');

    const data = res.data; // axios 的響應數據在 res.data 中
    settings.value = data;
  } catch (error) {
    console.error('載入設定資料時發生錯誤：', error);
    // 檢查是否是 401 錯誤，如果是，可能需要導向登入頁面
    if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
      // 這裡可以觸發 userStore 的 logout 或直接導向登入頁面
    }
  }
}

async function saveSettings() {
  displayMessage.value = ''; // 清除之前的訊息
  const token = userStore.admin_token; // 使用 userStore 中的 admin_token
  if (!token) {
     console.error('未找到認證 token！');
     displayMessage.value = '❌ 請先登入！';
     return;
  }

  if (!settings.value) return;

  try {
    // 使用 api 實例發送請求
    const res = await api.post('/admin/settings', settings.value); // 或者 PUT，根據後端 API 設計

    const result = res.data; // axios 的響應數據在 res.data 中

    if (res.status !== 200) { // 檢查響應狀態碼
       console.error('保存設定失敗：', result);
       displayMessage.value = result.error || '❌ 保存設定失敗！';
    } else {
       displayMessage.value = result.message || '✅ 設定保存成功！';
       // 保存成功後可以選擇重新載入設定或更新本地狀態
       loadSettings(); 
    }

  } catch (error) {
    console.error('保存設定時發生錯誤：', error);
    // 檢查是否是 401 錯誤，如果是，可能需要導向登入頁面
    if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
      // 這裡可以觸發 userStore 的 logout 或直接導向登入頁面
    }
  }
}
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
}

/* 提升卡片的質感 - 與其他頁面保持一致 */
.card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: var(--white); /* 使用白色背景 */
  margin-top: 1.5rem; /* 添加一些頂部間距 */
}

/* 表單元素樣式微調 */
.form-label {
  font-weight: bold;
  color: var(--dark-brown); /* 標籤顏色使用深棕色 */
  margin-bottom: 0.5rem;
}

.form-control {
  border-radius: 5px;
  border-color: var(--light-brown); /* 輸入框邊框顏色 */
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  color: var(--dark-brown); /* 輸入框文字顏色 */
}

.form-control:focus {
  border-color: var(--accent-brown); /* 聚焦時邊框顏色 */
  box-shadow: 0 0 0 0.25rem rgba(161, 138, 123, 0.25); /* 根據 light-brown 調整陰影顏色 */
}

/* 按鈕樣式微調 - 與其他頁面保持一致 */
.btn {
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

/* 主要按鈕 (保存) */
.btn-primary {
  background-color: var(--light-brown); /* 主要按鈕背景色 */
  border-color: var(--light-brown); /* 主要按鈕邊框顏色 */
  color: var(--dark-brown); /* 主要按鈕文字顏色 */
}

.btn-primary:hover {
  background-color: var(--accent-brown); /* 主要按鈕懸停背景色 */
  border-color: var(--accent-brown); /* 主要按鈕懸停邊框顏色 */
  color: var(--white); /* 主要按鈕懸停文字顏色 */
}

/* 標題樣式微調 - 與其他頁面保持一致 */
.card-title {
  color: var(--dark-brown); /* 深棕色標題 */
  border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
  padding-bottom: 10px; /* 標題與線的間距 */
  margin-bottom: 20px; /* 標題與內容的間距 */
  font-size: 1.5rem; /* 保持原有的字體大小 */
}

/* 載入中提示文字樣式 */
.text-muted {
  font-style: italic;
  color: #6c757d !important; /* 保持灰色，與棕色調協調 */
}
</style> 