<template>
  <main class="container my-5">
    <h1 class="text-center mb-4"><i class="fas fa-shopping-cart"></i> 購物車</h1>

    <table class="table table-bordered text-center align-middle" v-if="cart.length">
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
            <input type="number" min="1" v-model.number="item.quantity" @change="updateQuantity(index)" class="form-control form-control-sm">
          </td>
          <td>{{ item.price }}</td>
          <td>{{ item.price * item.quantity }}</td>
          <td>
            <button class="btn btn-danger btn-sm" @click="removeItem(index)">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="text-center text-muted">購物車是空的！</p>

    <div class="text-end mb-3 fs-4 fw-bold" v-if="cart.length">
      總金額：{{ totalAmount }} 元
    </div>

    <div class="text-center mt-4" v-if="cart.length">
      <template v-if="customerStore.isAuthenticated">
        <button class="btn btn-success btn-lg px-5" @click="checkout">
          <i class="fas fa-credit-card"></i> 結帳
        </button>
      </template>
      <template v-else>
        <router-link to="/login" class="btn btn-primary btn-lg px-5" @click="saveRedirect">
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
  // 在這裡不再需要檢查登入，因為未登入時會顯示連結而非按鈕
  // if (!customerStore.isAuthenticated) {
  //   const authModal = new Modal(document.getElementById('authModal'));
  //   authModal.show();
  //   return;
  // }

  if (cartStore.items.length === 0) {
    alert("❌ 購物車是空的！");
    return;
  }

  // 參考 frontend/html/cart.html 中的 checkout 函數
  fetch("/pay", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      products: cartStore.items,
      customer_id: customerStore.customer?.customer_id
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.ecpay_url && data.params) {
      cartStore.clearCart(); // 呼叫 Store 中的 action 清空購物車
      // 儲存 order_id 到 localStorage
      if (data.order_id) {
        localStorage.setItem('latest_order_id', data.order_id);
      }
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
      alert("❌ 發起付款失敗！");
    }
  })
  .catch(err => {
    alert("❌ 發起付款錯誤！");
    console.error(err);
  });
}

onMounted(() => {
  cartStore.loadCart();
});
</script>

<style scoped>
@media (max-width: 576px) {
  .table thead {
    display: none;
  }
  .table tr {
    display: block;
    margin-bottom: 1rem;
    border-bottom: 2px solid #dee2e6;
  }
  .table td {
    display: block;
    text-align: right;
    position: relative;
    padding-left: 50%;
  }
  .table td::before {
    position: absolute;
    top: 0;
    left: 0;
    width: 50%;
    padding-right: 10px;
    white-space: nowrap;
    text-align: left;
    font-weight: bold;
  }
  .table td:nth-of-type(1)::before { content: "商品名稱"; }
  .table td:nth-of-type(2)::before { content: "數量"; }
  .table td:nth-of-type(3)::before { content: "單價"; }
  .table td:nth-of-type(4)::before { content: "小計"; }
  .table td:nth-of-type(5)::before { content: "操作"; }
}
</style> 