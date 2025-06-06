<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">👤 使用者管理</h5>
    <!-- 訊息提示 -->
    <div v-if="displayMessage" class="alert text-center mb-3" :class="{ 'alert-success': displayMessage.includes('✅'), 'alert-danger': displayMessage.includes('❌') }">
      {{ displayMessage }}
    </div>
    <div class="row g-2 mb-3 align-items-end">
      <div class="col-md-4"><input v-model="newAdmin.username" class="form-control" placeholder="使用者名稱"></div>
      <div class="col-md-4"><input v-model="newAdmin.password" type="password" class="form-control" placeholder="密碼"></div>
      <div class="col-md-4 d-flex align-items-end">
        <button class="btn btn-success w-100 add-admin-btn" @click="addAdmin">新增使用者</button>
      </div>
    </div>
    <div class="table-responsive">
      <table class="table table-striped table-bordered">
        <thead class="table-dark">
          <tr>
            <th>使用者名稱</th>
            <th>操作</th>
            <th>備註</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="admin in admins" :key="admin.id" :class="{ 'admin-row': admin.username === 'admin' }">
            <td>
              <input v-model="admin.username" class="form-control form-control-sm" :disabled="admin.username === 'admin'">
            </td>
            <td>
              <button class="btn btn-primary btn-sm me-1" @click="saveAdmin(admin)" :disabled="admin.username === 'admin'">保存</button>
              <button class="btn btn-warning btn-sm me-1" @click="resetPassword(admin)" :disabled="admin.username === 'admin'">重置密碼</button>
              <button class="btn btn-danger btn-sm" @click="deleteAdmin(admin.id)" :disabled="admin.username === 'admin'">刪除</button>
            </td>
            <td>
              <input v-model="admin.notes" class="form-control form-control-sm" :disabled="admin.username === 'admin'">
            </td>
          </tr>
          <tr v-if="admins.length === 0">
            <td colspan="3" class="text-center text-muted">沒有找到使用者資料。</td>
          </tr>
        </tbody>
      </table>
    </div>
    <AdminCardList :items="admins" :fields="cardFields" key-field="id" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api';
import AdminCardList from '@/components/AdminCardList.vue';

const admins = ref([]);
const userStore = useUserStore();
const displayMessage = ref(''); // 新增響應式變數用於顯示訊息

const newAdmin = ref({
  username: '',
  password: '',
});

const cardFields = [
  { key: 'id', label: '管理員ID' },
  { key: 'username', label: '帳號' },
  { key: 'created_at', label: '建立時間' },
  { key: 'notes', label: '備註' },
];

onMounted(() => {
  loadAdmins();
  displayMessage.value = ''; // 在組件載入時清除訊息
});

async function loadAdmins() {
  console.log('loadAdmins triggered.');
  console.log('userStore.admin_token:', userStore.admin_token);
  console.log('userStore.isAuthenticated:', userStore.isAuthenticated);

  displayMessage.value = ''; // 清除之前的訊息
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.get('/api/admin/admin_users');

    const data = res.data;
    console.log('從後端接收到的使用者數據:', data);
    admins.value = data.map(admin => ({ ...admin, notes: admin.notes || '' }));
  } catch (error) {
    console.error('無法載入使用者資料：', error);
    if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    }
  }
}

async function addAdmin() {
  displayMessage.value = ''; // 清除之前的訊息
  const { username, password } = newAdmin.value;

  if (!username || !password) {
    displayMessage.value = "❌ 請填寫完整使用者名稱與密碼！";
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.post('/api/admin/create_admin', { username, password });

    const result = res.data;

    if (res.status === 200) {
      displayMessage.value = result.message || '✅ 使用者新增成功！';
      newAdmin.value = {
        username: '',
        password: '',
      };
      loadAdmins();
    } else {
      console.error('新增使用者失敗：', result);
      displayMessage.value = result.error || '❌ 新增使用者失敗！';
    }
  } catch (error) {
    console.error('新增使用者時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      displayMessage.value = error.response.data.error;
    } else if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else {
      displayMessage.value = '❌ 新增使用者時發生未知錯誤！';
    }
  }
}

async function saveAdmin(admin) {
  displayMessage.value = ''; // 清除之前的訊息
  if (admin.username === 'admin') {
    displayMessage.value = '❌ 無法修改 admin 帳號！';
    return;
  }

  const { id, notes } = admin;

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.post('/api/admin/update_admin', { id, notes });

    const result = res.data;

    if (res.status === 200) {
      displayMessage.value = result.message || '✅ 備註更新成功！';
    } else {
      console.error('更新備註失敗：', result);
      displayMessage.value = result.error || '❌ 更新備註失敗！';
    }
  } catch (error) {
    console.error('更新備註時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      displayMessage.value = error.response.data.error;
    } else if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else {
      displayMessage.value = '❌ 更新備註時發生未知錯誤！';
    }
  }
}

async function resetPassword(admin) {
  displayMessage.value = ''; // 清除之前的訊息
  if (admin.username === 'admin') {
    displayMessage.value = '❌ 無法重置 admin 帳號的密碼！';
    return;
  }

  if (!confirm(`確定要重置使用者 ${admin.username} 的密碼嗎？`)) {
    displayMessage.value = '取消重置密碼！';
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.post('/api/admin/reset_admin_password', { username: admin.username });

    const result = res.data;

    if (res.status === 200 && result.new_password) {
      displayMessage.value = `✅ 使用者 ${admin.username} 的新密碼為：${result.new_password}`;
    } else {
      console.error('重置密碼失敗：', result);
      displayMessage.value = result.error || '❌ 重置密碼失敗！';
    }
  } catch (error) {
    console.error('重置密碼時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      displayMessage.value = error.response.data.error;
    } else if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else {
      displayMessage.value = '❌ 重置密碼時發生未知錯誤！';
    }
  }
}

async function deleteAdmin(id) {
  displayMessage.value = ''; // 清除之前的訊息
  const adminToDelete = admins.value.find(a => a.id === id);
  if (adminToDelete && adminToDelete.username === 'admin') {
    displayMessage.value = '❌ 無法刪除 admin 帳號！';
    return;
  }

  if (!confirm("確定刪除這個使用者？")) {
    displayMessage.value = '取消刪除使用者！';
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.delete(`/api/admin/admin_users/${id}`);

    const result = res.data;

    if (res.status === 200) {
      displayMessage.value = result.message || '✅ 使用者刪除成功！';
      loadAdmins();
    } else {
      console.error('刪除使用者失敗：', result);
      displayMessage.value = result.error || '❌ 刪除使用者失敗！';
    }
  } catch (error) {
    console.error('刪除使用者時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      displayMessage.value = error.response.data.error;
    } else if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else if (error.response && error.response.status === 405) {
      displayMessage.value = '❌ 後端不支援刪除管理員的功能。';
    } else {
      displayMessage.value = '❌ 刪除使用者時發生未知錯誤！';
    }
  }
}
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
  --disabled-grey: #cccccc; /* 用於禁用元素的灰色 */
  --disabled-text: #6c757d; /* 用於禁用文字的顏色 */
}

/* 提升卡片的質感 */
.card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: var(--white); /* 使用白色背景 */
  margin-top: 1.5rem; /* 添加一些頂部間距 */
}

/* 表格樣式優化 - 與其他頁面保持一致 */
.table {
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid var(--light-grey); /* 淺灰色邊框 */
  border-radius: 8px;
  overflow: hidden; /* 確保圓角生效 */
  margin-bottom: 1rem; /* 添加底部間距 */
  background-color: var(--white); /* 表格背景色 */
}

.table th,
.table td {
  padding: 12px 15px; /* 調整單元格內邊距 */
  border-top: 1px solid var(--light-grey); /* 單元格頂部邊框 */
}

.table thead th {
  background-color: var(--dark-brown); /* 表頭背景色 */
  color: var(--white); /* 表頭文字顏色 */
  font-weight: bold;
  border-bottom: 2px solid var(--light-brown); /* 表頭底部邊框 */
}

/* 偶數行條紋 */
.table-striped tbody tr:nth-of-type(even) {
  background-color: var(--light-grey); /* 淺灰色條紋 */
}

/* 懸停效果 */
.table tbody tr:hover {
  background-color: var(--medium-grey); /* 懸停時變色 */
}

/* 輸入框樣式微調 */
.form-control {
  border-radius: 5px;
  border-color: var(--light-brown); /* 輸入框邊框顏色 */
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  color: var(--dark-brown); /* 輸入框文字顏色 */
}

.form-control::placeholder {
  color: var(--light-brown); /* Placeholder 文字顏色 */
  opacity: 0.8; /* 調整透明度 */
}

.form-control:focus {
  border-color: var(--accent-brown); /* 聚焦時邊框顏色 */
  box-shadow: 0 0 0 0.25rem rgba(161, 138, 123, 0.25); /* 根據 light-brown 調整陰影顏色 */
}

.form-control:disabled {
    background-color: var(--medium-grey); /* 禁用時背景色 */
    color: var(--disabled-text); /* 禁用時文字顏色 */
    opacity: 0.65; /* 禁用時透明度 */
}

/* 按鈕樣式微調 - 與其他頁面保持一致 */
.btn {
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

/* 主要按鈕 (保存) */
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

.btn-primary:disabled {
    background-color: var(--disabled-grey); /* 禁用時背景色 */
    border-color: var(--disabled-grey); /* 禁用時邊框顏色 */
    color: var(--white); /* 禁用時文字顏色 */
    opacity: 0.65;
}

/* 成功按鈕 (新增使用者) */
.btn-success {
   background-color: var(--dark-brown); /* 新增按鈕背景色 */
   border-color: var(--dark-brown); /* 新增按鈕邊框顏色 */
   color: var(--white); /* 新增按鈕文字顏色 */
}

.btn-success:hover {
    background-color: #2a2523; /* 新增按鈕懸停顏色 (深一點的棕色) */
    border-color: #2a2523;
    color: var(--white);
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

.btn-warning:disabled {
    background-color: var(--disabled-grey); /* 禁用時背景色 */
    border-color: var(--disabled-grey); /* 禁用時邊框顏色 */
    color: var(--white); /* 禁用時文字顏色 */
    opacity: 0.65;
}

/* 危險按鈕 (刪除) */
.btn-danger {
   background-color: #dc3545; /* 保留紅色，作為危險操作的標準顏色 */
   border-color: #dc3545;
   color: var(--white);
}

.btn-danger:hover {
    background-color: #c82333;
    border-color: #bd2130;
    color: var(--white);
}

.btn-danger:disabled {
    background-color: var(--disabled-grey); /* 禁用時背景色 */
    border-color: var(--disabled-grey); /* 禁用時邊框顏色 */
    color: var(--white); /* 禁用時文字顏色 */
    opacity: 0.65;
}

/* 標題樣式微調 */
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
  color: #6c757d !important; /* 保持灰色，與棕色調協調 */
}

/* Admin 行的特殊樣式 */
tr.admin-row {
  background-color: var(--light-grey); /* 使用淺灰色背景 */
  color: var(--disabled-text); /* 使用禁用文字顏色 */
  font-style: italic; /* 可以添加斜體 */
}

 tr.admin-row td {
     color: var(--disabled-text); /* 確保單元格文字也是禁用顏色 */
 }

.add-admin-btn {
  height: 38px;
  font-size: 0.97rem;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  box-sizing: border-box;
}
</style> 