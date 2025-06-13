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
            <div><strong>地址：</strong>{{ shipment.address }}</div>
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
              <button class="btn btn-secondary mt-3 ms-2" @click="initiateReturn" :disabled="confirming">申請退貨</button>
              <span v-if="confirmSuccess" class="text-success ms-3">已完成！</span>
              <span v-if="confirmError" class="text-danger ms-3">{{ confirmError }}</span>
            </div>
            <div v-else-if="shipment.status === 'returned_pending'">
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
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
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
const returnStoreName = ref('');
const returnTrackingNumber = ref('');

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
  if (status === 'returned_pending') return '退貨申請中';
  return status;
}

function onStoreSelect(store) {
  returnStoreName.value = store.store;
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
  confirming.value = true;
  confirmError.value = '';
  try {
    const token = customerStore.token;
    if (!token) {
      confirmError.value = '未找到認證 token！請重新登入。';
      return;
    }
    await axios.post(`/api/orders/${order_id}/return`, {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    shipment.value.status = 'returned_pending';
    confirmSuccess.value = true;
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
  if (!returnStoreName.value) {
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
    
    const res = await axios.post(`/api/orders/${order_id}/set-return-logistics`, {
      return_store_name: returnStoreName.value
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    confirmSuccess.value = true;
    shipment.value.return_tracking_number = res.data.tracking_number;
    shipment.value.return_store_name = returnStoreName.value;

    confirmError.value = '';
    await loadShipmentDetail();
  } catch (e) {
    console.error('確認門市失敗：', e);
    confirmError.value = e.response?.data?.error || e.message || '確認門市失敗，請稍後再試！';
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
  await loadOrderDetail();
  await loadShipmentDetail();
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
</style> 