<template>
  <div class="container mt-4">
    <h2 class="mb-3">📦 訂單管理</h2>
    <div v-if="isLoading" class="text-center text-muted">載入中...</div>
    <div v-else-if="displayErrorMessage" class="alert alert-danger text-center mb-3" role="alert">
      {{ displayErrorMessage }}
    </div>
    <div v-else>
      <!-- 桌機版表格 -->
      <div class="table-responsive d-none d-md-block">
        <table class="table table-striped table-bordered">
          <thead>
            <tr>
              <th>訂單編號</th>
              <th>金額</th>
              <th>商品內容</th>
              <th>狀態</th>
              <th>建立時間</th>
              <th>付款時間</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.order_id">
              <td>{{ order.order_id }}</td>
              <td><span class="price-currency">NT$</span> {{ order.amount }}</td>
              <td>{{ order.item_names ? order.item_names : '無商品內容' }}</td>
              <td>{{ order.status }}</td>
              <td>{{ formatDateTime(order.created_at) }}</td>
              <td>{{ order.paid_at ? formatDateTime(order.paid_at) : '尚未付款' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 手機版共用卡片元件 -->
      <AdminCardList :items="orders" :fields="cardFields" key-field="order_id" />
      <p v-if="orders.length === 0" class="text-center text-muted">目前沒有訂單</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import AdminCardList from '@/components/AdminCardList.vue';

const router = useRouter();
const orders = ref([]);
const isLoading = ref(true);
const userStore = useUserStore();

const cardFields = [
  { key: 'order_id', label: '訂單編號' },
  { key: 'amount', label: '金額', formatter: (v) => `NT$ ${v}` },
  { key: 'item_names', label: '商品內容' },
  { key: 'status', label: '狀態' },
  { key: 'created_at', label: '建立時間' },
  { key: 'paid_at', label: '付款時間', formatter: (v) => v || '尚未付款' },
];

const loadOrders = async () => {
  const token = userStore.admin_token;
  console.log('[Orders.vue] loadOrders token:', token);
  if (!token) {
    alert('請先登入後台');
    router.push('/admin/login');
    return;
  }

  try {
    const res = await axios.get('/api/admin/orders', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    console.log('從後端接收到的訂單數據:', res.data);

    // Log each order object for inspection
    if (Array.isArray(res.data)) {
      res.data.forEach((order, index) => {
        console.log(`訂單 ${index}:`, order);
      });
    }

    orders.value = res.data;
    isLoading.value = false;
  } catch (error) {
    console.error('載入訂單時發生錯誤:', error);
    isLoading.value = false;
  }
};

function formatDateTime(dt) {
  if (!dt) return '';
  const d = new Date(dt);
  if (isNaN(d.getTime())) return dt;
  const pad = n => n.toString().padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

onMounted(() => {
  loadOrders();
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

/* 容器微調 */
.container {
  padding: 1rem; /* 添加內邊距 */
  /* 可以添加背景色或陰影，與 Dashboard 的整體風格統一 */
}

/* 表格樣式優化 - 與 Products.vue 保持一致 */
.table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(56,48,46,0.08);
  background: #fff;
  margin-bottom: 1.5rem;
}

.table th, .table td {
  padding: 10px 14px;
  vertical-align: middle;
  border-top: 1px solid #f0eae6;
  font-size: 0.92rem;
}

.table thead th {
  background: #38302e;
  color: #fff;
  font-weight: bold;
  font-size: 0.97rem;
  border-bottom: 2px solid #a18a7b;
}

.table-striped tbody tr:nth-of-type(even) {
  background-color: #f8f9fa;
}

.table tbody tr:hover {
  background-color: #f3edea;
  transition: background 0.2s;
}

.table td {
  font-size: 0.97rem;
  color: #38302e;
}

/* 標題樣式微調 */
h2 {
  color: var(--dark-brown); /* 深棕色標題 */
  border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
  padding-bottom: 10px; /* 標題與線的間距 */
  margin-bottom: 20px; /* 標題與內容的間距 */
  font-size: 1.18rem;
}

/* 載入中和無資料提示文字樣式 */
.text-muted {
  font-style: italic;
  color: #a18a7b !important;
}

/* 響應式調整表格 */
@media (max-width: 768px) {
  .table-responsive .table {
    /* 在小螢幕上可以考慮不顯示部分欄位或堆疊顯示 */
  }
}

.price-currency {
  font-size: 0.82em;
  color: #a18a7b;
  margin-right: 2px;
  white-space: nowrap;
  vertical-align: middle;
}

</style>