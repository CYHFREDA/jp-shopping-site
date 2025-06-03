<template>
  <main class="auth-main">
    <!-- 登入 / 註冊卡片 -->
    <div class="card auth-card">
      <h3 class="text-center mb-4">會員登入 / 註冊</h3>

      <ul class="nav nav-tabs mb-3" id="authTab" role="tablist">
        <li class="nav-item" role="presentation">
          <button
            class="nav-link"
            :class="{ active: activeTab === 'login' }"
            @click="activeTab = 'login'"
            id="login-tab"
            type="button"
          >
            登入
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button
            class="nav-link"
            :class="{ active: activeTab === 'register' }"
            @click="activeTab = 'register'"
            id="register-tab"
            type="button"
          >
            註冊
          </button>
        </li>
      </ul>

      <div class="tab-content">
        <!-- 登入 -->
        <div
          class="tab-pane fade"
          :class="{ 'show active': activeTab === 'login' }"
          id="login"
          role="tabpanel"
        >
          <div class="mb-3">
            <label for="loginUsername" class="form-label">使用者名稱</label>
            <input
              id="loginUsername"
              type="text"
              class="form-control"
              v-model="loginForm.username"
              placeholder="使用者名稱"
            />
          </div>
          <div class="mb-3">
            <label for="loginPassword" class="form-label">密碼</label>
            <input
              id="loginPassword"
              type="password"
              class="form-control"
              v-model="loginForm.password"
              placeholder="密碼"
            />
          </div>
          <div class="d-grid">
            <button class="btn btn-success" @click="handleLogin">登入</button>
          </div>
        </div>

        <!-- 註冊 -->
        <div
          class="tab-pane fade"
          :class="{ 'show active': activeTab === 'register' }"
          id="register"
          role="tabpanel"
        >
          <div class="mb-3">
            <label for="registerUsername" class="form-label">使用者名稱</label>
            <input
              id="registerUsername"
              type="text"
              class="form-control"
              v-model="registerForm.username"
              placeholder="使用者名稱"
            />
          </div>
          <div class="mb-3">
            <label for="registerName" class="form-label">姓名</label>
            <input
              id="registerName"
              type="text"
              class="form-control"
              v-model="registerForm.name"
              placeholder="姓名"
            />
          </div>
          <div class="mb-3">
            <label for="registerEmail" class="form-label">Email（選填）</label>
            <input
              id="registerEmail"
              type="email"
              class="form-control"
              v-model="registerForm.email"
              placeholder="Email（選填）"
            />
          </div>
          <div class="mb-3">
            <label for="registerPhone" class="form-label">電話（選填）</label>
            <input
              id="registerPhone"
              type="text"
              class="form-control"
              v-model="registerForm.phone"
              placeholder="電話（選填）"
            />
          </div>
          <div class="mb-3">
            <label for="registerPassword" class="form-label">密碼</label>
            <input
              id="registerPassword"
              type="password"
              class="form-control"
              v-model="registerForm.password"
              placeholder="密碼"
            />
          </div>
          <div class="d-grid">
            <button class="btn btn-primary" @click="handleRegister">註冊</button>
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
  password: '',
});

async function handleLogin() {
  const { username, password } = loginForm.value;

  if (!username || !password) {
    alert("請填寫完整使用者名稱和密碼！");
    return;
  }

  try {
    const res = await fetch('/customers/login', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (res.ok) {
      alert("✅ 登入成功！");
      customerStore.setCustomer({
        id: data.id,
        name: data.name,
        username: data.username,
        email: data.email,
        phone: data.phone
      });
      const redirectURL = localStorage.getItem("redirectAfterLogin") || "/";
      localStorage.removeItem("redirectAfterLogin");
      router.push(redirectURL);
    } else {
      console.error('登入失敗：', data);
      alert(data.error || '登入失敗！');
    }
  } catch (error) {
    console.error('登入時發生錯誤：', error);
    alert('登入時發生錯誤！');
  }
}

async function handleRegister() {
  const { username, name, email, phone, password } = registerForm.value;

  if (!username || !name || !password) {
    alert("請填寫完整使用者名稱、姓名和密碼！");
    return;
  }

  try {
    const res = await fetch('/customers/register', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, name, email, phone, password })
    });

    const data = await res.json();

    if (res.ok) {
      alert("✅ 註冊成功！請切換到登入分頁登入");
      registerForm.value = {
        username: '',
        name: '',
        email: '',
        phone: '',
        password: '',
      };
      activeTab.value = 'login';
    } else {
      console.error('註冊失敗：', data);
      alert(data.error || '註冊失敗！');
    }
  } catch (error) {
    console.error('註冊時發生錯誤：', error);
    alert('註冊時發生錯誤！');
  }
}

onMounted(() => {
  if (localStorage.getItem('redirectAfterLogin')) {
    activeTab.value = 'login';
  }
});
</script>

<style scoped>
.auth-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to right, #f8f9fa, #e9ecef);
}

.auth-card {
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 12px;
  background-color: #fff;
  padding: 30px;
}

.nav-tabs .nav-link.active {
  font-weight: bold;
  color: #0d6efd;
}

@media (max-width: 576px) {
  .auth-card {
    margin: 20px auto;
    padding: 20px;
  }
}
</style> 