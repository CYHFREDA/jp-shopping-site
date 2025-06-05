<template>
  <nav class="navbar navbar-expand-lg border-bottom shadow-sm">
    <div class="container-fluid">
      <router-link class="navbar-brand fw-bold d-flex align-items-center" to="/">
        <img src="/images/LOGO.png" alt="LOGO" class="me-2" />
        <span>Clevora 日本代購</span>
      </router-link>
      <form id="searchForm" class="d-flex ms-auto me-3" @submit.prevent="handleSearch">
        <input 
          id="searchInput" 
          class="form-control form-control-sm me-2 search-input" 
          type="search" 
          placeholder="搜尋" 
          v-model="searchQuery"
        />
        <button class="btn btn-outline-dark btn-sm search-button" type="submit"><i class="fas fa-search"></i></button>
      </form>
      <div class="d-flex align-items-center">
        <template v-if="customerStore.isAuthenticated">
          <span class="me-2 welcome-message fw-bold">你好, {{ customerStore.customer?.name }}</span>
          <router-link to="/orderHistory" class="me-3 nav-link-text text-decoration-none">我的訂單</router-link>
          <a href="#" class="me-3 nav-link-text text-decoration-none" @click.prevent="handleLogout">登出</a>
        </template>
        <template v-else>
          <router-link to="/login" class="me-3 nav-link-text text-decoration-none">會員登入</router-link>
          <router-link to="/admin/login" class="me-3 nav-link-text text-decoration-none">管理員登入</router-link>
        </template>
        <router-link to="/cart" class="cart-icon-link text-decoration-none position-relative">
          <i class="fas fa-shopping-cart"></i>
          <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger cart-badge">
            {{ cartStore.totalItems }}
          </span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useCustomerStore } from '@/stores/customerStore';
import { useCartStore } from '@/stores/cartStore';
import { useRouter } from 'vue-router';

const customerStore = useCustomerStore();
const cartStore = useCartStore();
const router = useRouter();
const searchQuery = ref('');

function handleLogout() {
  customerStore.logout();
  alert('已成功登出');
  router.push('/');
}

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/', query: { search: searchQuery.value.trim() } });
    searchQuery.value = ''; // 清空搜尋框
  }
}
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

.navbar {
  padding: 0.8rem 1rem; /* 增加垂直內邊距 */
  background-color: var(--dark-brown) !important; /* 導航列背景色 */
  border-bottom: none; /* 移除底部邊框 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); /* 加大陰影 */
}

.navbar-brand {
  color: var(--white) !important; /* 品牌文字顏色 */
  font-weight: bold;
  display: flex;
  align-items: center;
  font-size: 1.4rem; /* 加大品牌文字字體 */
}

.navbar-brand:hover {
  color: var(--light-brown) !important; /* 懸停時顏色 */
}

.navbar-brand img {
  height: 40px;
  /* 可能需要調整 LOGO 在深色背景下的可見性 */
  background-color: #8F8A80; /* 修改 LOGO 背景顏色 */
  padding: 5px; /* 增加一些內邊距 */
  border-radius: 5px; /* 添加圓角 */
}

/* 搜尋表單樣式 */
#searchForm {
    flex-grow: 1; /* 允許搜尋表單佔據更多空間 */
    max-width: 300px; /* 設定最大寬度 */
}

.search-input {
  border-radius: 20px; /* 藥丸形狀 */
  border-color: transparent; /* 隱藏邊框 */
  background-color: rgba(255, 255, 255, 0.1); /* 半透明白色背景 */
  color: var(--white); /* 文字顏色 */
}

.search-input::placeholder {
   color: rgba(255, 255, 255, 0.6); /* 半透明 placeholder 文字顏色 */
}

.search-input:focus {
  border-color: var(--light-brown); /* 聚焦時淺棕色邊框 */
  background-color: var(--white); /* 聚焦時白色背景 */
  color: var(--dark-brown); /* 聚焦時文字顏色 */
  box-shadow: 0 0 0 0.25rem rgba(161, 138, 123, 0.4); /* 根據 light-brown 調整陰影顏色 */
}

.search-button {
  border-radius: 20px; /* 藥丸形狀 */
  border-color: transparent; /* 隱藏邊框 */
  color: var(--light-brown); /* 按鈕圖標顏色 */
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out;
}

.search-button:hover {
  color: var(--white); /* 懸停文字顏色 */
  background-color: rgba(255, 255, 255, 0.1); /* 懸停背景色 */
  border-color: transparent;
}

/* 導航連結文字樣式 */
.nav-link-text {
    color: var(--light-brown) !important; /* 連結文字顏色 */
    transition: color 0.2s ease;
    padding: 0.5rem 0.8rem; /* 調整內邊距 */
    border-radius: 5px; /* 添加輕微圓角 */
}

.nav-link-text:hover {
    color: var(--white) !important; /* 懸停時變色 */
    background-color: rgba(255, 255, 255, 0.08); /* 懸停時半透明背景 */
}

/* 歡迎訊息文字顏色 */
.welcome-message {
    color: var(--white); /* 使用白色以在深色背景上清晰 */
    margin-right: 1rem !important; /* 調整間距 */
}

/* 購物車圖標和徽章樣式 */
.cart-icon-link {
    color: var(--light-brown); /* 圖標顏色 */
    font-size: 1.3rem; /* 加大圖標大小 */
    transition: color 0.2s ease;
}

.cart-icon-link:hover {
    color: var(--white); /* 懸停時變色 */
}

.cart-badge {
   background-color: var(--danger-color) !important; /* 徽章背景色使用紅色 */
   color: var(--white); /* 徽章文字顏色使用白色 */
   font-size: 0.75rem;
   top: -0.2rem !important; /* 微調位置 */
   right: -0.5rem !important;
}

/* RWD 調整 */
@media (max-width: 992px) { /* 根據 navbar-expand-lg 的斷點調整 */
  #searchForm {
    max-width: 100%; /* 小螢幕下搜尋表單佔滿寬度 */
    margin-right: 0 !important;
    margin-bottom: 1rem; /* 添加底部間距 */
  }

  .navbar-collapse {
      flex-grow: 1;
      align-items: center;
  }

  .navbar-nav {
      width: 100%;
      text-align: center;
  }

  .nav-link-text {
      margin-right: 0 !important;
      margin-bottom: 0.5rem; /* 添加底部間距 */
  }

  .welcome-message {
      margin-right: 0 !important;
      margin-bottom: 0.5rem; /* 添加底部間距 */
  }

  .cart-icon-link {
      display: block; /* 購物車圖標獨佔一行 */
      text-align: center;
      margin-top: 0.5rem; /* 添加頂部間距 */
  }

  .cart-badge {
      top: 0 !important;
      right: 0 !important;
      position: static; /* 小螢幕下移除絕對定位 */
      margin-left: 5px; /* 添加左側間距 */
  }
}

@media (max-width: 576px) {
    .navbar-brand span {
        font-size: 1.2rem; /* 小螢幕調整品牌文字大小 */
    }

    .search-input,
    .search-button {
        font-size: 0.9rem; /* 小螢幕調整搜尋欄字體大小 */
    }
}

</style>
