<template>
  <div class="container mt-4">
    <h2 class="mb-3">📦 訂單管理</h2>
    <div v-if="isLoading" class="text-center text-muted">載入中...</div>
    <div v-else>
      <div class="table-responsive">
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
              <td>NT$ {{ order.amount }}</td>
              <td>{{ order.item_names ? order.item_names : '無商品內容' }}</td>
              <td>{{ order.status }}</td>
              <td>{{ order.created_at }}</td>
              <td>{{ order.paid_at || '尚未付款' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="orders.length === 0" class="text-center text-muted">目前沒有訂單</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';

const router = useRouter();
const orders = ref([]);
const isLoading = ref(true);
const userStore = useUserStore();

const loadOrders = async () => {
  const token = userStore.admin_token;
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

onMounted(() => {
  loadOrders();
});
</script>

<style scoped>
/* 表格樣式優化 */
.table {
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden; /* 確保圓角生效 */
  margin-bottom: 1rem; /* 添加底部間距 */
}

.table th,
.table td {
  padding: 12px 15px; /* 調整單元格內邊距 */
  border-top: 1px solid #e0e0e0;
}

.table thead th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: bold;
  border-bottom: 2px solid #dee2e6;
}

/* 偶數行條紋 */
.table-striped tbody tr:nth-of-type(even) {
  background-color: #f2f2f2;
}

/* 懸停效果 */
.table tbody tr:hover {
  background-color: #e9ecef;
}

/* 標題樣式微調 */
h2 {
  color: #343a40; /* 深色標題 */
  border-bottom: 2px solid #007bff; /* 底部裝飾線 */
  padding-bottom: 10px; /* 標題與線的間距 */
  margin-bottom: 20px; /* 標題與內容的間距 */
}

/* 載入中和無資料提示文字樣式 */
.text-muted {
  font-style: italic;
}
</style>