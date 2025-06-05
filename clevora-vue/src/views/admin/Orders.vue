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
            <td>{{ order.item_names ? order.item_names : '無商品內容' }}</td>
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
import { useUserStore } from '@/stores/userStore';

const router = useRouter();
const orders = ref([]);
const isLoading = ref(true);
const userStore = useUserStore();

const loadOrders = async () => {
  const token = userStore.admin_token;
  if (!token) {
    alert('請先登入後台');
    router.push('/admin/login');
    return;
  }

  try {
    const res = await axios.get('/api/admin/orders', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    console.log('從後端接收到的訂單數據:', res.data);

    // Log each order object for inspection
    if (Array.isArray(res.data)) {
      res.data.forEach((order, index) => {
        console.log(`訂單 ${index}:`, order);
      });
    }

    orders.value = res.data;
    isLoading.value = false;
  } catch (error) {
    console.error('載入訂單時發生錯誤:', error);
    isLoading.value = false;
  }
};

onMounted(() => {
  loadOrders();
});
</script>

<style scoped>
  /* Add your styles here */
</style>