<template>
  <div class="dashboard-container">
    <!-- 數據卡片區 -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3" v-for="card in cards" :key="card.title">
        <div class="card shadow-sm h-100">
          <div class="card-body text-center">
            <h5 class="card-title">{{ card.title }}</h5>
            <p class="card-text display-6 fw-bold">{{ card.value }}</p>
          </div>
        </div>
      </div>
    </div>
    <!-- 訂單趨勢圖表 -->
    <div class="card">
      <div class="card-body">
        <h5 class="card-title mb-3">近七日訂單數趨勢</h5>
        <v-chart :option="orderChartOption" style="height: 320px; width: 100%" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useUserStore } from '@/stores/userStore';
import axios from 'axios';
import VChart from 'vue-echarts';

const userStore = useUserStore();

const cards = ref([
  { title: '今日訂單數', value: 0 },
  { title: '未付款訂單數', value: 0 },
  { title: '未出貨訂單數', value: 0 },
  { title: '總營業額', value: 0 }
]);

const orderChartOption = ref({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value' },
  series: [
    { name: '訂單數', type: 'line', data: [] }
  ]
});

async function fetchDashboard() {
  try {
    const token = userStore.admin_token;
    if (!token) return;
    const res = await axios.get('/api/admin/dashboard_summary', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const data = res.data;
    cards.value = [
      { title: '今日訂單數', value: data.todayOrder },
      { title: '未付款訂單數', value: data.unpaidOrder },
      { title: '未出貨訂單數', value: data.unshippedOrder },
      { title: '總營業額', value: data.totalSales }
    ];
    orderChartOption.value = {
      ...orderChartOption.value,
      xAxis: { type: 'category', data: data.orderChart.dates },
      series: [
        { name: '訂單數', type: 'line', data: data.orderChart.counts }
      ]
    };
  } catch (e) {
    console.error('載入儀表板資料失敗', e);
  }
}

onMounted(() => {
  if (userStore.admin_token) {
    fetchDashboard();
  }
});

watch(() => userStore.admin_token, (newToken) => {
  if (newToken) {
    fetchDashboard();
  }
});
</script>

<style scoped>
.dashboard-container {
  max-width: 1100px;
  margin: 0 auto;
}
.card-title {
  color: #a18a7b;
}
</style> 