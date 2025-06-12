<template>
  <main class="container my-5 cart-page-container">
    <h1 class="text-center mb-4 page-title"><i class="fas fa-shopping-cart"></i> 購物車</h1>

    <div v-if="cart.length" class="table-responsive">
      <table class="table table-bordered text-center align-middle cart-table">
        <thead class="table-dark">
          <tr>
            <th>商品名稱</th>
            <th>數量</th>
            <th>單價</th>
            <th>小計</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in cart" :key="index">
            <td>{{ item.name }}</td>
            <td>
              <input type="number" min="1" v-model.number="item.quantity" @change="updateQuantity(index)" class="form-control form-control-sm quantity-input">
            </td>
            <td>{{ item.price }}</td>
            <td>{{ item.price * item.quantity }}</td>
            <td>
              <button class="btn btn-danger btn-sm remove-item-btn" @click="removeItem(index)">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="text-center text-muted empty-cart-message">購物車是空的！</p>

    <div v-if="checkoutErrorMessage" class="alert alert-danger text-center mt-3" role="alert">
      {{ checkoutErrorMessage }}
    </div>

    <div class="text-end mb-3 fs-4 fw-bold total-amount" v-if="cart.length">
      總金額：{{ totalAmount }} 元
    </div>

    <div class="text-center mt-4" v-if="cart.length">
      <template v-if="customerStore.isAuthenticated">
        <button class="btn btn-success btn-lg px-5 checkout-btn" @click="checkout">
          <i class="fas fa-credit-card"></i> 結帳
        </button>
      </template>
      <template v-else>
        <router-link to="/login" class="btn btn-primary btn-lg px-5 login-prompt-btn" @click="saveRedirect">
          <i class="fas fa-user"></i> 請先登入
        </router-link>
      </template>
    </div>

  </main>

  <!-- 登入提示 Modal (保留，以防其他地方需要) -->
  <!-- 我們目前直接導向登入頁，所以這個 Modal 在購物車頁面可能不再需要，但先保留 -->
  <div class="modal fade" id="authModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">請先登入</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>您需要先登入才能結帳。</p>
          <router-link to="/login" class="btn btn-primary w-100" @click="saveRedirect">立即登入 / 註冊</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/stores/cartStore';
import { useCustomerStore } from '@/stores/customerStore';
import { Modal } from 'bootstrap';

const router = useRouter();
const cartStore = useCartStore();
const customerStore = useCustomerStore();

const cart = computed(() => cartStore.items);
const totalAmount = computed(() => cartStore.totalAmount);
const checkoutErrorMessage = ref('');

function updateQuantity(index) {
  const item = cart.value[index];
  cartStore.updateQuantity(item.id, item.quantity);
}

function removeItem(index) {
  const item = cart.value[index];
  cartStore.removeItem(item.id);
}

function saveRedirect() {
  localStorage.setItem('redirectAfterLogin', '/cart');
}

function checkout() {
  if (cartStore.items.length === 0) {
    checkoutErrorMessage.value = "❌ 購物車是空的！";
    return;
  }

  fetch("/pay", {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": `Bearer ${customerStore.token}`
    },
    body: JSON.stringify({
      products: cartStore.items,
      customer_id: customerStore.customer?.customer_id
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.ecpay_url && data.params) {
      // 開始支付流程，保存相關資訊
      customerStore.startPayment(data.order_id);
      
      // 建立表單並提交
      const form = document.createElement("form");
      form.action = data.ecpay_url;
      form.method = "post";
      Object.entries(data.params).forEach(([key, value]) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = key;
        input.value = value;
        form.appendChild(input);
      });
      document.body.appendChild(form);
      form.submit();
    } else {
      checkoutErrorMessage.value = "❌ 發起付款失敗！";
    }
  })
  .catch(err => {
    checkoutErrorMessage.value = "❌ 發起付款錯誤！";
    console.error(err);
  });
}

onMounted(() => {
  cartStore.loadCart();
  checkoutErrorMessage.value = '';
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
  --danger-color: #dc3545; /* 保留失敗的紅色 */
}

.cart-page-container {
  background-color: var(--white); /* 容器背景色 */
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.page-title {
  color: var(--dark-brown); /* 深棕色標題 */
  border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 2rem; /* 調整字體大小 */
  font-weight: bold; /* 確保加粗 */
}

/* 表格樣式優化 - 主要使用 main.css 中的 .table 樣式 */
/* .cart-table 將應用 main.css 中的 .table 規則 */
.cart-table {
  /* 可以在這裡添加購物車表格特有的樣式，但盡量利用全局樣式 */
}

/* 數量輸入框樣式 - 使用 main.css 中的 .form-control */
.quantity-input {
  /* 繼承 main.css 中的 .form-control 樣式 */
  width: 80px; /* 固定寬度 */
  text-align: center; /* 文字居中 */
}

/* 按鈕樣式 - 確保使用全局按鈕樣式 */
/* .remove-item-btn 將應用 main.css 中的 .btn-danger 規則 */
/* .checkout-btn 將應用 main.css 中的 .btn-success 規則 */
/* .login-prompt-btn 將應用 main.css 中的 .btn-primary 規則 */

/* 總金額文字樣式 */
.total-amount {
    color: var(--dark-brown); /* 深棕色文字 */
    margin-top: 20px; /* 添加頂部間距 */
}

/* 購物車為空提示文字樣式 */
.empty-cart-message {
    font-style: italic;
    color: var(--disabled-text); /* 使用禁用文字顏色 */
    margin-top: 40px; /* 添加頂部間距 */
    font-size: 1.2rem;
}

/* 載入中 Modal 樣式 - 如果還使用的話 */
.modal-content {
    border-radius: 8px;
}

.modal-header {
    background-color: var(--dark-brown);
    color: var(--white);
    border-bottom: none;
}

.modal-title {
    color: var(--white);
}

.modal-body {
    color: var(--dark-brown);
}

.modal-footer {
    border-top: none;
}

/* RWD 調整 */
@media (max-width: 768px) {
  /* 表格在小螢幕下的響應式處理主要依靠 .table-responsive */
  /* 數量輸入框可能需要調整寬度 */
  .quantity-input {
      width: 60px; /* 小螢幕調整寬度 */
  }

  .cart-page-container {
      padding: 20px; /* 小螢幕調整內邊距 */
  }

  .page-title {
      font-size: 1.8rem; /* 小螢幕調整字體大小 */
  }
}
</style> 