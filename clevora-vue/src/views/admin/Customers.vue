<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">👥 客戶管理</h5>
    <div class="table-responsive">
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
            <td>{{ customer.created_at }}</td>
            <td>
              <button class="btn btn-primary btn-sm" @click="editCustomer(customer.customer_id)">修改</button>
              <button class="btn btn-warning btn-sm" @click="resetPassword(customer.customer_id)">重置密碼</button>
            </td>
          </tr>
          <tr v-if="customers.length === 0">
            <td colspan="7" class="text-center">沒有找到客戶資料。</td>
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

const customers = ref([]);
const userStore = useUserStore();

async function loadCustomers() {
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.get('/admin/customers');

    const data = res.data;
    customers.value = data;
  } catch (error) {
    console.error('載入客戶資料時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function editCustomer(customerId) {
  const customer = customers.value.find(c => c.customer_id === customerId);
  if (!customer) return;

  const name = prompt("請輸入姓名：", customer.name);
  if (!name) { alert("❌ 請輸入姓名！"); return; }

  const phone = prompt("請輸入電話：", customer.phone);
  if (!phone) { alert("❌ 請輸入電話！"); return; }

  const address = prompt("請輸入地址：", customer.address || '');

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  try {
    const res = await api.put('/admin/customers', { customer_id: customerId, name, phone, address });

    const result = res.data;

    if (res.status !== 200) {
       console.error('更新客戶資料失敗：', result);
       alert(result.error || '更新客戶資料失敗！');
    } else {
       alert(result.message || '客戶資料更新成功！');
       loadCustomers();
    }

  } catch (error) {
    console.error('更新客戶資料時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function resetPassword(customerId) {
  const new_password = prompt("請輸入新密碼：");
  if (!new_password) { alert("❌ 請輸入新密碼！"); return; }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  try {
    const res = await api.post('/admin/reset_customer_password', { customer_id: customerId, new_password });

    const result = res.data;

    if (res.status !== 200) {
       console.error('重置密碼失敗：', result);
       alert(result.error || '重置密碼失敗！');
    } else {
       alert(result.message || '密碼重置成功！');
    }

  } catch (error) {
    console.error('重置密碼時發生錯誤：', error);
  }
}

onMounted(() => {
  loadCustomers();
});
</script>

<style scoped>
/* 可以添加一些 Customers.vue 特有的樣式 */
</style> 