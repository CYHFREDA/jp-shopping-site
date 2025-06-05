<template>
  <AdminNavbar />
  <div class="admin-login-page">
    <div class="card p-4 text-center">
      <h4 class="card-title mb-3">後台登入</h4>
      <p class="text-muted mb-4">請輸入您的帳號與密碼以登入後台</p>
      
      <div v-if="error" class="alert alert-danger mb-3">
        {{ error }}
      </div>
      
      <div class="mb-2">
        <input v-model="username" class="form-control form-control-lg" placeholder="Username">
      </div>
      <div class="mb-3">
        <input v-model="password" type="password" class="form-control form-control-lg" placeholder="Password">
      </div>
      <div class="d-grid">
        <button class="btn btn-primary btn-lg" @click="login">登入</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import AdminNavbar from '@/components/AdminNavbar.vue';

const username = ref('');
const password = ref('');
const router = useRouter();
const error = ref('');
const userStore = useUserStore();

// 監聽 userStore.isAuthenticated 的變化，如果為 true 則導向後台主控台頁面
watch(() => userStore.isAuthenticated, (newVal) => {
  if (newVal) {
    router.push('/admin/orders');
  }
}, { immediate: true }); // immediate: true 確保在組件初始化時也執行一次檢查

// 登入功能
const login = async () => {
  if (!username.value || !password.value) {
    error.value = '請輸入完整帳號密碼！';
    return;
  }

  try {
    const res = await axios.post('/api/admin/login', {
      username: username.value,
      password: password.value,
    });

    if (res.status === 200) {
      const { token, expire_at } = res.data;
      // 登入成功，設置 token 和 expire_at
      userStore.setToken(token, expire_at);
      // 導向後台主控台頁面
      router.push('/admin/orders');
    } else if (res.status === 401) {
      error.value = '❌ 帳號或密碼錯誤！';
    } else {
      error.value = `後台登入失敗！(${res.status})`;
      console.error('後台登入請求失敗：', res.status, res.statusText);
    }
  } catch (err) {
    if (err.response && err.response.status === 401) {
      error.value = '❌ 帳號或密碼錯誤！';
    } else {
      console.error('後台登入時發生網路錯誤：', err);
    error.value = '後台登入失敗！請檢查網路連線。';
    }
  }
};
</script>

<style scoped>
.admin-login-page {
  background-color: var(--light-grey); /* 淺灰色背景，與後台其他頁面協調 */
  display: flex;
  justify-content: center;
  align-items: center; /* 垂直置中 */
  min-height: 100vh; /* 確保背景覆蓋整個視窗 */
  padding: 20px;
}

/* 提升卡片的質感 - 與其他頁面保持一致 */
.card {
  max-width: 400px; /* 調整最大寬度 */
  width: 90%; /* 確保在小螢幕上自適應 */
  margin: 0 auto; /* 水平置中 */
  border: none; /* 移除預設邊框 */
  border-radius: 10px; /* 柔和圓角 */
  box-shadow: 0 8px 16px rgba(0,0,0,0.1); /* 更明顯的陰影 */
  background-color: var(--white); /* 白色背景 */
  padding: 40px; /* 增加內邊距 */
}

/* 標題樣式微調 - 與其他頁面保持一致 */
.card-title {
  font-weight: 600;
  color: var(--dark-brown); /* 深棕色標題 */
  font-size: 1.75rem; /* 調整標題字體大小 */
  margin-bottom: 1.5rem !important; /* 增加標題底部間距 */
}

/* 輸入框樣式微調 - 與其他頁面保持一致 */
.form-control {
  border-radius: 5px;
  border-color: var(--light-brown); /* 輸入框邊框顏色 */
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  color: var(--dark-brown); /* 輸入框文字顏色 */
}

.form-control::placeholder {
  color: var(--light-brown); /* Placeholder 文字顏色 */
  opacity: 0.8; /* 調整透明度 */
}

.form-control:focus {
  border-color: var(--accent-brown); /* 聚焦時邊框顏色 */
  box-shadow: 0 0 0 0.25rem rgba(161, 138, 123, 0.25); /* 根據 light-brown 調整陰影顏色 */
}

.form-control-lg {
  text-align: left; /* 輸入框文字靠左對齊 */
}

/* 按鈕樣式微調 - 與其他頁面保持一致 */
.btn {
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

/* 主要按鈕 (登入) */
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

.btn-lg {
    font-size: 1.25rem;
    padding: 0.5rem 1rem;
}

/* 提示文字樣式 */
.text-muted {
    font-style: italic;
    color: #6c757d !important; /* 調整提示文字顏色，保持灰色協調 */
}

/* 錯誤提示樣式 - 保持紅色 */
.alert-danger {
    font-size: 0.9rem;
    padding: 0.75rem 1rem;
    color: #721c24; /* 錯誤文字顏色 */
    background-color: #f8d7da; /* 錯誤背景色 */
    border-color: #f5c6cb; /* 錯誤邊框顏色 */
    border-radius: 5px;
}
</style> 