<template>
  <main class="my-5 auth-main">
    <!-- 登入 / 註冊卡片 -->
    <div class="card auth-card mx-auto">
      <h3 class="text-center mb-4 auth-title">會員登入 / 註冊</h3>

      <ul class="nav nav-tabs mb-3 auth-tabs" id="authTab" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link auth-tab-link active" id="login-tab" data-bs-toggle="tab" data-bs-target="#login" type="button">登入</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link auth-tab-link" id="register-tab" data-bs-toggle="tab" data-bs-target="#register" type="button">註冊</button>
        </li>
      </ul>

      <div class="tab-content">
        <!-- 登入 -->
        <div class="tab-pane fade show active" id="login" role="tabpanel">
          <div class="mb-3">
            <input v-model="loginForm.username" type="text" class="form-control" placeholder="使用者名稱">
          </div>
          <div class="mb-3">
            <input v-model="loginForm.password" type="password" class="form-control" placeholder="密碼">
          </div>
          <div class="d-grid">
            <button class="btn btn-success" @click="login">登入</button>
          </div>
        </div>

        <!-- 註冊 -->
        <div class="tab-pane fade" id="register" role="tabpanel">
          <div class="mb-3">
            <input v-model="registerForm.username" type="text" class="form-control" placeholder="使用者名稱">
          </div>
          <div class="mb-3">
            <input v-model="registerForm.name" type="text" class="form-control" placeholder="姓名">
          </div>
          <div class="mb-3">
            <input v-model="registerForm.email" type="email" class="form-control" placeholder="Email">
          </div>
          <div class="mb-3">
            <input v-model="registerForm.phone" type="text" class="form-control" placeholder="電話">
          </div>
          <div class="mb-3">
            <input v-model="registerForm.address" type="text" class="form-control" placeholder="地址">
          </div>
          <div class="mb-3">
            <input v-model="registerForm.password" type="password" class="form-control" placeholder="密碼">
          </div>
          <div class="d-grid">
            <button class="btn btn-primary" @click="register">註冊</button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useCustomerStore } from '@/stores/customerStore';
import * as bootstrap from 'bootstrap'; // 引入 Bootstrap JS

const router = useRouter();
const customerStore = useCustomerStore();

const loginForm = ref({
  username: '',
  password: '',
});

const registerForm = ref({
  username: '',
  name: '',
  email: '',
  phone: '',
  address: '', // Initialize address field
  password: '',
});

// 登入功能
const login = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    alert('請輸入完整帳號密碼！');
    return;
  }

  try {
    const res = await axios.post('/customers/login', loginForm.value);
    const data = res.data;

    if (data.message) {
      alert('✅ 登入成功！');
      // 使用 customerStore 更新客戶狀態，傳遞從後端獲取的用戶數據、token 和過期時間
      customerStore.setCustomer(
        {
          id: data.customer_id,
          name: data.name,
          // 如果後端返回更多客戶相關屬性，請在此處添加
        }, // 客戶數據
        data.token,       // token
        data.expire_at    // 過期時間
      );

      const redirectURL = localStorage.getItem('redirectAfterLogin') || '/';
      localStorage.removeItem('redirectAfterLogin');
      window.location.href = redirectURL; // 使用 window.location.href 進行全頁面跳轉以確保導覽列狀態更新
    } else {
      alert(data.error);
    }
  } catch (error) {
    console.error('登入失敗：', error);
    alert('登入失敗！請稍後再試。');
  }
};

// 註冊功能
const register = async () => {
  if (!registerForm.value.username || !registerForm.value.name || !registerForm.value.email || !registerForm.value.phone || !registerForm.value.address || !registerForm.value.password) {
    alert('請填寫完整必填資訊！');
    return;
  }

  try {
    const res = await axios.post('/customers/register', registerForm.value);
    const data = res.data;

    if (data.message) {
      alert('✅ 註冊成功！請再點一次登入');
      // 切換到登入 tab
      const loginTab = document.getElementById('login-tab');
      if (loginTab) {
        const tab = new bootstrap.Tab(loginTab);
        tab.show();
      }
    } else {
      alert(data.error);
    }
  } catch (error) {
    console.error('註冊失敗：', error);
    alert('註冊失敗！請稍後再試。');
  }
};

// 在組件掛載後初始化 Bootstrap Tab
onMounted(() => {
  const triggerTabList = document.querySelectorAll('#authTab button')
  triggerTabList.forEach(triggerEl => {
    const tabTrigger = new bootstrap.Tab(triggerEl)

    triggerEl.addEventListener('click', event => {
      event.preventDefault()
      tabTrigger.show()
    })
  })
});

// 檢查登入狀態，如果已登入則導向首頁 (避免重複登入)
onMounted(() => {
  // 增加一個短暫的延遲，確保頁面渲染完成再檢查登入狀態和導向
  setTimeout(() => {
    if (customerStore.isAuthenticated) {
      console.log('已偵測到登入狀態，導向首頁...'); // 添加日誌
      router.push('/');
    }
  }, 100); // 延遲 100 毫秒，可根據需要調整
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
}

.auth-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--light-grey); /* 淺灰色背景，與其他頁面協調 */
  padding: 20px; /* 添加內邊距 */
  min-height: 100vh; /* 確保覆蓋整個視窗高度 */
}

.auth-card {
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 12px;
  background-color: var(--white); /* 白色背景 */
  padding: 30px;
}

.auth-title {
  color: var(--dark-brown); /* 深棕色標題 */
  font-weight: bold;
  border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
  padding-bottom: 10px;
  margin-bottom: 20px;
}

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
}

.auth-tabs .nav-link:hover {
    color: var(--accent-brown); /* 懸停時變色 */
}

/* 表單元素樣式微調 - 與其他頁面保持一致 */
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

.form-control::placeholder {
  color: var(--light-brown); /* Placeholder 文字顏色 */
  opacity: 0.8; /* 調整透明度 */
}

.form-control:focus {
  border-color: var(--accent-brown); /* 聚焦時邊框顏色 */
  box-shadow: 0 0 0 0.25rem rgba(161, 138, 123, 0.25); /* 根據 light-brown 調整陰影顏色 */
}

/* 按鈕樣式微調 - 與其他頁面保持一致 */
.btn {
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out, color 0.15s ease-in-out;
}

/* 登入按鈕 (success) */
.btn-success {
   background-color: var(--dark-brown); /* 深棕色 */
   border-color: var(--dark-brown); /* 深棕色 */
   color: var(--white); /* 白色文字 */
}

.btn-success:hover {
    background-color: #2a2523; /* 懸停時深一點的棕色 */
    border-color: #2a2523;
    color: var(--white);
}

/* 註冊按鈕 (primary) */
.btn-primary {
  background-color: var(--light-brown); /* 淺棕色 */
  border-color: var(--light-brown); /* 淺棕色 */
  color: var(--dark-brown); /* 深棕色文字 */
}

.btn-primary:hover {
  background-color: var(--accent-brown); /* 強調棕色 */
  border-color: var(--accent-brown); /* 強調棕色 */
  color: var(--white); /* 白色文字 */
}

/* RWD 調整 */
@media (max-width: 576px) {
  .auth-card {
    margin: 20px auto; /* 在小螢幕上添加上下間距 */
    padding: 20px;
  }
}
</style> 