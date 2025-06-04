<template>
  <AdminHeader />
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
import AdminHeader from '@/components/AdminHeader.vue';

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
    // 後台管理員登入使用 Basic Auth
    const base64Credentials = btoa(`${username.value}:${password.value}`);
    
    // 嘗試訪問一個受保護的後台端點來驗證 Basic Auth 憑證
    const res = await fetch('/admin/orders', {
      headers: { 'Authorization': 'Basic ' + base64Credentials },
    });

    if (res.ok) {
      // 登入成功，設置 token
      userStore.setToken(base64Credentials);
      // 導向後台主控台頁面
      router.push('/admin');
    } else if (res.status === 401) {
      error.value = '❌ 帳號或密碼錯誤！';
    } else {
      error.value = `後台登入失敗！(${res.status})`;
      console.error('後台登入請求失敗：', res.status, res.statusText);
    }
  } catch (error) {
    console.error('後台登入時發生網路錯誤：', error);
    error.value = '後台登入失敗！請檢查網路連線。';
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

.card {
  max-width: 400px; /* 調整最大寬度 */
  width: 90%; /* 確保在小螢幕上自適應 */
  margin: 0 auto; /* 水平置中 */
  border-radius: 1rem; /* 圓角 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* 柔和陰影 */
  background-color: #fff; /* 白色背景 */
  padding: 40px; /* 增加內邊距 */
}

.card-title {
  font-weight: 600;
  color: #343a40;
}

.form-control-lg {
  text-align: center; /* 輸入框文字置中 */
}

.btn-primary {
  background-color: #6a89cc;
  border-color: #6a89cc;
  font-size: 1.25rem; /* 較大字體 */
  padding: 0.5rem 1rem; /* 調整內邊距 */
}

.btn-primary:hover {
  background-color: #4a69bd;
  border-color: #4a69bd;
}
</style> 