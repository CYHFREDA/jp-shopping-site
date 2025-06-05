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
        <input v-model="username" class="form-control form-control-lg text-center" placeholder="Username">
      </div>
      <div class="mb-3">
        <input v-model="password" type="password" class="form-control form-control-lg text-center" placeholder="Password">
      </div>
      <div class="d-grid">
        <button class="btn btn-primary btn-lg" @click="login">登入</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import AdminNavbar from '@/components/AdminNavbar.vue';

const username = ref('');
const password = ref('');
const router = useRouter();
const error = ref('');
const userStore = useUserStore();

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
      router.push('/admin');
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
  background-color: #f8f9fa; /* 淺灰色背景 */
  display: flex;
  justify-content: center;
  align-items: center; /* 垂直置中 */
  min-height: 100vh; /* 確保背景覆蓋整個視窗 */
  padding: 20px;
}

/* 提升卡片的質感 */
.card {
  max-width: 400px; /* 調整最大寬度 */
  width: 90%; /* 確保在小螢幕上自適應 */
  margin: 0 auto; /* 水平置中 */
  border: none; /* 移除預設邊框 */
  border-radius: 10px; /* 柔和圓角 */
  box-shadow: 0 8px 16px rgba(0,0,0,0.1); /* 更明顯的陰影 */
  background-color: #fff; /* 白色背景 */
  padding: 40px; /* 增加內邊距 */
}

.card-title {
  font-weight: 600;
  color: #343a40; /* 深色標題 */
  font-size: 1.75rem; /* 調整標題字體大小 */
  margin-bottom: 1.5rem !important; /* 增加標題底部間距 */
}

/* 輸入框樣式微調 */
.form-control {
  border-radius: 5px;
  border-color: #ced4da;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.25);
}

.form-control-lg {
  text-align: center; /* 輸入框文字置中 */
}

/* 按鈕樣式微調 */
.btn {
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn-primary {
  background-color: #007bff; /* 使用標準 Bootstrap 主色 */
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}

.btn-lg {
    font-size: 1.25rem;
    padding: 0.5rem 1rem;
}

/* 提示文字樣式 */
.text-muted {
    font-style: italic;
    color: #6c757d !important; /* 調整提示文字顏色 */
}

/* 錯誤提示樣式 */
.alert-danger {
    font-size: 0.9rem;
    padding: 0.75rem 1rem;
}
</style> 