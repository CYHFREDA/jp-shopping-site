<template>
  <div class="reset-password-container">
    <h2>重設密碼</h2>
    <form @submit.prevent="submitReset">
      <label for="password">新密碼：</label>
      <input v-model="password" id="password" type="password" required />
      <button type="submit" :disabled="loading">重設密碼</button>
    </form>
    <p v-if="message" :class="{ success: success, error: !success }">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const token = route.query.token
const password = ref('')
const message = ref('')
const success = ref(false)
const loading = ref(false)

const submitReset = async () => {
  message.value = ''
  loading.value = true
  try {
    const res = await axios.post('/api/customers/reset-password', { token, new_password: password.value })
    message.value = res.data.message || '密碼已重設成功，請用新密碼登入。'
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
.reset-password-container {
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