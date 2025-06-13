<template>
  <main class="container my-5 order-history-page-container">
    <h1 class="text-center mb-4 page-title"><i class="fas fa-history"></i> 我的訂單</h1>

    <div v-if="loading" class="text-center text-muted loading-message">載入中...</div>

    <div v-else-if="error" class="alert alert-danger text-center error-message">{{ error }}</div>

    <div v-if="displayErrorMessage" class="alert alert-danger text-center mt-3" role="alert">
      {{ displayErrorMessage }}
    </div>

    <div v-else-if="orders.length === 0" class="text-center text-muted empty-message">您還沒有任何訂單。</div>

    <div v-else>
      <!-- 桌機版表格 -->
      <div class="table-responsive d-none d-md-block">
        <table class="table table-bordered table-striped align-middle order-history-table">
          <thead>
            <tr>
              <th>訂單編號</th>
              <th>訂單日期</th>
              <th>總金額</th>
              <th>商品數量</th>
              <th>狀態</th>
              <th>商品清單</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.order_id">
              <td>{{ order.order_id }}</td>
              <td class="nowrap">{{ formatDateTime(order.created_at) }}</td>
              <td>
                <span>NT$</span>
                <span>{{ order.amount }}</span>
              </td>
              <td>{{ getOrderItemCount(order.item_names) }}</td>
              <td>
                <span 
                  class="badge"
                  :class="{
                    'bg-secondary': order.status === 'pending',
                    'bg-success': order.status === 'success',
                    'bg-danger': order.status === 'fail'
                  }"
                >
                  {{ statusText(order.status) }}
                </span>
              </td>
              <td>
                <template v-if="order.item_names">
                  {{ order.item_names.split('#')[0] }}
                  <template v-if="order.item_names.split('#').length > 1">
                    ...等{{ order.item_names.split('#').length }}項
                  </template>
                </template>
              </td>
              <td>
                <router-link :to="`/orderDetail/${order.order_id}`" class="btn btn-outline-primary btn-sm me-1">查看</router-link>
                <button 
                  v-if="order.status === 'arrived'"
                  class="btn btn-success btn-sm"
                  @click="completePickup(order.order_id)"
                >
                  完成取貨
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 手機版卡片 -->
      <div class="d-block d-md-none">
        <div v-for="order in orders" :key="order.order_id" class="card mb-3 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <strong>訂單編號：</strong>{{ order.order_id }}
              </div>
              <span class="badge"
                :class="{
                  'bg-secondary': order.status === 'pending',
                  'bg-success': order.status === 'success',
                  'bg-danger': order.status === 'fail'
                }"
              >
                {{ statusText(order.status) }}
              </span>
            </div>
            <div class="mb-2">
              <strong>訂單日期：</strong>{{ formatDateTime(order.created_at) }}
            </div>
            <div class="mb-2">
              <strong>總金額：</strong><br><span>NT$</span><br><span>{{ order.amount }}</span>
            </div>
            <div class="mb-2">
              <strong>商品數量：</strong>{{ getOrderItemCount(order.item_names) }}
            </div>
            <div class="mb-2">
              <strong>商品清單：</strong>
              <template v-if="order.item_names">
                {{ order.item_names.split('#')[0] }}
                <template v-if="order.item_names.split('#').length > 1">
                  ...等{{ order.item_names.split('#').length }}項
                </template>
              </template>
            </div>
            <div class="text-end mt-3">
              <router-link :to="`/orderDetail/${order.order_id}`" class="btn btn-outline-primary btn-sm me-1">查看</router-link>
              <button 
                v-if="order.status === 'arrived'"
                class="btn btn-success btn-sm"
                @click="completePickup(order.order_id)"
              >
                完成取貨
              </button>
            </div>
          </div>
        </div>
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
const displayErrorMessage = ref(null);

// 格式化日期時間
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  // 轉換為台灣時區（+8）
  const twDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  return twDate.toLocaleString('zh-TW', { hour12: false });
}

// 計算商品數量
function getOrderItemCount(itemNames) {
  if (!itemNames) return 0;
  return itemNames.split('#').reduce((sum, item) => {
    const match = item.match(/x\s*(\d+)/);
    return sum + (match ? parseInt(match[1]) : 1);
  }, 0);
}

// 新增 statusText 函式
function statusText(status) {
  if (status === 'pending') return '待處理';
  if (status === 'success') return '成功';
  if (status === 'fail') return '失敗';
  // 新增出貨狀態對應
  if (status === 'out_of_stock') return '缺貨中';
  if (status === 'shipped') return '已出貨';
  if (status === 'arrived') return '已到店';
  if (status === 'completed') return '已完成';
  if (status === 'returned_pending') return '退貨申請中';
  return status;
}

async function completePickup(orderId) {
  try {
    // 確保客戶已登入且 customer_id 可用
    if (!customerStore.isAuthenticated || !customerStore.customer?.customer_id) {
      displayErrorMessage.value = '請先登入才能完成取貨。';
      return;
    }
    const token = customerStore.customer_token;
    if (!token) {
      displayErrorMessage.value = '未找到認證 token！請重新登入。';
      return;
    }

    const res = await ordersAPI.completeShipment(orderId, token);
    displayErrorMessage.value = res.data.message || '✅ 完成取貨成功！';
    // 重新載入訂單以更新狀態
    await onMounted(); // 重新觸發 onMounted 中的 loadOrders 邏輯
  } catch (error) {
    console.error('完成取貨失敗：', error);
    displayErrorMessage.value = error.response?.data?.error || error.message || '❌ 完成取貨失敗！';
  }
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
        if (err.response.data?.detail === 'KICKED') {
          displayErrorMessage.value = '您的帳號已在其他地方登入。';
        } else if (err.response.data?.detail === '認證令牌已過期') {
          displayErrorMessage.value = '登入已過期，請重新登入。';
        } else {
          displayErrorMessage.value = '請重新登入。';
        }
      } else {
        error.value = '載入訂單記錄失敗，請稍後再試。';
      }
    } else if (err.message === '請求超時') {
      error.value = '載入訂單記錄超時，請稍後再試。';
    } else {
      error.value = '發生未知錯誤，請稍後再試。';
    }
  } finally {
    loading.value = false;
  }
});

</script>

<style scoped>
.order-history-page-container {
  background-color: var(--white); /* 容器背景色 */
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 30px;
  border: 1px solid var(--medium-grey); /* 添加邊框 */
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
/* .order-history-table 將應用 main.css 中的 .table 規則 */
.order-history-table {
  /* 可以在這裡添加訂單歷史表格特有的樣式，但盡量利用全局樣式 */
}

/* 移除 Bootstrap 默認的 table-striped 樣式 */
.order-history-table.table-striped tbody tr:nth-of-type(odd) {
    background-color: var(--white); /* 奇數行白色背景 */
}

/* 狀態徽章顏色 */
.badge {
  font-size: 0.9em;
}

.badge.bg-secondary {
    background-color: var(--info-color) !important; /* Pending 狀態使用 info 灰色 */
}

.badge.bg-success {
    background-color: var(--success-color) !important; /* Success 狀態使用綠色 */
}

.badge.bg-danger {
    background-color: var(--danger-color) !important; /* Fail 狀態使用紅色 */
}

/* 商品清單樣式 */
.order-history-table ul {
    padding-left: 20px; /* 添加左邊距 */
    text-align: left; /* 左對齊 */
    margin-bottom: 0; /* 移除底部默認間距 */
}

.order-history-table li {
    word-break: break-word; /* 長單字換行 */
}

/* 載入中、錯誤、空狀態提示文字樣式 - 應用 main.css 的 .text-muted */
.loading-message,
.empty-message {
    font-style: italic;
    color: var(--disabled-text); /* 使用禁用文字顏色 */
    margin-top: 40px; /* 添加頂部間距 */
    font-size: 1.2rem;
}

.error-message {
    /* 繼承 main.css 中的 .alert 和 .alert-danger 樣式 */
    margin-top: 20px;
}

/* RWD 調整 */
@media (max-width: 768px) {
    .order-history-page-container {
        padding: 20px; /* 小螢幕調整內邊距 */
    }

    .page-title {
        font-size: 1.8rem; /* 小螢幕調整字體大小 */
    }

    /* 表格在小螢幕下的響應式處理主要依靠 .table-responsive */
}

/* 防止表格日期欄位換行 */
.nowrap {
  white-space: nowrap;
}
</style> 