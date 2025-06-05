<template>
  <div class="email-verification-page">
    <div class="card p-4 text-center">
      <h4 class="card-title mb-3">Email 驗證</h4>
      
      <div v-if="loading" class="alert alert-info">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">正在驗證您的 Email 地址...</p>
      </div>

      <div v-else-if="success" class="alert alert-success">
        <i class="bi bi-check-circle-fill me-2"></i>
        {{ message }}
        <p class="mt-3">您現在可以前往登入頁面。</p>
        <router-link to="/login" class="btn btn-primary mt-2">前往登入</router-link>
      </div>

      <div v-else class="alert alert-danger">
        <i class="bi bi-x-circle-fill me-2"></i>
        {{ message }}
        <p class="mt-3">如果驗證連結已過期，您可以嘗試重新註冊。</p>
        <router-link to="/login" class="btn btn-secondary mt-2">返回登入/註冊</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const loading = ref(true);
const success = ref(false);
const message = ref('');

onMounted(async () => {
  const token = route.query.token;

  if (!token) {
    message.value = '無效的驗證連結。';
    loading.value = false;
    return;
  }

  try {
    const response = await axios.get(`/api/verify-email?token=${token}`);
    if (response.status === 200) {
      success.value = true;
      message.value = response.data.message;
    } else {
      success.value = false;
      message.value = response.data.detail || 'Email 驗證失敗！';
    }
  } catch (error) {
    success.value = false;
    if (error.response) {
      message.value = error.response.data.detail || 'Email 驗證失敗！';
    } else {
      message.value = '網路錯誤，請稍後再試。';
    }
    console.error('Email 驗證錯誤:', error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.email-verification-page {
  background-color: var(--light-grey); /* 淺灰色背景 */
  display: flex;
  justify-content: center;
  align-items: center; /* 垂直置中 */
  min-height: 100vh; /* 確保背景覆蓋整個視窗 */
  padding: 20px;
}

.card {
  max-width: 500px; /* 調整最大寬度 */
  width: 90%; /* 確保在小螢幕上自適應 */
  margin: 0 auto; /* 水平置中 */
  border: none; /* 移除預設邊框 */
  border-radius: 10px; /* 柔和圓角 */
  box-shadow: 0 8px 16px rgba(0,0,0,0.1); /* 更明顯的陰影 */
  background-color: var(--white); /* 白色背景 */
  padding: 40px; /* 增加內邊距 */
}

.card-title {
  font-weight: 600;
  color: var(--dark-brown); /* 深棕色標題 */
  font-size: 1.75rem; /* 調整標題字體大小 */
  margin-bottom: 1.5rem !important; /* 增加標題底部間距 */
}

.alert {
  padding: 1.25rem 1.5rem;
  border-radius: 8px;
  font-size: 1.1rem;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border-color: #c3e6cb;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border-color: #bee5eb;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
}

.btn {
  border-radius: 5px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s ease-in-out;
}

.btn-primary {
  background-color: var(--light-brown);
  border-color: var(--light-brown);
  color: var(--dark-brown);
}

.btn-primary:hover {
  background-color: var(--accent-brown);
  border-color: var(--accent-brown);
  color: var(--white);
}

.btn-secondary {
  background-color: var(--medium-grey);
  border-color: var(--medium-grey);
  color: var(--dark-brown);
}

.btn-secondary:hover {
  background-color: #dee2e6;
  border-color: #dee2e6;
}
</style> 