<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">⚙️ 系統設定</h5>
    
    <div v-if="settings">
      <div class="mb-3">
        <label for="siteTitle" class="form-label">網站標題：</label>
        <input type="text" id="siteTitle" v-model="settings.site_title" class="form-control">
      </div>
      <div class="mb-3">
        <label for="contactEmail" class="form-label">聯絡 Email：</label>
        <input type="email" id="contactEmail" v-model="settings.contact_email" class="form-control">
      </div>
      <div class="mb-3">
        <label for="itemsPerPage" class="form-label">每頁商品數量：</label>
        <input type="number" id="itemsPerPage" v-model.number="settings.items_per_page" class="form-control">
      </div>
      
      <!-- 更多設定項目可以根據需要添加 -->

      <button class="btn btn-primary mt-3" @click="saveSettings">保存設定</button>
    </div>
    <div v-else>
      載入設定中...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api'; // 引入 api 實例

const settings = ref(null);
const userStore = useUserStore();

onMounted(() => {
  loadSettings();
});

async function loadSettings() {
  const token = userStore.admin_token; // 使用 userStore 中的 admin_token
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    // 使用 api 實例發送請求
    const res = await api.get('/admin/settings');

    const data = res.data; // axios 的響應數據在 res.data 中
    settings.value = data;
  } catch (error) {
    console.error('載入設定資料時發生錯誤：', error);
    // 檢查是否是 401 錯誤，如果是，可能需要導向登入頁面
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
      // 這裡可以觸發 userStore 的 logout 或直接導向登入頁面
    }
  }
}

async function saveSettings() {
  const token = userStore.admin_token; // 使用 userStore 中的 admin_token
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  if (!settings.value) return;

  try {
    // 使用 api 實例發送請求
    const res = await api.post('/admin/settings', settings.value); // 或者 PUT，根據後端 API 設計

    const result = res.data; // axios 的響應數據在 res.data 中

    if (res.status !== 200) { // 檢查響應狀態碼
       console.error('保存設定失敗：', result);
       alert(result.error || '保存設定失敗！');
    } else {
       alert(result.message || '設定保存成功！');
       // 保存成功後可以選擇重新載入設定或更新本地狀態
       loadSettings(); 
    }

  } catch (error) {
    console.error('保存設定時發生錯誤：', error);
    // 檢查是否是 401 錯誤，如果是，可能需要導向登入頁面
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
      // 這裡可以觸發 userStore 的 logout 或直接導向登入頁面
    }
  }
}
</script>

<style scoped>
/* 可以添加一些 Settings.vue 特有的樣式 */
</style> 