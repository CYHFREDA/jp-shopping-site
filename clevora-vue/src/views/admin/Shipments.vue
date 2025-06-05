<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">🚚 出貨管理</h5>
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

async function loadShipments() {
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.get('/api/admin/shipments');

    shipments.value = res.data;

  } catch (error) {
    console.error('載入出貨資料時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
        alert(error.response.data.error);
     } else if (error.response && error.response.status === 401) {
        alert('認證失敗，請重新登入！');
     } else {
        alert('載入出貨資料時發生未知錯誤！');
     }
  }
}

async function editShipment(shipmentId) {
  const shipmentToEdit = shipments.value.find(s => s.shipment_id === shipmentId);
  if (!shipmentToEdit) return;

  const recipient_name = prompt("請輸入收件人姓名：", shipmentToEdit.recipient_name);
  if (!recipient_name) { alert("❌ 請輸入收件人姓名！"); return; }

  const address = prompt("請輸入收件人地址：", shipmentToEdit.address);
  if (!address) { alert("❌ 請輸入收件人地址！"); return; }

  const status = prompt("請輸入狀態（pending, shipped, completed）：", shipmentToEdit.status);
  if (!status) { alert("❌ 請輸入狀態！"); return; }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
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
       alert(result.message || '出貨資料更新成功！');
       loadShipments();
    } else {
       console.error('更新出貨資料失敗：', result);
       alert(result.error || '更新出貨資料失敗！');
    }

  } catch (error) {
    console.error('更新出貨資料時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
        alert(error.response.data.error);
     } else if (error.response && error.response.status === 401) {
        alert('認證失敗，請重新登入！');
     } else {
        alert('更新出貨資料時發生未知錯誤！');
     }
  }
}

onMounted(() => {
  loadShipments();
});
</script>

<style scoped>
.card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
   margin-top: 1.5rem;
}

.table {
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
   margin-bottom: 1rem;
}

.table th,
.table td {
  padding: 12px 15px;
  border-top: 1px solid #e0e0e0;
}

.table thead th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: bold;
  border-bottom: 2px solid #dee2e6;
}

.table-striped tbody tr:nth-of-type(even) {
  background-color: #f2f2f2;
}

.table tbody tr:hover {
  background-color: #e9ecef;
}

.card-title {
  color: #343a40;
  padding-bottom: 10px;
  margin-bottom: 20px;
   font-size: 1.5rem;
}

.text-muted {
  font-style: italic;
}
</style> 