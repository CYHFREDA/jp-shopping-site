<template>
  <div class="product-create-page-center">
    <div class="card p-4">
      <h5 class="card-title mb-3">➕ 新增商品</h5>
      <!-- 訊息提示 -->
      <div v-if="displayMessage" class="alert text-center mb-3" :class="{ 'alert-success': displayMessage.includes('✅'), 'alert-danger': displayMessage.includes('❌') }">
        {{ displayMessage }}
      </div>
      <div class="row g-2 mb-3 align-items-end">
        <div class="col-md-3">
          <input v-model="newProduct.name" class="form-control search-input" placeholder="商品名稱">
        </div>
        <div class="col-md-2">
          <input v-model="newProduct.price" type="number" class="form-control search-input" placeholder="價格">
        </div>
        <div class="col-md-4">
          <input v-model="newProduct.description" class="form-control search-input" placeholder="商品描述">
        </div>
        <div class="col-md-3 d-flex align-items-center">
          <input v-model="newProduct.image_url" class="form-control search-input me-2" placeholder="圖片網址 (可空)">
          <button class="add-product-btn btn btn-success btn-sm" @click="handleAddProduct">新增商品</button>
        </div>
        <div class="category-checkboxes mb-3 col-12">
          <label v-for="(label, key) in categoryMap" :key="key" class="category-tag">
            <input type="checkbox" v-model="newProduct.categories" :value="key" />
            <span>{{ label }}</span></label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api';
import { useRouter } from 'vue-router';

const router = useRouter();
const userStore = useUserStore();
const displayMessage = ref('');

const newProduct = ref({
  name: '',
  price: '',
  description: '',
  image_url: '',
  categories: []
});

const categoryMap = {
  flashsale: '限時搶購',
  sale: '限定SALE',
  japan_medicine: '日本藥品',
  food_drink: '食品/飲料/酒',
  beauty: '美妝/美髮/肌膚護理',
  men: '男士用品',
  home: '生活家用/沐浴&身體',
  baby: '親子育兒'
};

async function handleAddProduct() {
  displayMessage.value = '';
  const { name, price, description, image_url, categories } = newProduct.value;

  if (!name || !price) {
    displayMessage.value = "❌ 請填寫完整商品名稱與價格！";
    return;
  }

  const category = categories.join("#");
  if (category.length > 255) {
    displayMessage.value = "❌ 分類超過 255 字元限制，請刪減分類！";
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
    displayMessage.value = '❌ 請先登入！';
    return;
  }

  try {
    const res = await api.post('/api/admin/products', { name, price, description, image_url, category });
    const result = res.data;
    displayMessage.value = result.message || '✅ 商品新增成功！';
    newProduct.value = { name: '', price: '', description: '', image_url: '', categories: [] };
    // 新增成功後自動跳回商品列表
    setTimeout(() => router.push('/admin/products'), 1000);
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.message || '新增商品失敗！';
    displayMessage.value = `❌ ${errorMessage}`;
  }
}
</script>

<style scoped>
.product-create-page-center {
  max-width: 900px;
  margin: 0 auto;
  padding-top: 24px;
}
</style> 