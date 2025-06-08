<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">👥 客戶管理</h5>
    <div v-if="displayErrorMessage" class="alert alert-danger text-center mb-3" role="alert">
      {{ displayErrorMessage }}
    </div>
    <div v-if="isLoading" class="text-center text-muted">載入中...</div>
    <div v-else>
      <!-- 桌機版表格 -->
      <div class="table-responsive d-none d-md-block">
        <table class="table table-striped table-bordered">
          <thead class="table-dark">
            <tr>
              <th>客戶編號</th>
              <th>姓名</th>
              <th>Email</th>
              <th>電話</th>
              <th>地址</th>
              <th>建立時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in customers" :key="customer.customer_id">
              <td>{{ customer.customer_id }}</td>
              <td>{{ customer.name }}</td>
              <td>{{ customer.email }}</td>
              <td>{{ customer.phone }}</td>
              <td>{{ customer.address || '' }}</td>
              <td>{{ formatDateTime(customer.created_at) }}</td>
              <td>
                <button class="btn btn-primary btn-sm me-1" @click="editCustomer(customer.customer_id)">修改</button>
                <button class="btn btn-warning btn-sm" @click="resetPassword(customer.customer_id)">重置密碼</button>
              </td>
            </tr>
            <tr v-if="customers.length === 0">
              <td colspan="7" class="text-center text-muted">沒有找到客戶資料。</td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 手機版卡片 -->
      <div class="d-block d-md-none">
        <AdminCardList :items="customers" :fields="cardFields" key-field="customer_id" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api';
import AdminCardList from '@/components/AdminCardList.vue';

const customers = ref([]);
const userStore = useUserStore();
const displayErrorMessage = ref('');
const isLoading = ref(true);

const cardFields = [
  { key: 'customer_id', label: '客戶ID' },
  { key: 'name', label: '姓名' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: '電話' },
  { key: 'address', label: '地址' },
  { key: 'created_at', label: '註冊時間' },
];

async function loadCustomers() {
  displayErrorMessage.value = '';
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayErrorMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.get('/api/admin/customers');

    const data = res.data;
    console.log('從後端接收到的客戶數據:', data);
    customers.value = data;
  } catch (error) {
    console.error('載入客戶資料時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      displayErrorMessage.value = '❌ 認證失敗，請重新登入！';
    }
  } finally {
    isLoading.value = false;
  }
}

async function editCustomer(customerId) {
  const customer = customers.value.find(c => c.customer_id === customerId);
  if (!customer) return;

  const name = prompt("請輸入姓名：", customer.name);
  if (!name) { displayErrorMessage.value = "❌ 請輸入姓名！"; return; }

  const phone = prompt("請輸入電話：", customer.phone);
  if (!phone) { displayErrorMessage.value = "❌ 請輸入電話！"; return; }

  const address = prompt("請輸入地址：", customer.address || '');

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     displayErrorMessage.value = '❌ 請先登入！';
     return;
  }

  try {
    const res = await api.put('/admin/customers', { customer_id: customerId, name, phone, address });

    const result = res.data;

    if (res.status !== 200) {
       console.error('更新客戶資料失敗：', result);
       displayErrorMessage.value = result.error || '❌ 更新客戶資料失敗！';
    } else {
       displayErrorMessage.value = result.message || '✅ 客戶資料更新成功！';
       loadCustomers();
    }

  } catch (error) {
    console.error('更新客戶資料時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      displayErrorMessage.value = '❌ 認證失敗，請重新登入！';
    }
  }
}

async function resetPassword(customerId) {
  displayErrorMessage.value = '';
  const new_password = prompt("請輸入新密碼：");
  if (!new_password) { displayErrorMessage.value = "❌ 請輸入新密碼！"; return; }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     displayErrorMessage.value = '❌ 請先登入！';
     return;
  }

  try {
    const res = await api.post('/admin/reset_customer_password', { customer_id: customerId, new_password });

    const result = res.data;

    if (res.status !== 200) {
       console.error('重置密碼失敗：', result);
       displayErrorMessage.value = result.error || '❌ 重置密碼失敗！';
    } else {
       displayErrorMessage.value = result.message || '✅ 密碼重置成功！';
    }

  } catch (error) {
    console.error('重置密碼時發生錯誤：', error);
    displayErrorMessage.value = '❌ 重置密碼時發生未知錯誤！';
  }
}

function formatDateTime(dt) {
  if (!dt) return '';
  const date = new Date(dt);
  const twDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  return twDate.toLocaleString('zh-TW', { hour12: false });
}

onMounted(() => {
  loadCustomers();
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
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(56,48,46,0.08);
  background: #fff;
  margin-bottom: 1.5rem;
}

.table th, .table td {
  padding: 16px 18px;
  vertical-align: middle;
  border-top: 1px solid #f0eae6;
}

.table thead th {
  background: #38302e;
  color: #fff;
  font-weight: bold;
  font-size: 1.08rem;
  border-bottom: 2px solid #a18a7b;
}

.table-striped tbody tr:nth-of-type(even) {
  background-color: #f8f9fa;
}

.table tbody tr:hover {
  background-color: #f3edea;
  transition: background 0.2s;
}

.table td {
  font-size: 1.05rem;
  color: #38302e;
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

/* 警告按鈕 (重置密碼) */
.btn-warning {
   background-color: #ffc107; /* 保留黃色，作為警告操作的標準顏色 */
   border-color: #ffc107;
   color: var(--dark-brown); /* 黃色按鈕使用深色文字 */
}

.btn-warning:hover {
    background-color: #e0a800;
    border-color: #d39e00;
    color: var(--dark-brown);
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
  color: #a18a7b !important;
}
</style>

<AdminCardList :items="customers" :fields="cardFields" key-field="customer_id" /> 