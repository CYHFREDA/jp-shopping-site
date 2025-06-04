<template>
  <div class="container mt-4">
    <h2 class="mb-3">訂單管理</h2>
    <div v-if="isLoading" class="text-center">載入中...</div>
    <div v-else>
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>訂單編號</th>
            <th>金額</th>
            <th>商品內容</th>
            <th>狀態</th>
            <th>建立時間</th>
            <th>付款時間</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.order_id">
            <td>{{ order.order_id }}</td>
            <td>NT$ {{ order.amount }}</td>
            <td>{{ order.item_names }}</td>
            <td>{{ order.status }}</td>
            <td>{{ order.created_at }}</td>
            <td>{{ order.paid_at || '尚未付款' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="orders.length === 0" class="text-muted">目前沒有訂單</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const orders = ref([]);
const isLoading = ref(true);

const loadOrders = async () => {
  const token = localStorage.getItem('adminToken');
  if (!token) {
    alert('請先登入後台');
    router.push('/admin/login');
    return;
  }

  try {
    const res = await axios.get('/admin/orders', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    orders.value = res.data;
  } catch (error) {
    console.error('讀取訂單失敗', error);
    if (error.response?.status === 401) {
      alert('登入已過期或無效，請重新登入');
      localStorage.removeItem('adminToken');
      router.push('/admin/login');
    }
  } finally {
    isLoading.value = false;
  }
};

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