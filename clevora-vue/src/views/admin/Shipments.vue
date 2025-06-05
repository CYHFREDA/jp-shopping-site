<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">�� 出貨管理</h5>
    <div v-if="displayErrorMessage" class="alert alert-danger text-center mb-3" role="alert">
      {{ displayErrorMessage }}
    </div>
    <div class="table-responsive">
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
            <td>
              <button class="btn btn-primary btn-sm" @click="editShipment(shipment.shipment_id)">修改</button>
            </td>
          </tr>
          <tr v-if="shipments.length === 0">
            <td colspan="6" class="text-center text-muted">沒有找到出貨資料。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api';

const shipments = ref([]);
const userStore = useUserStore();
const displayErrorMessage = ref('');

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
  }
}

async function editShipment(shipmentId) {
  const shipmentToEdit = shipments.value.find(s => s.shipment_id === shipmentId);
  if (!shipmentToEdit) return;

  const recipient_name = prompt("請輸入收件人姓名：", shipmentToEdit.recipient_name);
  if (!recipient_name) { displayErrorMessage.value = "❌ 請輸入收件人姓名！"; return; }

  const address = prompt("請輸入收件人地址：", shipmentToEdit.address);
  if (!address) { displayErrorMessage.value = "❌ 請輸入收件人地址！"; return; }

  const status = prompt("請輸入狀態（pending, shipped, completed）：", shipmentToEdit.status);
  if (!status) { displayErrorMessage.value = "❌ 請輸入狀態！"; return; }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     displayErrorMessage.value = '❌ 請先登入！';
     return;
  }

  try {
    const res = await api.post('/api/admin/update_shipment', {
      shipment_id: shipmentId,
      recipient_name: recipient_name,
      address: address,
      status: status
    });

    const result = res.data;

    if (res.status === 200) {
       displayErrorMessage.value = result.message || '✅ 出貨資料更新成功！';
       loadShipments();
    } else {
       console.error('更新出貨資料失敗：', result);
       displayErrorMessage.value = result.error || '❌ 更新出貨資料失敗！';
    }

  } catch (error) {
    console.error('更新出貨資料時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
        displayErrorMessage.value = error.response.data.error;
     } else if (error.response && error.response.status === 401) {
        displayErrorMessage.value = '❌ 認證失敗，請重新登入！';
     } else {
        displayErrorMessage.value = '❌ 更新出貨資料時發生未知錯誤！';
     }
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
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid var(--light-grey); /* 淺灰色邊框 */
  border-radius: 8px;
  overflow: hidden; /* 確保圓角生效 */
   margin-bottom: 1rem; /* 添加底部間距 */
   background-color: var(--white); /* 表格背景色 */
}

.table th,
.table td {
  padding: 12px 15px; /* 調整單元格內邊距 */
  border-top: 1px solid var(--light-grey); /* 單元格頂部邊框 */
}

.table thead th {
  background-color: var(--dark-brown); /* 表頭背景色 */
  color: var(--white); /* 表頭文字顏色 */
  font-weight: bold;
  border-bottom: 2px solid var(--light-brown); /* 表頭底部邊框 */
}

/* 偶數行條紋 */
.table-striped tbody tr:nth-of-type(even) {
  background-color: var(--light-grey); /* 淺灰色條紋 */
}

/* 懸停效果 */
.table tbody tr:hover {
  background-color: var(--medium-grey); /* 懸停時變色 */
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
  color: #6c757d !important; /* 保持灰色，與棕色調協調 */
}
</style> 