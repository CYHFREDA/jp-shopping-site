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

    <!-- 收件人資訊表單 -->
    <div class="card mb-4" v-if="cart.length">
      <div class="card-body">
        <h5 class="card-title mb-3">收件人資訊</h5>
        <div class="mb-3">
          <label class="form-label">配送方式</label>
          <div class="form-check">
            <input class="form-check-input" type="radio" v-model="deliveryType" value="home" id="homeDelivery">
            <label class="form-check-label" for="homeDelivery">宅配到府</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="radio" v-model="deliveryType" value="cvs" id="cvsDelivery">
            <label class="form-check-label" for="cvsDelivery">超商取貨</label>
          </div>
        </div>
        
        <!-- 宅配地址 -->
        <div v-if="deliveryType === 'home'" class="mb-3">
          <label class="form-label">配送地址</label>
          <input type="text" class="form-control" v-model="address" placeholder="請輸入配送地址">
          <div class="invalid-feedback" v-if="showValidation && !address">請填寫配送地址</div>
        </div>

        <!-- 超商取貨 -->
        <div v-if="deliveryType === 'cvs'" class="mb-3">
          <label class="form-label">選擇取貨門市</label>
          <MultiCvsStoreSelector 
            @select="handleStoreSelect"
            :selected-store="selectedStore"
          />
          <div v-if="showValidation && !selectedStore" class="text-danger small mt-1">
            請選擇取貨門市
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">收件人姓名</label>
          <input 
            type="text" 
            class="form-control" 
            :class="{ 'is-invalid': showValidation && !recipientName }"
            v-model="recipientName" 
            placeholder="請輸入收件人姓名"
          >
          <div v-if="showValidation && !recipientName" class="text-danger small mt-1">
            請填寫收件人姓名
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">收件人電話</label>
          <input 
            type="tel" 
            class="form-control" 
            :class="{ 'is-invalid': showValidation && !recipientPhone }"
            v-model="recipientPhone" 
            placeholder="請輸入收件人電話"
          >
          <div v-if="showValidation && !recipientPhone" class="text-danger small mt-1">
            請填寫收件人電話
          </div>
        </div>
      </div>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/stores/cartStore';
import { useCustomerStore } from '@/stores/customerStore';
import { Modal } from 'bootstrap';
import MultiCvsStoreSelector from '@/components/MultiCvsStoreSelector.vue';

const router = useRouter();
const cartStore = useCartStore();
const customerStore = useCustomerStore();

const cart = computed(() => cartStore.items);
const totalAmount = computed(() => cartStore.totalAmount);
const checkoutErrorMessage = ref('');

// 收件人資訊
const deliveryType = ref('home');  // 預設宅配
const address = ref('');
const selectedStore = ref(null);
const recipientName = ref('');
const recipientPhone = ref('');
const showValidation = ref(false);

// 監聽配送方式變更
watch(deliveryType, (newType) => {
  // 清空相關欄位
  if (newType === 'home') {
    selectedStore.value = null;
  } else {
    address.value = '';
  }
  // 重置驗證狀態
  showValidation.value = false;
});

function handleStoreSelect(store) {
  console.log('選擇的門市：', store);
  selectedStore.value = store ? {
    id: store.id,
    name: store.name,
    type: store.type
  } : null;
}

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

function validateForm() {
  showValidation.value = true;
  
  if (deliveryType.value === 'home' && !address.value) {
    return false;
  }
  
  if (deliveryType.value === 'cvs' && !selectedStore.value) {
    return false;
  }
  
  if (!recipientName.value || !recipientPhone.value) {
    return false;
  }
  
  return true;
}

async function checkout() {
  if (cartStore.items.length === 0) {
    checkoutErrorMessage.value = "❌ 購物車是空的！";
    return;
  }

  if (!validateForm()) {
    checkoutErrorMessage.value = "❌ 請填寫完整的收件人資訊！";
    return;
  }

  try {
    const orderData = {
      products: cart.value,
      customer_id: customerStore.customer.customer_id,
      delivery_type: deliveryType.value,
      recipient_name: recipientName.value,
      recipient_phone: recipientPhone.value,
      ...(deliveryType.value === 'home' 
        ? { address: address.value }
        : { 
            store_id: selectedStore.value.id,
            store_name: selectedStore.value.name,
            cvs_type: selectedStore.value.type
          }
      )
    };
    
    console.log('準備送出訂單資料：', orderData);
    
    const response = await fetch('/api/pay', {
      method: 'POST',
    headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${customerStore.token}`
    },
      body: JSON.stringify(orderData)
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || '結帳失敗');
    }

    if (data.ecpay_url && data.params) {
      // 儲存訂單ID到sessionStorage，以便支付完成後查詢狀態
      sessionStorage.setItem('payment_order_id', data.params.MerchantTradeNo);
      
      // 清空購物車
      cartStore.clearCart();
      
      // 建立並提交表單到綠界
      const form = document.createElement('form');
      form.method = 'post';
      form.action = data.ecpay_url;
      
      Object.entries(data.params).forEach(([key, value]) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
      });
      
      document.body.appendChild(form);
      form.submit();
    } else {
      throw new Error('未收到付款資訊');
    }
  } catch (e) {
    console.error('結帳失敗：', e);
    checkoutErrorMessage.value = e.response?.data?.error || e.message || '結帳失敗，請稍後再試';
  }
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

/* 表單樣式 */
.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(var(--primary-rgb), 0.25);
}

.invalid-feedback {
  display: block;
  color: var(--danger-color);
}

.card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-title {
  color: var(--primary-color);
  font-weight: bold;
}
</style> 