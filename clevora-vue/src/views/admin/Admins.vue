<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">👤 使用者管理</h5>
    <div class="row g-2 mb-3">
      <div class="col-md-4"><input v-model="newAdmin.username" class="form-control" placeholder="使用者名稱"></div>
      <div class="col-md-4"><input v-model="newAdmin.password" type="password" class="form-control" placeholder="密碼"></div>
      <div class="col-md-4"><input v-model="newAdmin.name" class="form-control" placeholder="姓名"></div>
    </div>
    <button class="btn btn-success w-100 mb-3" @click="addAdmin">新增使用者</button>
    <div class="table-responsive">
      <table class="table table-striped table-bordered">
        <thead class="table-dark">
          <tr>
            <th>使用者名稱</th>
            <th>姓名</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="admin in admins" :key="admin.id">
            <td><input v-model="admin.username" class="form-control form-control-sm"></td>
            <td><input v-model="admin.name" class="form-control form-control-sm"></td>
            <td>
              <button class="btn btn-danger btn-sm" @click="deleteAdmin(admin.id)">刪除</button>
              <button class="btn btn-primary btn-sm" @click="saveAdmin(admin.id)">保存</button>
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
  name: ''
});

onMounted(() => {
  loadAdmins();
});

async function loadAdmins() {
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.get('/api/admin/admins');

    const data = res.data;
    admins.value = data;
  } catch (error) {
    console.error('無法載入使用者資料：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function addAdmin() {
  const { username, password, name } = newAdmin.value;

  if (!username || !password || !name) {
    alert("請填寫完整使用者名稱、密碼與姓名！");
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.post('/api/admin/admins', { username, password, name });

    const result = res.data;

    if (res.status !== 200) {
      console.error('新增使用者失敗：', result);
      alert(result.error || '新增使用者失敗！');
    } else {
      alert(result.message || '使用者新增成功！');
      newAdmin.value = {
        username: '',
        password: '',
        name: ''
      };
      loadAdmins();
    }
  } catch (error) {
    console.error('新增使用者時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function saveAdmin(id) {
  const admin = admins.value.find(a => a.id === id);
  if (!admin) return;

  const { username, name } = admin;

  if (!username || !name) {
    alert("請填寫完整使用者名稱與姓名！");
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.put(`/api/admin/admins/${id}`, { username, name });

    const result = res.data;

    if (res.status !== 200) {
      console.error('更新使用者失敗：', result);
      alert(result.error || '更新使用者失敗！');
    } else {
      alert(result.message || '使用者更新成功！');
      loadAdmins();
    }
  } catch (error) {
    console.error('更新使用者時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function deleteAdmin(id) {
  if (!confirm("確定刪除這個使用者？")) return;

  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.delete(`/api/admin/admins/${id}`);

    const result = res.data;

    if (res.status !== 200) {
      console.error('刪除使用者失敗：', result);
      alert(result.error || '刪除使用者失敗！');
    } else {
      alert(result.message || '使用者刪除成功！');
      loadAdmins();
    }
  } catch (error) {
    console.error('刪除使用者時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}
</script>

<style scoped>
/* 可以添加一些 Admins.vue 特有的樣式 */
</style> 