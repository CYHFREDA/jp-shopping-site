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

const settings = ref(null);
const userStore = useUserStore();

onMounted(() => {
  loadSettings();
});

async function loadSettings() {
  const token = userStore.token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await fetch('/admin/settings', {
      headers: { "Authorization": "Basic " + token }
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error('無法載入設定資料：', res.status, errorText);
      alert('無法載入設定資料！');
      return;
    }

    settings.value = await res.json();
  } catch (error) {
    console.error('載入設定資料時發生錯誤：', error);
    alert('載入設定資料時發生錯誤！');
  }
}

async function saveSettings() {
  const token = userStore.token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  if (!settings.value) return;

  try {
    const res = await fetch('/admin/settings', {
      method: "POST", // 或者 PUT，根據後端 API 設計
      headers: { "Content-Type": "application/json", "Authorization": "Basic " + token },
      body: JSON.stringify(settings.value)
    });

    const result = await res.json();

    if (!res.ok) {
       console.error('保存設定失敗：', result);
       alert(result.error || '保存設定失敗！');
    } else {
       alert(result.message || '設定保存成功！');
       // 保存成功後可以選擇重新載入設定或更新本地狀態
       loadSettings(); 
    }

  } catch (error) {
    console.error('保存設定時發生錯誤：', error);
    alert('保存設定時發生錯誤！');
  }
}
</script>

<style scoped>
/* 可以添加一些 Settings.vue 特有的樣式 */
</style> 