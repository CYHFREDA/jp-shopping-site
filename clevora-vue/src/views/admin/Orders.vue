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
import api from '@/services/api';

const orders = ref([]);
const userStore = useUserStore();

async function loadOrders() {
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.get('/admin/orders');
    orders.value = res.data;
  } catch (error) {
    console.error('載入訂單時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else {
      alert('載入訂單失敗，請稍後再試！');
    }
  }
}

async function updateOrderStatus(orderId, status) {
  if (!status) return;
  
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.post('/admin/update_order_status', {
      order_id: orderId,
      status: status
    });

    if (res.data.message) {
      alert(res.data.message);
      await loadOrders(); // 重新載入訂單列表
    }
  } catch (error) {
    console.error('更新訂單狀態時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else {
      alert('更新訂單狀態失敗，請稍後再試！');
    }
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