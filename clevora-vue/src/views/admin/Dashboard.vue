<template>
  <div>
    <!-- 導覽列 -->
    <AdminNavbar />

    <!-- 主要內容區域 -->
    <div class="container mt-4">
      <!-- 上方橫向選單 -->
      <ul class="nav nav-tabs mb-3">
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/orders" active-class="active">📦 訂單管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/shipments" active-class="active">🚚 出貨管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/customers" active-class="active">👥 客戶管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/products" active-class="active">🛍️ 商品管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/admins" active-class="active">👤 使用者管理</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/admin/settings" active-class="active">⚙️ 系統設定</router-link>
        </li>
      </ul>

      <!-- 路由視圖 -->
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import AdminNavbar from '@/components/AdminNavbar.vue';
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { use } from 'echarts/core';
import VChart from 'vue-echarts';

const router = useRouter();
const userStore = useUserStore();

// 統計卡片資料
const cards = ref([
  { title: '今日訂單數', value: 0 },
  { title: '未付款訂單數', value: 0 },
  { title: '未出貨訂單數', value: 0 },
  { title: '總營業額', value: 0 }
]);

// 折線圖資料
const orderChartOption = ref({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value' },
  series: [
    { name: '訂單數', type: 'line', data: [] }
  ]
});

// 封裝 API 請求
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

function handleLogout() {
  if (confirm('確定要登出嗎？')) {
    userStore.logout();
    router.push('/admin/login');
  }
}
</script>

<style scoped>
.navbar {
  padding: 0.5rem 1rem;
}

.navbar-brand img {
  height: 40px;
}

.nav-tabs {
  border-bottom: 1px solid var(--light-brown); /* 調整底部邊框顏色 */
}

.nav-tabs .nav-link {
  color: var(--dark-brown); /* 非激活鏈接文字顏色 */
  border: none;
  padding: 0.75rem 1.25rem;
  margin-right: 0.5rem;
  transition: color 0.3s ease, background-color 0.3s ease;
}

.nav-tabs .nav-link.active {
  color: var(--white); /* 激活鏈接文字顏色 */
  border-bottom: 2px solid var(--light-brown); /* 激活底部邊框顏色 */
  background-color: var(--light-brown); /* 激活背景色 */
  font-weight: bold;
}

.nav-tabs .nav-link:hover {
  color: var(--light-brown); /* 懸停時文字顏色 */
  background-color: var(--light-grey); /* 懸停時淺色背景 */
  border-color: transparent;
}

/* 可以針對整個 Dashboard 容器添加一些基礎樣式 */
/* 例如：背景色、字體等 */
/* body { font-family: 'Arial', sans-serif; } */
/* .container { background-color: #fff; } */
</style> 