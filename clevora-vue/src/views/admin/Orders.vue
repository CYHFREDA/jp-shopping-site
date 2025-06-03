<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">📦 訂單管理</h5>
    <div class="table-responsive">
      <table class="table table-striped table-bordered">
        <thead class="table-dark">
          <tr>
            <th>訂單編號</th>
            <th>商品內容</th>
            <th>金額</th>
            <th>狀態</th>
            <th>建立時間</th>
            <th>付款時間</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.order_id">
            <td>{{ order.order_id }}</td>
            <td>{{ order.item_names }}</td>
            <td>{{ order.amount }}</td>
            <td>{{ order.status }}</td>
            <td>{{ order.created_at }}</td>
            <td>{{ order.paid_at || '-' }}</td>
            <td>
              <select @change="updateOrderStatus(order.order_id, $event.target.value)" class="form-select form-select-sm">
                <option value="">--修改狀態--</option>
                <option value="pending">pending</option>
                <option value="success">success</option>
                <option value="fail">fail</option>
              </select>
            </td>
          </tr>
          <tr v-if="orders.length === 0">
            <td colspan="7" class="text-center">沒有找到訂單。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';

const orders = ref([]);
const userStore = useUserStore();

async function loadOrders() {
  const token = userStore.token;
  if (!token) {
    // 如果沒有 token，可能需要導向登入頁面或顯示錯誤訊息
    console.error('未找到認證 token！');
    return;
  }

  try {
    const res = await fetch('/admin/orders', {
      headers: { "Authorization": "Basic " + token }
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error('無法載入訂單：', res.status, errorText);
      alert('❌ 無法載入訂單！');
      return;
    }

    orders.value = await res.json();
  } catch (error) {
    console.error('載入訂單時發生錯誤：', error);
    alert('載入訂單時發生錯誤！');
  }
}

async function updateOrderStatus(orderId, newStatus) {
  if (!newStatus) return;

  const token = userStore.token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  try {
    const res = await fetch('/admin/update_order_status', {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Basic " + token },
      body: JSON.stringify({ order_id: orderId, status: newStatus })
    });

    const result = await res.json();

    if (!res.ok) {
       console.error('更新訂單狀態失敗：', result);
       alert(result.error || '更新訂單狀態失敗！');
    } else {
       alert(result.message || '訂單狀態更新成功！');
       loadOrders(); // 更新成功後重新載入訂單
    }

  } catch (error) {
    console.error('更新訂單狀態時發生錯誤：', error);
    alert('更新訂單狀態時發生錯誤！');
  }
}

onMounted(() => {
  loadOrders();
});
</script>

<style scoped>
/* 可以添加一些 Orders.vue 特有的樣式 */
/* Add specific styles for table header from admin.css */
.table-dark th {
  background-color: #4a69bd;
  color: #fff;
}
</style>