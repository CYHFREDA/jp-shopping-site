<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">👤 使用者管理</h5>
    <div class="row g-2 mb-3">
      <div class="col-md-6"><input v-model="newAdmin.username" class="form-control" placeholder="使用者名稱"></div>
      <div class="col-md-6"><input v-model="newAdmin.password" type="password" class="form-control" placeholder="密碼"></div>
    </div>
    <button class="btn btn-success w-100 mb-3" @click="addAdmin">新增使用者</button>
    <div class="table-responsive">
      <table class="table table-striped table-bordered">
        <thead class="table-dark">
          <tr>
            <th>使用者名稱</th>
            <th>備註</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="admin in admins" :key="admin.id" :class="{ 'admin-row': admin.username === 'admin' }">
            <td>
              <input v-model="admin.username" class="form-control form-control-sm" :disabled="admin.username === 'admin'">
            </td>
            <td>
              <input v-model="admin.notes" class="form-control form-control-sm" :disabled="admin.username === 'admin'">
            </td>
            <td>
              <button class="btn btn-primary btn-sm me-1" @click="saveAdmin(admin)" :disabled="admin.username === 'admin'">保存</button>
              <button class="btn btn-warning btn-sm me-1" @click="resetPassword(admin)" :disabled="admin.username === 'admin'">重置密碼</button>
              <button class="btn btn-danger btn-sm" @click="deleteAdmin(admin.id)" :disabled="admin.username === 'admin'">刪除</button>
            </td>
          </tr>
          <tr v-if="admins.length === 0">
            <td colspan="3" class="text-center">沒有找到使用者資料。</td>
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

const admins = ref([]);
const userStore = useUserStore();

const newAdmin = ref({
  username: '',
  password: '',
});

onMounted(() => {
  loadAdmins();
});

async function loadAdmins() {
  console.log('loadAdmins triggered.');
  console.log('userStore.admin_token:', userStore.admin_token);
  console.log('userStore.isAuthenticated:', userStore.isAuthenticated);

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
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
      alert('認證失敗，請重新登入！');
    }
  }
}

async function addAdmin() {
  const { username, password } = newAdmin.value;

  if (!username || !password) {
    alert("請填寫完整使用者名稱與密碼！");
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.post('/api/admin/create_admin', { username, password });

    const result = res.data;

    if (res.status === 200) {
      alert(result.message || '使用者新增成功！');
      newAdmin.value = {
        username: '',
        password: '',
      };
      loadAdmins();
    } else {
      console.error('新增使用者失敗：', result);
      alert(result.error || '新增使用者失敗！');
    }
  } catch (error) {
    console.error('新增使用者時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      alert(error.response.data.error);
    } else if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else {
      alert('新增使用者時發生未知錯誤！');
    }
  }
}

async function saveAdmin(admin) {
  if (admin.username === 'admin') return;

  const { id, notes } = admin;

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.post('/api/admin/update_admin', { id, notes });

    const result = res.data;

    if (res.status === 200) {
      alert(result.message || '備註更新成功！');
    } else {
      console.error('更新備註失敗：', result);
      alert(result.error || '更新備註失敗！');
    }
  } catch (error) {
    console.error('更新備註時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      alert(error.response.data.error);
    } else if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else {
      alert('更新備註時發生未知錯誤！');
    }
  }
}

async function resetPassword(admin) {
  if (admin.username === 'admin') return;

  if (!confirm(`確定要重置使用者 ${admin.username} 的密碼嗎？`)) return;

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.post('/api/admin/reset_admin_password', { username: admin.username });

    const result = res.data;

    if (res.status === 200 && result.new_password) {
      alert(`使用者 ${admin.username} 的新密碼為：${result.new_password}`);
    } else {
      console.error('重置密碼失敗：', result);
      alert(result.error || '重置密碼失敗！');
    }
  } catch (error) {
    console.error('重置密碼時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      alert(error.response.data.error);
    } else if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else {
      alert('重置密碼時發生未知錯誤！');
    }
  }
}

async function deleteAdmin(id) {
  const adminToDelete = admins.value.find(a => a.id === id);
  if (adminToDelete && adminToDelete.username === 'admin') {
    alert('無法刪除 admin 帳號！');
    return;
  }

  if (!confirm("確定刪除這個使用者？")) return;

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.delete(`/api/admin/admin_users/${id}`);

    const result = res.data;

    if (res.status === 200) {
      alert(result.message || '使用者刪除成功！');
      loadAdmins();
    } else {
      console.error('刪除使用者失敗：', result);
      alert(result.error || '刪除使用者失敗！');
    }
  } catch (error) {
    console.error('刪除使用者時發生錯誤：', error);
    if (error.response && error.response.data && error.response.data.error) {
      alert(error.response.data.error);
    } else if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else if (error.response && error.response.status === 405) {
      alert('後端不支援刪除管理員的功能。');
    } else {
      alert('刪除使用者時發生未知錯誤！');
    }
  }
}
</script>

<style scoped>
.admin-row {
  background-color: #f0f0f0;
  opacity: 0.8;
}
</style> 