<template>
  <main class="auth-main">
    <div class="card auth-card">
      <h3 class="text-center mb-4 auth-title">會員登入 / 註冊</h3>

      <ul class="nav nav-tabs mb-3 auth-tabs" id="authTab" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link auth-tab-link" :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">登入</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link auth-tab-link" :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">註冊</button>
        </li>
      </ul>

      <div class="tab-content">
        <!-- 登入 -->
        <div class="tab-pane fade" :class="{ 'show active': activeTab === 'login' }" id="login">
          <div v-if="loginApiErrorMessage" class="alert" :class="{ 'alert-danger': loginApiErrorMessage.includes('❌'), 'alert-success': loginApiErrorMessage.includes('✅') }" role="alert">
            {{ loginApiErrorMessage }}
          </div>
          <div class="mb-2">
            <label for="loginUsername" class="form-label">使用者名稱</label>
            <input id="loginUsername" type="text" class="form-control" v-model="loginForm.username" />
          </div>
          <div class="mb-2">
            <label for="loginPassword" class="form-label">密碼</label>
            <input id="loginPassword" type="password" class="form-control" v-model="loginForm.password" />
          </div>
          <div class="d-grid">
            <button class="btn btn-success" @click="handleLogin">登入</button>
          </div>
        </div>

        <!-- 註冊 -->
        <div class="tab-pane fade" :class="{ 'show active': activeTab === 'register' }" id="register">
          <div v-if="registrationSuccessAndPendingVerification" class="alert alert-info text-center" role="alert">
            ✅ 註冊成功！請到您的信箱進行驗證。<br>請勿關閉此頁面。待 Email 驗證完成後（透過點擊 Email 中的連結），系統會自動跳轉至登入畫面。<br>驗證連結將於 <b>{{ Math.floor(countdown/60) }} 分 {{ (countdown%60).toString().padStart(2, '0') }} 秒</b> 內過期。<br>若未收到，請檢查垃圾郵件或稍後再試。
          </div>
          <div v-else>
            <div v-if="apiErrorMessage" class="alert" :class="{ 'alert-danger': apiErrorMessage.includes('❌'), 'alert-success': apiErrorMessage.includes('✅') }" role="alert">
              {{ apiErrorMessage }}
            </div>
            <div class="mb-2">
              <label for="registerUsername" class="form-label">使用者名稱</label>
              <input id="registerUsername" type="text" class="form-control" :class="{ 'is-invalid': usernameError }" v-model="registerForm.username" placeholder="username(必填)" />
              <div v-if="usernameError" class="invalid-feedback">{{ usernameError }}</div>
            </div>
            <div class="mb-2">
              <label for="registerName" class="form-label">姓名</label>
              <input id="registerName" type="text" class="form-control" :class="{ 'is-invalid': nameError }" v-model="registerForm.name" placeholder="name(必填)" />
              <div v-if="nameError" class="invalid-feedback">{{ nameError }}</div>
            </div>
            <div class="mb-2">
              <label for="registerEmail" class="form-label">Email</label>
              <input id="registerEmail" type="email" class="form-control" :class="{ 'is-invalid': emailError }" v-model="registerForm.email" placeholder="@gmail.com(必填)" />
              <div v-if="emailError" class="invalid-feedback">{{ emailError }}</div>
            </div>
            <div class="mb-2">
              <label for="registerPhone" class="form-label">電話</label>
              <input id="registerPhone" type="text" class="form-control" :class="{ 'is-invalid': phoneError }" v-model="registerForm.phone" placeholder="Phone Number(必填)" />
              <div v-if="phoneError" class="invalid-feedback">{{ phoneError }}</div>
            </div>
            <div class="mb-2">
              <label for="registerAddress" class="form-label">地址</label>
              <input id="registerAddress" type="text" class="form-control" :class="{ 'is-invalid': addressError }" v-model="registerForm.address" placeholder="address(必填)" />
              <div v-if="addressError" class="invalid-feedback">{{ addressError }}</div>
            </div>         
            <div class="mb-2">
              <label for="registerPassword" class="form-label">密碼</label>
              <input id="registerPassword" type="password" class="form-control" :class="{ 'is-invalid': passwordError }" v-model="registerForm.password" placeholder="password(必填)" />
              <div v-if="passwordError" class="invalid-feedback">{{ passwordError }}</div>
            </div>
            <div class="d-grid">
              <button class="btn btn-primary" @click="handleRegister">註冊</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCustomerStore } from '@/stores/customerStore';
import axios from 'axios';
import { useUserStore } from '@/stores/userStore';

const router = useRouter();
const customerStore = useCustomerStore();
const userStore = useUserStore();

const activeTab = ref('login');

const loginForm = ref({
  username: '',
  password: '',
});

const registerForm = ref({
  username: '',
  name: '',
  email: '',
  phone: '',
  address: '',
  password: '',
});

const registrationSuccessAndPendingVerification = ref(false);
const apiErrorMessage = ref(''); // 用於顯示後端 API 錯誤或成功訊息
const loginApiErrorMessage = ref(''); // 新增用於顯示登入表單的後端 API 錯誤或成功訊息

// 驗證錯誤訊息
const usernameError = ref('');
const nameError = ref('');
const emailError = ref('');
const phoneError = ref('');
const addressError = ref('');
const passwordError = ref('');

const registrationEmail = ref(''); // 新增一個 ref 來儲存註冊成功的 Email
let registrationTimer = null; // 用於儲存計時器 ID
const countdown = ref(300); // 5分鐘=300秒
let countdownTimer = null;

// 驗證函式
function validateUsername() {
  const username = registerForm.value.username;
  if (username.length < 4 || username.length > 20) {
    usernameError.value = '使用者名稱長度需為 4~20 字元！';
    return false;
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    usernameError.value = '使用者名稱只能包含英文、數字、底線！';
    return false;
  }
  if (/^\d+$/.test(username)) {
    usernameError.value = '使用者名稱不可全為數字！';
    return false;
  }
  usernameError.value = '';
  return true;
}

function validateName() {
  const name = registerForm.value.name;
  if (name.length < 2 || name.length > 30) {
    nameError.value = '姓名長度需為 2~30 字元！';
    return false;
  }
  if (!/^[\u4e00-\u9fa5a-zA-Z]+$/.test(name)) {
    nameError.value = '姓名只能包含中文或英文！';
    return false;
  }
  nameError.value = '';
  return true;
}

function validateEmail() {
  const email = registerForm.value.email;
  if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
    emailError.value = '請輸入有效的 Email 格式！';
    return false;
  }
  emailError.value = '';
  return true;
}

function validatePhone() {
  const phone = registerForm.value.phone;
  if (!/^09\d{8}$/.test(phone)) {
    phoneError.value = '請輸入有效的台灣手機號碼 (09 開頭共 10 碼)！';
    return false;
  }
  if (/^(0)+[0-9]{9}$/.test(phone) && new Set(phone.split('')).size === 1) {
    phoneError.value = '電話號碼不可全為相同數字！';
    return false;
  }
  phoneError.value = '';
  return true;
}

function validateAddress() {
  const address = registerForm.value.address;
  if (address.length < 10 || address.length > 100) {
    addressError.value = '地址長度需為 10~100 字元！';
    return false;
  }
  if (!/^[\u4e00-\u9fa5a-zA-Z0-9]+$/.test(address)) {
    addressError.value = '地址只能包含中文、英文、數字！';
    return false;
  }
   if (/^\d+$/.test(address)) {
    addressError.value = '地址不可全為數字！';
    return false;
  }
  addressError.value = '';
  return true;
}

function validatePassword() {
  const password = registerForm.value.password;
  const username = registerForm.value.username;

  if (password.length < 8 || password.length > 20) {
    passwordError.value = '密碼長度需為 8~20 字元！';
    return false;
  }
  if (!/[a-z]/.test(password) || !/[A-Z]/.test(password) || !/\d/.test(password) || !/[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]/.test(password)) {
    passwordError.value = '密碼需包含大小寫英文、數字、特殊字元！';
    return false;
  }
  if (password === username) {
    passwordError.value = '密碼不可與使用者名稱相同！';
    return false;
  }
  passwordError.value = '';
  return true;
}

// 監聽 registerForm 欄位變化，即時清除錯誤訊息
watch(() => registerForm.value.username, validateUsername);
watch(() => registerForm.value.name, validateName);
watch(() => registerForm.value.email, validateEmail);
watch(() => registerForm.value.phone, validatePhone);
watch(() => registerForm.value.address, validateAddress);
watch(() => registerForm.value.password, validatePassword);

async function handleLogin() {
  loginApiErrorMessage.value = ''; // 清除之前的訊息

  const { username, password } = loginForm.value;
  if (!username || !password) {
    loginApiErrorMessage.value = "❌ 請填寫完整使用者名稱和密碼！";
    return;
  }

  try {
    const res = await fetch('/api/customers/login', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (res.ok) {
      loginApiErrorMessage.value = "✅ 登入成功！";
      customerStore.setCustomer(
        { id: data.customer_id, name: data.name },
        data.token,
        data.expire_at
      );

      const redirectURL = localStorage.getItem("redirectAfterLogin") || "/";
      localStorage.removeItem("redirectAfterLogin");
      router.push(redirectURL);
    } else {
      loginApiErrorMessage.value = data.error || '❌ 登入失敗！';
    }
  } catch (error) {
    console.error('登入錯誤：', error);
    loginApiErrorMessage.value = '❌ 登入失敗，請稍後再試。';
  }
}

async function handleRegister() {
  apiErrorMessage.value = ''; // 清除之前的訊息

  // 在這裡執行所有驗證
  const isUsernameValid = validateUsername();
  const isNameValid = validateName();
  const isEmailValid = validateEmail();
  const isPhoneValid = validatePhone();
  const isAddressValid = validateAddress();
  const isPasswordValid = validatePassword();

  if (!isUsernameValid || !isNameValid || !isEmailValid || !isPhoneValid || !isAddressValid || !isPasswordValid) {
    apiErrorMessage.value = '❌ 請修正表單中的錯誤！';
    return;
  }

  try {
    const res = await axios.post('/api/customers/register', registerForm.value);
    const data = res.data;

    if (data.message) {
      registrationSuccessAndPendingVerification.value = true;
      apiErrorMessage.value = '✅ 註冊成功！請到您的信箱進行驗證。';
      
      // 清除表單資料
      registerForm.value = {
        username: '',
        name: '',
        email: '',
        phone: '',
        address: '',
        password: '',
      };
      
      // 清除錯誤訊息
      usernameError.value = '';
      nameError.value = '';
      emailError.value = '';
      phoneError.value = '';
      addressError.value = '';
      passwordError.value = '';

      registrationEmail.value = registerForm.value.email;

      // 啟動 5 分鐘的計時器
      if (registrationTimer) {
        clearTimeout(registrationTimer);
      }
      registrationTimer = setTimeout(() => {
        if (registrationSuccessAndPendingVerification.value) {
          registrationSuccessAndPendingVerification.value = false;
          apiErrorMessage.value = '❌ 註冊失敗：Email 驗證連結已過期，請重新註冊。';
        }
      }, 5 * 60 * 1000);

      startCountdown();
    } else if (data.error) {
      if (data.error.includes('Email 已被使用')) {
        emailError.value = '此 Email 已被註冊，請使用其他 Email 或嘗試登入。';
      } else if (data.error.includes('使用者名稱已被使用')) {
        usernameError.value = '此使用者名稱已被註冊，請使用其他名稱或嘗試登入。';
      } else {
        apiErrorMessage.value = data.error;
      }
    }
  } catch (error) {
    console.error('註冊錯誤：', error);
    if (error.response) {
      // 優先顯示後端回傳的 error 或 detail
      apiErrorMessage.value = error.response.data.error || error.response.data.detail || '❌ 註冊失敗！請稍後再試。';
    } else {
      apiErrorMessage.value = '❌ 註冊失敗！網路錯誤，請稍後再試。';
    }
  }
}

// 新增重新發送驗證信函式
const resendVerificationEmail = async () => {
  if (!registrationEmail.value) {
    loginApiErrorMessage.value = '❌ 無法重新發送：沒有可用的 Email 地址。';
    return;
  }
  try {
    const response = await axios.post('/api/customers/resend-verification-email', {
      email: registrationEmail.value
    });
    apiErrorMessage.value = response.data.message; // 顯示成功訊息
    loginApiErrorMessage.value = ''; // 清除錯誤訊息
    // 重啟計時器，給予用戶新的 5 分鐘時間
    if (registrationTimer) {
        clearTimeout(registrationTimer);
    }
    registrationTimer = setTimeout(() => {
        if (registrationSuccessAndPendingVerification.value) {
            registrationSuccessAndPendingVerification.value = false;
            loginApiErrorMessage.value = '❌ 註冊失敗：Email 驗證連結已過期，請重新註冊或嘗試登入。';
            apiErrorMessage.value = '';
        }
    }, 5 * 60 * 1000); // 5 分鐘（毫秒）

  } catch (error) {
    console.error('重新發送驗證信失敗:', error);
    loginApiErrorMessage.value = error.response?.data?.error || '重新發送驗證信失敗，請稍後再試。';
    apiErrorMessage.value = ''; // 清除成功訊息
  }
};

function startCountdown() {
  countdown.value = 300;
  if (countdownTimer) clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    } else {
      clearInterval(countdownTimer);
      registrationSuccessAndPendingVerification.value = false;
      apiErrorMessage.value = '❌ 驗證連結已過期，請重新註冊。';
    }
  }, 1000);
}

// 在組件卸載時清除計時器，防止記憶體洩漏
onUnmounted(() => {
  if (registrationTimer) {
    clearTimeout(registrationTimer);
  }
  if (countdownTimer) {
    clearInterval(countdownTimer);
  }
});

onMounted(() => {
  if (localStorage.getItem('redirectAfterLogin')) {
    activeTab.value = 'login';
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
  --primary-color: var(--dark-brown); /* 主按鈕使用深棕色 */
}

.auth-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--light-grey); /* 淺灰色背景，與其他頁面協調 */
  padding: 20px; /* 添加內邊距 */
  min-height: 100vh; /* 確保主容器佔滿整個視窗高度 */
}

.auth-card {
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 12px;
  background-color: var(--white);
  padding: 30px;
  border: 1px solid var(--medium-grey);
  box-sizing: border-box; /* 添加 box-sizing */
  display: flex; /* 設置為彈性容器 */
  flex-direction: column; /* 子元素垂直排列 */
  max-height: calc(100vh - 60px); /* 限制卡片總高度，留出頂部和底部間距 */
  overflow-y: auto; /* 讓卡片本身在需要時滾動 */
}

.auth-title {
  color: var(--dark-brown);
  font-weight: bold;
  border-bottom: 2px solid var(--light-brown);
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 1.8rem;
}

/* Nav Tabs 樣式 - 與 main.css 中的全局樣式一致 */
.auth-tabs {
  margin-bottom: 20px; /* 保持與標題的間距 */
}
.auth-tabs .nav-link {
    color: var(--dark-brown);
    border: none;
    border-bottom: 2px solid transparent;
    transition: color 0.3s ease, border-bottom-color 0.3s ease;
}

.auth-tabs .nav-link.active {
  font-weight: bold;
  color: var(--light-brown);
  border-bottom-color: var(--light-brown);
  background-color: transparent;
}

.auth-tabs .nav-link:hover {
    color: var(--accent-brown);
}

/* tab-content 的滾動樣式 */
.tab-content {
  flex-grow: 1; /* 讓其彈性增長，佔滿剩餘空間 */
  overflow-y: auto; /* 啟用垂直滾動，但由 auth-card 決定是否溢出 */
}

/* 表單元素樣式 - 繼承 main.css 中的全局樣式 */
.form-label {
  font-weight: bold;
  color: var(--dark-brown);
  margin-bottom: 0.5rem;
}

/* .form-control 樣式繼承 main.css */

/* 按鈕樣式 - 繼承 main.css 中的全局樣式 */
/* 登入按鈕使用 btn-success 或 btn-primary，註冊按鈕使用 btn-primary */
.btn-success {
    /* 繼承 main.css */
}
.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    color: var(--white);
}
.btn-primary:hover {
    background-color: #2a2523;
    border-color: #2a2523;
    color: var(--white);
}

/* RWD 調整 */
@media (max-width: 768px) {
  .auth-card {
    padding: 20px; /* Adjust padding for smaller screens */
    max-height: calc(100vh - 40px); /* 小螢幕調整卡片最大高度 */
  }
  .auth-title {
    font-size: 1.5rem;
  }
  .auth-tabs .nav-link {
    padding: 0.5rem;
    font-size: 0.9rem;
  }
  .tab-content {
    /* 移除 max-height */
  }
}

/* 確保註冊按鈕初始可見且顏色正確，並提供最高優先級 */
.tab-pane.fade.show.active .d-grid .btn.btn-primary {
  background-color: #38302e !important;
  border-color: #38302e !important;
  color: var(--white) !important;
}

/* 確保懸停時的顏色也正確 */
.tab-pane.fade.show.active .d-grid .btn.btn-primary:hover {
  background-color: #2a2523 !important;
  border-color: #2a2523 !important;
}
</style>