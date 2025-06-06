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
              <td>{{ shipment.status }}</td>
              <td><button class="btn btn-sm btn-brown" @click="openEditModal(shipment)">修改</button></td>
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
            <button class="btn btn-sm btn-brown" @click="openEditModal(item)">修改</button>
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
                <option value="pending">pending</option>
                <option value="shipped">shipped</option>
                <option value="completed">completed</option>
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
  padding: 16px 18px;
  vertical-align: middle;
  border-top: 1px solid #f0eae6;
}

.table thead th {
  background: #38302e;
  color: #fff;
  font-weight: bold;
  font-size: 1.08rem;
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
  font-size: 1.05rem;
  color: #38302e;
}

/* 按鈕樣式微調 - 與 Products.vue 保持一致 */
.btn {
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

/* 主要按鈕 (修改) */
.btn-primary {
  background-color: var(--light-brown); /* 主要按鈕背景色 */
  border-color: var(--light-brown); /* 主要按鈕邊框顏色 */
  color: var(--dark-brown); /* 主要按鈕文字顏色 */
}

.btn-primary:hover {
  background-color: var(--accent-brown); /* 主要按鈕懸停背景色 */
  border-color: var(--accent-brown); /* 主要按鈕懸停邊框顏色 */
  color: var(--white); /* 主要按鈕懸停文字顏色 */
}

/* 標題樣式微調 - 與 Orders.vue 保持一致 */
.card-title {
  color: var(--dark-brown); /* 深棕色標題 */
  border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
  padding-bottom: 10px; /* 標題與線的間距 */
  margin-bottom: 20px; /* 標題與內容的間距 */
   font-size: 1.5rem; /* 保持原有的字體大小 */
}

/* 無資料提示文字樣式 */
.text-muted {
  font-style: italic;
  color: #a18a7b !important;
}
</style> 