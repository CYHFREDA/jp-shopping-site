<template>
  <main class="container my-5 order-detail-page-container">
    <h1 class="text-center mb-4 page-title"><i class="fas fa-file-alt"></i> 訂單詳細</h1>
    <div v-if="loading" class="text-center text-muted">載入中...</div>
    <div v-else-if="error" class="alert alert-danger text-center">{{ error }}</div>
    <div v-else>
      <div class="card mb-4">
        <div class="card-body">
          <h5 class="mb-3">訂單資訊</h5>
          <div><strong>訂單編號：</strong>{{ order.order_id }}</div>
          <div><strong>訂單日期：</strong>{{ formatDateTime(order.created_at) }}</div>
          <div><strong>總金額：</strong>NT${{ order.amount }}</div>
          <div>
            <strong>狀態：</strong>
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
          </div>
          <div><strong>商品數量：</strong>{{ getOrderItemCount(order.item_names) }}</div>
        </div>
      </div>
      <div class="card mb-4">
        <div class="card-body">
          <h5 class="mb-3">商品清單</h5>
          <ul class="mb-0">
            <li v-for="item in (order.item_names?.split('#') || [])" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>
      <div class="card">
        <div class="card-body">
          <h5 class="mb-3">出貨狀態</h5>
          <div v-if="shipmentLoading" class="text-muted">查詢中...</div>
          <div v-else-if="shipmentError" class="text-danger">{{ shipmentError }}</div>
          <div v-else-if="shipment">
            <div><strong>收件人：</strong>{{ shipment.recipient_name }}</div>
            <div>
              <strong>配送方式：</strong>
              <span class="badge" :class="{'bg-info': shipment.delivery_type === 'home', 'bg-warning': shipment.delivery_type === 'cvs'}">
                {{ shipment.delivery_type === 'home' ? '宅配到府' : '超商取貨' }}
              </span>
            </div>
            <!-- 超商取貨資訊 -->
            <template v-if="shipment.delivery_type === 'cvs'">
              <div><strong>取貨門市：</strong>{{ shipment.store_name }}</div>
              <div><strong>門市代號：</strong>{{ shipment.store_id }}</div>
              <div><strong>超商類型：</strong>{{ cvstypeText(shipment.cvs_type) }}</div>
            </template>
            <!-- 宅配資訊 -->
            <template v-else>
              <div><strong>配送地址：</strong>{{ shipment.address }}</div>
            </template>
            <div>
              <strong>出貨狀態：</strong>
              <span 
                class="badge"
                :class="{
                  'bg-info': shipment.status === 'pending',
                  'bg-warning': shipment.status === 'out_of_stock',
                  'bg-primary': shipment.status === 'shipped',
                  'bg-success': shipment.status === 'arrived',
                  'bg-success': shipment.status === 'completed'
                }"
              >
                {{ shipmentStatusText(shipment.status) }}
              </span>
            </div>
            <div><strong>建立時間：</strong>{{ formatDateTime(shipment.created_at) }}</div>
            <div v-if="shipment.status === 'arrived'">
              <button class="btn btn-success mt-3" @click="markPickedUp" :disabled="confirming">{{ confirming ? '送出中...' : '確認取貨' }}</button>
              <span v-if="confirmSuccess" class="text-success ms-3">已完成！</span>
              <span v-if="confirmError" class="text-danger ms-3">{{ confirmError }}</span>
            </div>
            <div v-else-if="shipment.status === 'picked_up'">
              <button class="btn btn-success mt-3" @click="completeOrder" :disabled="confirming">{{ confirming ? '送出中...' : '完成' }}</button>
              <button class="btn btn-secondary mt-3 ms-2" @click="console.log('申請退貨按鈕被點擊！'); initiateReturn()" :disabled="confirming">申請退貨</button>
              <span v-if="confirmSuccess" class="text-success ms-3">已完成！</span>
              <span v-if="confirmError" class="text-danger ms-3">{{ confirmError }}</span>
            </div>
            <div v-else-if="shipment.status === 'return_requested'">
              <span class="text-muted mt-3">退貨申請已送出，等待管理員處理。</span>
              <div v-if="!shipment.return_tracking_number" class="mt-3">
                <h6 class="mb-2">請選擇超商門市以完成退貨流程：</h6>
                <MultiCvsStoreSelector @select="onStoreSelect" />
                <button class="btn btn-primary" @click="confirmReturnLogistics" :disabled="confirming">確認門市</button>
                <span v-if="confirmError" class="text-danger ms-3">{{ confirmError }}</span>
              </div>
              <div v-else class="mt-3">
                <p><strong>退貨物流編號：</strong> {{ shipment.return_tracking_number }}</p>
                <p><strong>退貨門市：</strong> {{ shipment.return_store_name }}</p>
                <span class="text-success">請持退貨物流編號至超商門市寄件。</span>
              </div>
            </div>
            <div v-else-if="shipment.status === 'completed'">
              <span class="text-muted mt-3">此訂單已完成。</span>
            </div>
          </div>
          <div v-else class="text-muted">尚未建立出貨單</div>
        </div>
      </div>
    </div>

    <!-- 退貨原因對話框 -->
    <div v-if="showReturnDialog" class="modal fade show" style="display: block;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">申請退貨</h5>
            <button type="button" class="btn-close" @click="showReturnDialog = false"></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="returnReason" class="form-label">退貨原因</label>
              <textarea 
                id="returnReason" 
                v-model="returnReason" 
                class="form-control" 
                rows="3" 
                placeholder="請填寫退貨原因..."
                readonly="false" 
                key="return-reason-textarea"
                ref="returnReasonTextarea"
                @input="console.log('Return Reason updated:', returnReason)"
                @keydown="console.log('Keydown event on returnReason textarea:', $event.key)"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showReturnDialog = false">取消</button>
            <button type="button" class="btn btn-primary" @click="submitReturn" :disabled="confirming">
              {{ confirming ? '送出中...' : '確認送出' }}
            </button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { useCustomerStore } from '@/stores/customerStore';
import MultiCvsStoreSelector from '@/components/MultiCvsStoreSelector.vue';

const route = useRoute();
const order_id = route.params.order_id;
const order = ref({});
const loading = ref(true);
const error = ref(null);
const customerStore = useCustomerStore();

const shipment = ref(null);
const shipmentLoading = ref(true);
const shipmentError = ref(null);

const confirming = ref(false);
const confirmSuccess = ref(false);
const confirmError = ref('');
const selectedStore = ref(null);
const returnReason = ref('');
const showReturnDialog = ref(false);
const returnReasonTextarea = ref(null);

function formatDateTime(dateTimeString) {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  const twDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  return twDate.toLocaleString('zh-TW', { hour12: false });
}

function statusText(status) {
  if (status === 'pending') return '待處理';
  if (status === 'success') return '成功';
  if (status === 'fail') return '失敗';
  return status;
}

function getOrderItemCount(itemNames) {
  if (!itemNames) return 0;
  return itemNames.split('#').reduce((sum, item) => {
    const match = item.match(/x\s*(\d+)/);
    return sum + (match ? parseInt(match[1]) : 1);
  }, 0);
}

function shipmentStatusText(status) {
  if (status === 'pending') return '待出貨';
  if (status === 'out_of_stock') return '缺貨中';
  if (status === 'shipped') return '已出貨';
  if (status === 'arrived') return '已到店';
  if (status === 'picked_up') return '已取貨';
  if (status === 'completed') return '已完成';
  if (status === 'return_requested') return '退貨申請中';
  if (status === 'return_processing') return '退貨處理中';
  return status;
}

function cvstypeText(type) {
  const mapping = {
    'FAMI': '全家',
    'UNIMART': '7-11',
    'HILIFE': '萊爾富',
    'OKMART': 'OK超商'
  };
  return mapping[type] || type;
}

function onStoreSelect(store) {
  console.log('選擇的門市：', store);
  selectedStore.value = store;
}

async function markPickedUp() {
  confirming.value = true;
  confirmError.value = '';
  try {
    const token = customerStore.token;
    if (!token) {
      confirmError.value = '未找到認證 token！請重新登入。';
      return;
    }
    await axios.post(`/api/orders/${order_id}/mark-picked-up`, {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    shipment.value.status = 'picked_up';
    confirmSuccess.value = true;
    await loadShipmentDetail();
  } catch (e) {
    console.error('確認取貨失敗：', e);
    confirmError.value = e.response?.data?.error || e.message || '狀態更新失敗，請稍後再試';
  } finally {
    confirming.value = false;
  }
}

async function completeOrder() {
  confirming.value = true;
  confirmError.value = '';
  try {
    const token = customerStore.token;
    if (!token) {
      confirmError.value = '未找到認證 token！請重新登入。';
      return;
    }
    await axios.post(`/api/orders/${order_id}/complete`, {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    shipment.value.status = 'completed';
    confirmSuccess.value = true;
    await loadShipmentDetail();
  } catch (e) {
    console.error('完成訂單失敗：', e);
    confirmError.value = e.response?.data?.error || e.message || '狀態更新失敗，請稍後再試';
  } finally {
    confirming.value = false;
  }
}

async function initiateReturn() {
  console.log('Initiate Return function called.');
  showReturnDialog.value = true;
  await nextTick(() => {
    if (returnReasonTextarea.value) {
      returnReasonTextarea.value.focus();
      console.log('Return Reason Textarea disabled:', returnReasonTextarea.value.disabled);
    }
  });
}

async function submitReturn() {
  if (!returnReason.value.trim()) {
    confirmError.value = '請填寫退貨原因';
    return;
  }
  
  console.log('Submitting return reason:', returnReason.value);

  confirming.value = true;
  confirmError.value = '';
  try {
    const token = customerStore.token;
    if (!token) {
      confirmError.value = '未找到認證 token！請重新登入。';
      return;
    }
    await axios.post(`/api/orders/${order_id}/return`, {
      return_reason: returnReason.value.trim()
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    shipment.value.status = 'return_requested';
    confirmSuccess.value = true;
    showReturnDialog.value = false;
    returnReason.value = '';
    await loadShipmentDetail();
  } catch (e) {
    console.error('申請退貨失敗：', e);
    confirmError.value = e.response?.data?.error || e.message || '申請退貨失敗，請稍後再試';
  } finally {
    confirming.value = false;
  }
}

async function confirmReturnLogistics() {
  confirming.value = true;
  confirmError.value = '';
  if (!selectedStore.value) {
    confirmError.value = '請選擇超商門市！';
    confirming.value = false;
    return;
  }

  try {
    const token = customerStore.token;
    if (!token) {
      confirmError.value = '未找到認證 token！請重新登入。';
      confirming.value = false;
      return;
    }
    
    // 檢查必要資訊是否完整
    if (!selectedStore.value.id || !selectedStore.value.name || !selectedStore.value.type) {
      confirmError.value = '門市資訊不完整，請重新選擇！';
      confirming.value = false;
      return;
    }

    console.log('準備送出的門市資料：', {
      store_id: selectedStore.value.id,
      store_name: selectedStore.value.name,
      cvs_type: selectedStore.value.type
    });
    
    const res = await axios.post(`/api/orders/${order_id}/set-return-logistics`, {
      store_id: selectedStore.value.id,
      store_name: selectedStore.value.name,
      cvs_type: selectedStore.value.type
    }, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('綠界回應：', res.data);
    confirmSuccess.value = true;
    shipment.value.return_tracking_number = res.data.logistics_id;
    shipment.value.return_store_name = selectedStore.value.name;

    confirmError.value = '';
    await loadShipmentDetail();
  } catch (e) {
    console.error('確認門市失敗：', e);
    if (e.response?.data?.error) {
      confirmError.value = e.response.data.error;
    } else if (e.message.includes('timeout')) {
      confirmError.value = '請求超時，請稍後再試！';
    } else {
      confirmError.value = '確認門市失敗，請稍後再試！';
    }
  } finally {
    confirming.value = false;
  }
}

onMounted(async () => {
  // 如果不是已登入狀態，嘗試重新連接
  if (!customerStore.isAuthenticated) {
    const reconnected = await customerStore.tryReconnect();
    if (!reconnected) {
      error.value = '登入狀態已過期，請重新登入';
      return;
    }
  }
  console.log('OrderDetail Mounted - Customer Authenticated:', customerStore.isAuthenticated);
  await loadOrderDetail();
  await loadShipmentDetail();
  console.log('OrderDetail Mounted - Shipment Data:', shipment.value);
});

async function loadOrderDetail() {
  try {
    const res = await axios.get(`/api/orders/${order_id}`);
    order.value = res.data;
    loading.value = false;
  } catch (e) {
    error.value = '訂單資料載入失敗';
    loading.value = false;
  }
}

async function loadShipmentDetail() {
  try {
    shipmentLoading.value = true;
    const res = await axios.get(`/api/orders/${order_id}/shipment`);
    if (res.data && res.data.shipment_id) {
      shipment.value = res.data;
    } else {
      shipment.value = null;
    }
    shipmentLoading.value = false;
  } catch (e) {
    shipmentError.value = '查詢出貨資料失敗';
    shipmentLoading.value = false;
  }
}
</script>

<style scoped>
.order-detail-page-container {
  background-color: var(--white);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 30px;
  border: 1px solid var(--medium-grey);
  max-width: 700px;
}
.page-title {
  color: var(--dark-brown);
  border-bottom: 2px solid var(--light-brown);
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 2rem;
  font-weight: bold;
}
.modal {
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050; /* 確保模態框在最前面 */
}

.modal-backdrop {
  z-index: 1040; /* 確保背景在模態框後面 */
}

.modal-body {
  pointer-events: auto !important; /* 確保模態框內部元素可以互動 */
}

/* 確保退貨原因輸入框可互動 */
.modal-body textarea#returnReason {
  pointer-events: auto !important;
  z-index: 9999 !important; /* 確保它在最上層 */
}
</style> 