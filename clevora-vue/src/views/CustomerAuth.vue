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
          <div class="form-content-scroll">
            <div class="mb-3">
              <label for="loginUsername" class="form-label">使用者名稱</label>
              <input id="loginUsername" type="text" class="form-control" v-model="loginForm.username" />
            </div>
            <div class="mb-3">
              <label for="loginPassword" class="form-label">密碼</label>
              <input id="loginPassword" type="password" class="form-control" v-model="loginForm.password" />
            </div>
            <div class="d-grid">
              <button class="btn btn-success" @click="handleLogin">登入</button>
            </div>
          </div>
        </div>

        <!-- 註冊 -->
        <div class="tab-pane fade" :class="{ 'show active': activeTab === 'register' }" id="register">
          <div class="form-content-scroll">
            <div class="mb-3">
              <label for="registerUsername" class="form-label">使用者名稱</label>
              <input id="registerUsername" type="text" class="form-control" v-model="registerForm.username" placeholder="username(必填)" />
            </div>
            <div class="mb-3">
              <label for="registerName" class="form-label">姓名</label>
              <input id="registerName" type="text" class="form-control" v-model="registerForm.name" placeholder="name(必填)" />
            </div>
            <div class="mb-3">
              <label for="registerEmail" class="form-label">Email</label>
              <input id="registerEmail" type="email" class="form-control" v-model="registerForm.email" placeholder="@gmail.com(必填)" />
            </div>
            <div class="mb-3">
              <label for="registerPhone" class="form-label">電話</label>
              <input id="registerPhone" type="text" class="form-control" v-model="registerForm.phone" placeholder="Phone Number(必填)" />
            </div>
            <div class="mb-3">
              <label for="registerAddress" class="form-label">地址</label>
              <input id="registerAddress" type="text" class="form-control" v-model="registerForm.address" placeholder="address(必填)" />
            </div>         
            <div class="mb-3">
              <label for="registerPassword" class="form-label">密碼</label>
              <input id="registerPassword" type="password" class="form-control" v-model="registerForm.password" placeholder="password(必填)" />
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCustomerStore } from '@/stores/customerStore';

const router = useRouter();
const customerStore = useCustomerStore();

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

async function handleLogin() {
  const { username, password } = loginForm.value;
  if (!username || !password) {
    alert("請填寫完整使用者名稱和密碼！");
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
      alert("✅ 登入成功！");
      customerStore.setCustomer(
        { id: data.customer_id, name: data.name },
        data.token,
        data.expire_at
      );

      const redirectURL = localStorage.getItem("redirectAfterLogin") || "/";
      localStorage.removeItem("redirectAfterLogin");
      router.push(redirectURL);
    } else {
      alert(data.error || '登入失敗！');
    }
  } catch (error) {
    console.error('登入錯誤：', error);
    alert('登入失敗，請稍後再試');
  }
}

async function handleRegister() {
  const { username, name, email, phone, address, password } = registerForm.value;

  if (!username || !name || !email || !phone || !address || !password) {
    alert("請填寫所有必填欄位！");
    return;
  }

  try {
    const res = await fetch('/api/customers/register', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, name, email, phone, address, password })
    });

    const data = await res.json();

    if (res.ok) {
      alert("✅ 註冊成功！請切換到登入分頁登入");
      registerForm.value = {
        username: '',
        name: '',
        email: '',
        phone: '',
        address: '',
        password: '',
      };
      activeTab.value = 'login';
    } else {
      alert(data.error || '註冊失敗！');
    }
  } catch (error) {
    console.error('註冊錯誤：', error);
    alert('註冊失敗，請稍後再試');
  }
}

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
  min-height: calc(100vh - 60px); /* 確保覆蓋視窗高度，扣除 footer 高度 */
}

.auth-card {
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 12px;
  background-color: var(--white); /* 白色背景 */
  padding: 30px;
  border: 1px solid var(--medium-grey); /* 添加邊框 */
}

.auth-title {
  color: var(--dark-brown); /* 深棕色標題 */
  font-weight: bold;
  border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 1.8rem; /* 調整字體大小 */
}

/* Nav Tabs 樣式 - 與 main.css 中的全局樣式一致 */
.auth-tabs .nav-link {
    color: var(--dark-brown); /* 非激活標籤文字顏色 */
    border: none;
    border-bottom: 2px solid transparent; /* 預設透明底部邊框 */
    transition: color 0.3s ease, border-bottom-color 0.3s ease;
}

.auth-tabs .nav-link.active {
  font-weight: bold;
  color: var(--light-brown); /* 激活標籤文字顏色 */
  border-bottom-color: var(--light-brown); /* 激活底部邊框顏色 */
  background-color: transparent; /* 移除背景色 */
}

.auth-tabs .nav-link:hover {
    color: var(--accent-brown); /* 懸停時變色 */
}

/* 表單元素樣式 - 繼承 main.css 中的全局樣式 */
.form-label {
  font-weight: bold;
  color: var(--dark-brown); /* 標籤顏色使用深棕色 */
  margin-bottom: 0.5rem;
}

/* .form-control 樣式繼承 main.css */

/* 按鈕樣式 - 繼承 main.css 中的全局樣式 */
/* 登入按鈕使用 btn-success 或 btn-primary，註冊按鈕使用 btn-primary */
.btn-success {
    /* 繼承 main.css */
}
.btn-primary {
    background-color: var(--primary-color); /* 使用深棕色 */
    border-color: var(--primary-color);
    color: var(--white);
}
.btn-primary:hover {
    background-color: #2a2523;
    border-color: #2a2523;
    color: var(--white);
}

.form-content-scroll {
  max-height: 400px; /* 根據需要調整，以確保內容滾動 */
  overflow-y: auto;
  padding-right: 15px; /* 為滾動條留出空間 */
}

/* RWD 調整 */
@media (max-width: 576px) {
  .auth-card {
    padding: 20px; /* 小螢幕調整內邊距 */
  }

  .auth-title {
    font-size: 1.5rem; /* 小螢幕調整標題字體大小 */
  }

  .auth-tabs .nav-link {
      padding: 0.5rem; /* 小螢幕調整 tab 內邊距 */
      font-size: 0.9rem;
  }

  .form-content-scroll {
    max-height: 300px; /* 小螢幕調整滾動區域高度 */
  }
}
</style>