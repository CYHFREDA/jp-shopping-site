<template>
  <main class="container my-5">
    <h1 class="text-center mb-4"><i class="fas fa-history"></i> 我的訂單</h1>

    <div v-if="loading" class="text-center text-muted">載入中...</div>

    <div v-else-if="error" class="alert alert-danger text-center">{{ error }}</div>

    <div v-else-if="orders.length === 0" class="text-center text-muted">您還沒有任何訂單。</div>

    <div v-else>
      <div class="table-responsive">
        <table class="table table-bordered table-striped align-middle">
          <thead class="table-dark">
            <tr>
              <th>訂單編號</th>
              <th>訂單日期</th>
              <th>總金額</th>
              <th>狀態</th>
              <th>商品清單</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.order_id">
              <td>{{ order.order_id }}</td>
              <td>{{ formatDateTime(order.created_at) }}</td>
              <td>NT$ {{ order.amount }}</td>
              <td>
                <span 
                  class="badge"
                  :class="{
                    'bg-secondary': order.status === 'pending',
                    'bg-success': order.status === 'success',
                    'bg-danger': order.status === 'fail'
                  }"
                >
                  {{ order.status === 'pending' ? '待處理' : order.status === 'success' ? '成功' : '失敗' }}
                </span>
              </td>
              <td>
                <ul class="list-unstyled mb-0">
                  <li v-for="item in order.item_names.split('#')" :key="item">{{ item }}</li>
                </ul>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useCustomerStore } from '@/stores/customerStore';
import { ordersAPI } from '@/services/api';

const orders = ref([]);
const loading = ref(true);
const error = ref(null);
const customerStore = useCustomerStore();

// 格式化日期時間
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleString();
}

onMounted(async () => {
  console.log('OrderHistory.vue mounted.');
  console.log('isAuthenticated:', customerStore.isAuthenticated);
  console.log('customer_id:', customerStore.customer?.customer_id);
  console.log('customerStore.customer:', customerStore.customer);
  
  // 確保客戶已登入且 customer_id 可用
  if (!customerStore.isAuthenticated || !customerStore.customer?.customer_id) {
    error.value = '請先登入以查看訂單記錄。';
    loading.value = false;
    return;
  }

  let retryCount = 0;
  const maxRetries = 3;

  const loadOrders = async () => {
    try {
      const customerId = customerStore.customer.customer_id;
      console.log('正在請求訂單資料，customerId:', customerId);
      
      // 添加請求超時設置
      const response = await Promise.race([
        ordersAPI.getCustomerOrders(customerId),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('請求超時')), 10000)
        )
      ]);
      
      console.log('訂單資料響應：', response);
      console.log('訂單資料：', response.data);
      
      if (Array.isArray(response.data)) {
        orders.value = response.data;
      } else {
        console.error('訂單資料格式不正確：', response.data);
        error.value = '訂單資料格式不正確，請聯繫客服。';
      }
    } catch (err) {
      console.error('載入訂單記錄錯誤：', err);
      console.error('錯誤詳情：', {
        message: err.message,
        response: err.response,
        request: err.request
      });

      if (err.response) {
        if (err.response.status === 401) {
          error.value = '認證已過期，請重新登入。';
          customerStore.logout();
        } else if (err.response.status === 404) {
          error.value = '找不到訂單記錄。';
        } else if (err.response.status >= 500) {
          if (retryCount < maxRetries) {
            retryCount++;
            console.log(`重試載入訂單 (${retryCount}/${maxRetries})...`);
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
            return loadOrders();
          }
          error.value = '伺服器錯誤，請稍後再試。';
        } else {
          error.value = '載入訂單記錄失敗，請稍後再試。';
        }
      } else if (err.message === '請求超時') {
        if (retryCount < maxRetries) {
          retryCount++;
          console.log(`重試載入訂單 (${retryCount}/${maxRetries})...`);
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
          return loadOrders();
        }
        error.value = '載入訂單超時，請稍後再試。';
      } else {
        error.value = '載入訂單記錄失敗，請稍後再試或聯繫客服。';
      }
    } finally {
      loading.value = false;
    }
  };

  await loadOrders();
});

</script>

<style scoped>
/* 在這裡添加 OrderHistory.vue 特有的樣式 */
.table th,
.table td {
  vertical-align: middle;
}

/* 可以根據需要調整表格列寬度 */
/*
.table th:nth-child(1) { width: 150px; }
.table th:nth-child(2) { width: 180px; }
.table th:nth-child(3) { width: 100px; }
.table th:nth-child(4) { width: 80px; }
.table th:nth-child(5) {  }
*/

@media (max-width: 768px) {
  .table thead {
    display: none;
  }
  .table tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid #dee2e6;
    border-radius: 0.25rem;
  }
  .table td {
    display: block;
    text-align: right;
    position: relative;
    padding-left: 50%;
    text-align: left;
    border: none;
  }
  .table td::before {
    position: absolute;
    top: 0;
    left: 12px;
    width: 45%;
    padding-right: 10px;
    white-space: nowrap;
    font-weight: bold;
  }
  .table td:nth-of-type(1)::before { content: "訂單編號"; }
  .table td:nth-of-type(2)::before { content: "訂單日期"; }
  .table td:nth-of-type(3)::before { content: "總金額"; }
  .table td:nth-of-type(4)::before { content: "狀態"; }
  .table td:nth-of-type(5)::before { content: "商品清單"; }

  .table td:first-child {
    border-top-left-radius: 0.25rem;
    border-top-right-radius: 0.25rem;
  }
  .table td:last-child {
    border-bottom-left-radius: 0.25rem;
    border-bottom-right-radius: 0.25rem;
    border-bottom: none; /* 最後一個 td 不需要底部邊框 */
  }

  .table tr td:first-child {
    border-top: 1px solid #dee2e6; /* 在小螢幕上為每個訂單的開頭添加頂部邊框 */
  }
}

</style> 