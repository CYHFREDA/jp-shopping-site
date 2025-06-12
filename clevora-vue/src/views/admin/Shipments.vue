<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">🚚 出貨管理</h5>
    <div v-if="displayErrorMessage" class="alert alert-danger text-center mb-3" role="alert">
      {{ displayErrorMessage }}
    </div>
    <div v-if="isLoading" class="text-center text-muted">載入中...</div>
    <div v-else>
      <!-- 桌機版表格 -->
      <div class="table-responsive d-none d-md-block">
        <table class="table table-striped table-bordered">
          <thead class="table-dark">
            <tr>
              <th>出貨編號</th>
              <th>訂單編號</th>
              <th>收件人</th>
              <th>地址</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="shipment in shipments" :key="shipment.shipment_id">
              <td>{{ shipment.shipment_id }}</td>
              <td>{{ shipment.order_id }}</td>
              <td>{{ shipment.recipient_name }}</td>
              <td>{{ shipment.address }}</td>
              <td>{{ statusText(shipment.status) }}</td>
              <td class="text-center">
                <div class="action-btns flex-row gap-2">
                  <button class="btn btn-sm btn-brown" @click="openEditModal(shipment)" :disabled="mockLoadingOrderId === shipment.order_id || shipment.status === 'completed'">修改</button>
                  <button class="btn btn-sm btn-outline-success" @click="mockDelivered(shipment)" :disabled="mockLoadingOrderId === shipment.order_id || shipment.status === 'arrived' || shipment.status === 'completed' || shipment.status === 'out_of_stock' || shipment.status === 'pending' || shipment.status === 'picked_up'">
                    <span v-if="mockLoadingOrderId === shipment.order_id">處理中...</span>
                    <span v-else>模擬到店</span>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="shipments.length === 0">
              <td colspan="6" class="text-center text-muted">沒有找到出貨資料。</td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 手機版卡片 -->
      <div class="d-block d-md-none">
        <AdminCardList :items="shipments" :fields="cardFields" key-field="shipment_id">
          <template #actions="{ item }">
            <button class="btn btn-sm btn-brown" @click="openEditModal(item)" :disabled="mockLoadingOrderId === item.order_id || item.status === 'completed'">修改</button>
            <button class="btn btn-sm btn-outline-success ms-1" @click="mockDelivered(item)" :disabled="mockLoadingOrderId === item.order_id || item.status === 'arrived' || item.status === 'completed' || item.status === 'out_of_stock' || item.status === 'pending' || item.status === 'picked_up'">
              <span v-if="mockLoadingOrderId === item.order_id">處理中...</span>
              <span v-else>模擬到店</span>
            </button>
          </template>
        </AdminCardList>
      </div>
    </div>
    <!-- 編輯出貨 Modal -->
    <div class="modal fade" :class="{ show: showEditModal }" tabindex="-1" style="display: block;" v-if="showEditModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">編輯出貨資料</h5>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">收件人</label>
              <input v-model="editShipmentData.recipient_name" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">地址</label>
              <input v-model="editShipmentData.address" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">狀態</label>
              <select v-model="editShipmentData.status" class="form-control">
                <option value="pending">待出貨</option>
                <option value="out_of_stock">缺貨中</option>
                <option value="shipped">已出貨</option>
                <option value="arrived">已到店</option>
                <option value="completed">已完成</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" @click="closeEditModal">取消</button>
            <button type="button" class="btn btn-primary btn-sm" @click="saveEditShipment">儲存</button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api';
import AdminCardList from '@/components/AdminCardList.vue';

const shipments = ref([]);
const userStore = useUserStore();
const displayErrorMessage = ref('');
const INACTIVITY_TIMEOUT = 30 * 60 * 1000;
const isLoading = ref(true);
const showEditModal = ref(false);
const editShipmentData = ref({ shipment_id: '', recipient_name: '', address: '', status: '' });
const mockLoadingOrderId = ref(null);

const cardFields = [
  { key: 'shipment_id', label: '出貨單ID' },
  { key: 'order_id', label: '訂單編號' },
  { key: 'recipient_name', label: '收件人' },
  { key: 'address', label: '地址' },
  { key: 'status', label: '狀態' },
  { key: 'created_at', label: '建立時間' },
];

async function loadShipments() {
  displayErrorMessage.value = '';
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayErrorMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.get('/api/admin/shipments');

    shipments.value = res.data;

  } catch (error) {
    console.error('載入出貨資料時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
        displayErrorMessage.value = error.response.data.error;
     } else if (error.response && error.response.status === 401) {
        displayErrorMessage.value = '❌ 認證失敗，請重新登入！';
     } else {
        displayErrorMessage.value = '❌ 載入出貨資料時發生未知錯誤！';
     }
  } finally {
    isLoading.value = false;
  }
}

function openEditModal(shipment) {
  editShipmentData.value = { ...shipment };
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
}

async function saveEditShipment() {
  const { shipment_id, recipient_name, address, status } = editShipmentData.value;
  if (!recipient_name || !address || !status) {
    displayErrorMessage.value = '❌ 請填寫完整資料！';
    return;
  }
  const token = userStore.admin_token;
  if (!token) {
    displayErrorMessage.value = '❌ 請先登入！';
    return;
  }
  try {
    const res = await api.post('/api/admin/update_shipment', {
      shipment_id,
      recipient_name,
      address,
      status
    });
    const result = res.data;
    if (res.status === 200) {
      displayErrorMessage.value = result.message || '✅ 出貨資料更新成功！';
      loadShipments();
      showEditModal.value = false;
    } else {
      displayErrorMessage.value = result.error || '❌ 更新出貨資料失敗！';
    }
  } catch (error) {
    displayErrorMessage.value = error.response?.data?.error || error.message || '❌ 更新出貨資料失敗！';
  }
}

async function mockDelivered(shipment) {
  const token = userStore.admin_token;
  if (!token) {
    displayErrorMessage.value = '❌ 請先登入！';
    return;
  }

  // 在前端進行狀態檢查，避免不必要的後端請求
  if (shipment.status === 'arrived' || shipment.status === 'completed' || shipment.status === 'out_of_stock' || shipment.status === 'pending' || shipment.status === 'picked_up') {
    displayErrorMessage.value = '❌ 只有已出貨狀態的訂單才能模擬到店！';
    return;
  }

  mockLoadingOrderId.value = shipment.order_id;
  try {
    const res = await api.post('/api/admin/mock_delivered', { order_id: shipment.order_id });
    displayErrorMessage.value = res.data.message || '✅ 已模擬到店';
    await loadShipments();
  } catch (error) {
    displayErrorMessage.value = error.response?.data?.error || error.message || '❌ 模擬到店失敗！';
  } finally {
    mockLoadingOrderId.value = null;
  }
}

function statusText(status) {
  if (status === 'pending') return '待出貨';
  if (status === 'out_of_stock') return '缺貨中';
  if (status === 'shipped') return '已出貨';
  if (status === 'arrived') return '已到店';
  if (status === 'picked_up') return '已取貨';
  if (status === 'completed') return '已完成';
  return status;
}

onMounted(() => {
  loadShipments();
  displayErrorMessage.value = '';
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

/* 提升卡片的質感 */
.card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: var(--white); /* 使用白色背景 */
   margin-top: 1.5rem; /* 保留一些頂部間距 */
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
  font-size: 0.92rem;
  padding: 10px 14px;
}

.table thead th {
  font-size: 0.97rem;
  background: #38302e;
  color: #fff;
  font-weight: bold;
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

/* 出貨編號欄位寬度縮小 */
.table th:first-child, .table td:first-child {
  min-width: 120px;
  width: 180px;
  max-width: 240px;
  white-space: nowrap;
}

/* 修改按鈕顏色為淺棕色 */
.btn-brown {
  background-color: #a18a7b !important;
  border-color: #a18a7b !important;
  color: #38302e !important;
}
.btn-brown:hover {
  background-color: #f3edea !important;
  border-color: #c8a99a !important;
  color: #38302e !important;
}

/* 標題樣式微調 - 與 Orders.vue 保持一致 */
.card-title {
  color: var(--dark-brown); /* 深棕色標題 */
  border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
  padding-bottom: 10px; /* 標題與線的間距 */
  margin-bottom: 20px; /* 標題與內容的間距 */
  font-size: 1.18rem;
}

/* 無資料提示文字樣式 */
.text-muted {
  font-style: italic;
  color: #a18a7b !important;
}

.modal-backdrop {
  z-index: 1040 !important;
  pointer-events: none !important;
  background: rgba(56, 48, 46, 0.18) !important; /* 柔和棕色半透明 */
}
.modal {
  z-index: 1051 !important;
  background: none;
}
.modal-content {
  background: #fffaf7;
  border-radius: 12px;
  border: 1.5px solid #a18a7b;
  box-shadow: 0 8px 32px rgba(56,48,46,0.18);
}
.modal-header {
  background: #f3edea;
  border-bottom: 1px solid #e9e0d8;
}
.modal-title {
  color: #a18a7b;
  font-weight: bold;
}
.modal-footer {
  background: #f3edea;
  border-top: 1px solid #e9e0d8;
}
.form-control {
  background: #fff;
  border: 1.5px solid #a18a7b;
  color: #38302e;
  border-radius: 6px;
  font-size: 0.97rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-control:focus {
  border-color: #c8a99a;
  box-shadow: 0 0 0 0.15rem rgba(161, 138, 123, 0.15);
}

/* 操作欄標題置中 */
.table th:last-child {
  text-align: center;
  vertical-align: middle;
}
/* 操作欄按鈕美化 */
.action-btns {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 32px;
}
.action-btns .btn {
  height: 32px;
  min-width: 48px;
  padding: 0 12px;
  font-size: 1rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn, .btn-secondary, .btn-primary {
  font-size: 0.97rem !important;
  padding: 0.35rem 1rem !important;
}
</style> 