<template>
  <div class="forgot-password-container">
    <h2>忘記密碼</h2>
    <form @submit.prevent="submitEmail">
      <label for="email">請輸入註冊信箱：</label>
      <input v-model="email" id="email" type="email" required />
      <button type="submit" :disabled="loading">送出</button>
    </form>
    <p v-if="message" :class="{ success: success, error: !success }">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const email = ref('')
const message = ref('')
const success = ref(false)
const loading = ref(false)

const submitEmail = async () => {
  message.value = ''
  loading.value = true
  try {
    const res = await axios.post('/api/customers/forgot-password', { email: email.value })
    message.value = res.data.message || '如果此 Email 有註冊，我們會寄送重設密碼信。'
    success.value = true
  } catch (err) {
    message.value = err.response?.data?.error || '發生錯誤，請稍後再試'
    success.value = false
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-password-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
label {
  display: block;
  margin-bottom: 8px;
}
input {
  width: 100%;
  padding: 8px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  width: 100%;
  padding: 10px;
  background: #a18a7b;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}
.success { color: #2e7d32; }
.error { color: #c62828; }
</style> 