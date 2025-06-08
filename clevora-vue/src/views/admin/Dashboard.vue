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
        <div class="d-flex flex-wrap align-items-center mb-3 justify-content-between">
          <h5 class="card-title mb-0">訂單數趨勢</h5>
          <div class="d-flex flex-wrap align-items-center gap-2">
            <label class="me-1">起始日</label>
            <input type="date" v-model="startDate" class="form-control form-control-sm" style="width: 140px;">
            <label class="mx-1">結束日</label>
            <input type="date" v-model="endDate" class="form-control form-control-sm" style="width: 140px;">
            <button class="btn btn-sm btn-primary ms-2" @click="fetchDashboard">查詢</button>
          </div>
        </div>
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
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#fff',
    borderColor: '#a18a7b',
    borderWidth: 1,
    textStyle: { color: '#38302e' }
  },
  xAxis: {
    type: 'category',
    data: [],
    axisLabel: { color: '#a18a7b', fontWeight: 'bold' },
    axisLine: { lineStyle: { color: '#a18a7b' } }
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    axisLabel: { color: '#a18a7b', fontWeight: 'bold' },
    splitLine: { lineStyle: { color: '#e9ecef' } }
  },
  grid: { left: 40, right: 20, top: 40, bottom: 40 },
  series: [
    {
      name: '訂單數',
      type: 'line',
      data: [],
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        color: '#a18a7b',
        width: 3
      },
      itemStyle: {
        color: '#a18a7b',
        borderColor: '#fff',
        borderWidth: 2
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#a18a7b44' },
            { offset: 1, color: '#fff' }
          ]
        }
      },
      label: {
        show: true,
        position: 'top',
        color: '#a18a7b',
        fontWeight: 'bold'
      }
    }
  ]
});

// 新增：日期篩選
const today = new Date();
const formatDate = d => d.toISOString().slice(0, 10);
const endDate = ref(formatDate(today));
const startDate = ref(formatDate(new Date(today.getTime() - 29 * 24 * 60 * 60 * 1000)));

async function fetchDashboard() {
  try {
    const token = userStore.admin_token;
    if (!token) return;
    // 改為帶日期參數
    const res = await axios.get('/api/admin/dashboard_summary', {
      headers: {
        Authorization: `Bearer ${token}`
      },
      params: {
        start_date: startDate.value,
        end_date: endDate.value
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

watch([startDate, endDate], ([newStart, newEnd], [oldStart, oldEnd]) => {
  if (newStart && newEnd && (newStart !== oldStart || newEnd !== oldEnd)) {
    fetchDashboard();
  }
});

function getOrderItemCount(itemNames) {
  if (!itemNames) return 0;
  return itemNames.split('#').reduce((sum, item) => {
    const match = item.match(/x\\s*(\\d+)/);
    return sum + (match ? parseInt(match[1]) : 1);
  }, 0);
}
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