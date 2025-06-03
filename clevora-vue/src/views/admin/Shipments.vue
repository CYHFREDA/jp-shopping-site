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
            <td colspan="6" class="text-center">沒有找到出貨資料。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';

const shipments = ref([]);
const userStore = useUserStore();

async function loadShipments() {
  const token = userStore.token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await fetch('/admin/shipments', {
      headers: { "Authorization": "Basic " + token }
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error('無法載入出貨資料：', res.status, errorText);
      alert('無法載入出貨資料！');
      return;
    }

    shipments.value = await res.json();
  } catch (error) {
    console.error('載入出貨資料時發生錯誤：', error);
    alert('載入出貨資料時發生錯誤！');
  }
}

async function editShipment(shipmentId) {
  const recipient_name = prompt("請輸入收件人姓名：");
  if (!recipient_name) { alert("❌ 請輸入收件人姓名！"); return; }

  const address = prompt("請輸入收件人地址：");
  if (!address) { alert("❌ 請輸入收件人地址！"); return; }

  const status = prompt("請輸入狀態（pending, shipped, completed）：", "shipped");
  if (!status) { alert("❌ 請輸入狀態！"); return; }

  const token = userStore.token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  try {
    const res = await fetch('/admin/update_shipment', {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Basic " + token },
      body: JSON.stringify({ shipment_id: shipmentId, recipient_name, address, status })
    });

    const result = await res.json();

    if (!res.ok) {
       console.error('更新出貨資料失敗：', result);
       alert(result.error || '更新出貨資料失敗！');
    } else {
       alert(result.message || '出貨資料更新成功！');
       loadShipments(); // 更新成功後重新載入出貨資料
    }

  } catch (error) {
    console.error('更新出貨資料時發生錯誤：', error);
    alert('更新出貨資料時發生錯誤！');
  }
}

onMounted(() => {
  loadShipments();
});
</script>

<style scoped>
/* 可以添加一些 Shipments.vue 特有的樣式 */
/* Add specific styles for table header from admin.css */
.table-dark th {
  background-color: #4a69bd;
  color: #fff;
}
</style> 