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

    // 直接使用 res.data 獲取數據，Axios 會自動解析 JSON
    const data = res.data;

    // Check if data is an array before mapping (optional but good practice)
    if (Array.isArray(data)) {
      products.value = data.map(p => ({
        ...p,
        // Ensure price is a number if needed for calculations/display
        price: parseFloat(p.price) || 0,
        // Split category string into an array of categories
        categories: (p.category || "").split("#")
      }));
       console.log('經過處理後的商品數據 (products.value):', products.value);
    } else {
      console.error('從後端接收到的數據不是一個陣列:', data);
      products.value = []; // Clear products if data format is unexpected
    }

  } catch (error) {
    console.error('載入商品資料時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else {
       alert('載入商品資料失敗！');
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

    // 直接從 res.data 獲取結果，Axios 已自動解析
    const result = res.data;

    // 如果請求成功（Axios 狀態碼在 2xx），執行以下邏輯
    alert(result.message || '商品新增成功！'); // 彈出成功提示
    // 清空表單
    newProduct.value = {
      name: '',
      price: '',
      description: '',
      image_url: '',
      categories: []
    };
    loadProducts(); // 重新載入商品資料

  } catch (error) {
    // 處理錯誤，包括非 2xx 狀態碼
    console.error('新增商品時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      alert('認證失敗，請重新登入！');
    } else {
      // 嘗試從錯誤響應中獲取後端返回的錯誤信息
      const errorMessage = error.response?.data?.error || error.message || '新增商品失敗！';
      alert(errorMessage);
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
/* 提升卡片的質感 */
.card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  /* 可以添加一些背景色或者留白 */
  background-color: #fff;
}

/* 表格樣式優化 */
.table {
  border-collapse: separate;
  border-spacing: 0;
  /* 調整表格邊框顏色和樣式 */
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden; /* 確保圓角生效 */
}

.table th,
.table td {
  padding: 12px 15px; /* 調整單元格內邊距 */
  border-top: 1px solid #e0e0e0; /* 單元格頂部邊框 */
}

.table thead th {
  background-color: #f8f9fa; /* 表頭背景色 */
  color: #495057; /* 表頭文字顏色 */
  font-weight: bold;
  border-bottom: 2px solid #dee2e6; /* 表頭底部邊框 */
}

/* 偶數行條紋 */
.table-striped tbody tr:nth-of-type(even) {
  background-color: #f2f2f2; /* 淺灰色條紋 */
}

/* 懸停效果 */
.table tbody tr:hover {
  background-color: #e9ecef; /* 懸停時變色 */
}

/* 輸入框樣式微調 */
.form-control {
  border-radius: 5px;
  border-color: #ced4da;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.25);
}

/* 按鈕樣式微調 */
.btn {
  border-radius: 5px;
  transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}

.btn-success {
   background-color: #28a745;
   border-color: #28a745;
}

.btn-success:hover {
    background-color: #218838;
    border-color: #1e7e34;
}

.btn-danger {
   background-color: #dc3545;
   border-color: #dc3545;
}

.btn-danger:hover {
    background-color: #c82333;
    border-color: #bd2130;
}

/* 分類 checkbox 間距調整 */
.category-checkboxes label {
  margin-right: 15px;
  margin-bottom: 5px; /* 添加底部間距 */
  display: inline-block; /* 讓 label 可以在一行顯示 */
}

.category-checkboxes input[type="checkbox"] {
  margin-right: 5px; /* 調整 checkbox 與文字間距 */
}

/* 響應式調整表格 */
@media (max-width: 768px) {
  .table-responsive .table {
    /* 在小螢幕上可以考慮不顯示部分欄位或堆疊顯示 */
  }
}

</style> 