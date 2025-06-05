<template>
  <div class="card p-4">
    <h5 class="card-title mb-3">🛍️ 商品管理</h5>
    
    <!-- 新增商品表單 -->
    <div class="row g-2 mb-3">
      <div class="col-md-3">
        <input v-model="newProduct.name" class="form-control" placeholder="商品名稱">
      </div>
      <div class="col-md-2">
        <input v-model="newProduct.price" type="number" class="form-control" placeholder="價格">
      </div>
      <div class="col-md-4">
        <input v-model="newProduct.description" class="form-control" placeholder="商品描述">
      </div>
      <div class="col-md-3">
        <input v-model="newProduct.image_url" class="form-control" placeholder="圖片網址 (可空)">
      </div>
      
      <div class="category-checkboxes mb-3">
        <label><input type="checkbox" v-model="newProduct.categories" value="flashsale" class="category-checkbox"> 限時搶購</label>
        <label><input type="checkbox" v-model="newProduct.categories" value="sale" class="category-checkbox"> 限定SALE</label>
        <label><input type="checkbox" v-model="newProduct.categories" value="japan_medicine" class="category-checkbox"> 日本藥品</label>
        <label><input type="checkbox" v-model="newProduct.categories" value="food_drink" class="category-checkbox"> 食品/飲料/酒</label>
        <label><input type="checkbox" v-model="newProduct.categories" value="beauty" class="category-checkbox"> 美妝/美髮/肌膚護理</label>
        <label><input type="checkbox" v-model="newProduct.categories" value="men" class="category-checkbox"> 男士用品</label>
        <label><input type="checkbox" v-model="newProduct.categories" value="home" class="category-checkbox"> 生活家用/沐浴&身體</label>
        <label><input type="checkbox" v-model="newProduct.categories" value="baby" class="category-checkbox"> 親子育兒</label>
      </div>
    </div>
    
    <button class="btn btn-success w-100 mb-3" @click="handleAddProduct">新增商品</button>
    
    <!-- 商品列表 -->
    <div class="table-responsive">
      <table class="table table-striped table-bordered">
        <thead class="table-dark">
          <tr>
            <th>名稱</th>
            <th>價格</th>
            <th>描述</th>
            <th>圖片</th>
            <th>分類</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>
              <input v-model="product.name" class="form-control form-control-sm">
            </td>
            <td>
              <input v-model="product.price" type="number" class="form-control form-control-sm">
            </td>
            <td>
              <input v-model="product.description" class="form-control form-control-sm">
            </td>
            <td>
              <input v-model="product.image_url" class="form-control form-control-sm">
            </td>
            <td>
              <div class="category-checkboxes">
                <label><input type="checkbox" v-model="product.categories" value="flashsale"> 限時搶購</label>
                <label><input type="checkbox" v-model="product.categories" value="sale"> 限定SALE</label>
                <label><input type="checkbox" v-model="product.categories" value="japan_medicine"> 日本藥品</label>
                <label><input type="checkbox" v-model="product.categories" value="food_drink"> 食品/飲料/酒</label>
                <label><input type="checkbox" v-model="product.categories" value="beauty"> 美妝/美髮/肌膚護理</label>
                <label><input type="checkbox" v-model="product.categories" value="men"> 男士用品</label>
                <label><input type="checkbox" v-model="product.categories" value="home"> 生活家用/沐浴&身體</label>
                <label><input type="checkbox" v-model="product.categories" value="baby"> 親子育兒</label>
              </div>
            </td>
            <td>
              <button class="btn btn-danger btn-sm" @click="handleDeleteProduct(product.id)">
                刪除
              </button>
              <button class="btn btn-primary btn-sm" @click="handleSaveProduct(product)">
                保存
              </button>
            </td>
          </tr>
          <tr v-if="products.length === 0">
            <td colspan="6" class="text-center">沒有找到商品資料。</td>
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

const products = ref([]);
const userStore = useUserStore();

const newProduct = ref({
  name: '',
  price: '',
  description: '',
  image_url: '',
  categories: []
});

onMounted(() => {
  loadProducts();
});

async function loadProducts() {
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    alert('請先登入！');
    return;
  }

  try {
    const res = await api.get('/api/admin/products');

    if (!res.ok) {
      const errorText = await res.text();
      console.error('無法載入商品資料：', res.status, errorText);
      alert('無法載入商品資料！');
      return;
    }

    const data = await res.json();
    console.log('從後端接收到的原始商品數據:', data);
    products.value = data.map(p => ({
      ...p,
      categories: (p.category || "").split("#")
    }));
    console.log('經過處理後的商品數據 (products.value):', products.value);
  } catch (error) {
    console.error('載入商品資料時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function handleAddProduct() {
  const { name, price, description, image_url, categories } = newProduct.value;

  if (!name || !price) {
    alert("請填寫完整商品名稱與價格！");
    return;
  }

  const category = categories.join("#");
  if (category.length > 255) {
    alert("❌ 分類超過 255 字元限制，請刪減分類！");
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  try {
    const res = await api.post('/api/admin/products', { name, price, description, image_url, category });

    const result = await res.json();

    if (!res.ok) {
       console.error('新增商品失敗：', result);
       alert(result.error || '新增商品失敗！');
    } else {
       alert(result.message || '商品新增成功！');
       // 清空表單
       newProduct.value = {
         name: '',
         price: '',
         description: '',
         image_url: '',
         categories: []
       };
       loadProducts(); // 更新成功後重新載入商品資料
    }

  } catch (error) {
    console.error('新增商品時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function handleSaveProduct(product) {
  const { name, price, description, image_url, categories } = product;
  const category = categories.join("#");

  if (!name || !price) {
    alert("請填寫完整商品名稱與價格！");
    return;
  }

  if (category.length > 255) {
    alert("❌ 分類超過 255 字元限制，請刪減分類！");
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  try {
    const res = await api.put(`/api/admin/products/${product.id}`, { name, price, description, image_url, category });

    const result = await res.json();

    if (!res.ok) {
       console.error('更新商品失敗：', result);
       alert(result.error || '更新商品失敗！');
    } else {
       alert(result.message || '商品更新成功！');
       loadProducts(); // 更新成功後重新載入商品資料
    }

  } catch (error) {
    console.error('更新商品時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}

async function handleDeleteProduct(id) {
  if (!confirm("確定刪除這個商品？")) return;

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     alert('請先登入！');
     return;
  }

  try {
    const res = await api.delete(`/api/admin/products/${id}`);

    const result = await res.json();

    if (!res.ok) {
       console.error('刪除商品失敗：', result);
       alert(result.error || '刪除商品失敗！');
    } else {
       alert(result.message || '商品刪除成功！');
       loadProducts(); // 更新成功後重新載入商品資料
    }

  } catch (error) {
    console.error('刪除商品時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    }
  }
}
</script>

<style scoped>
.category-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.category-checkboxes label {
  margin-right: 15px;
  white-space: nowrap;
}
</style> 