<template>
  <div class="products-page-center">
    <div class="card p-4">
      <h5 class="card-title mb-3">🛍️ 商品管理</h5>
      
      <!-- 訊息提示 -->
      <div v-if="displayMessage" class="alert text-center mb-3" :class="{ 'alert-success': displayMessage.includes('✅'), 'alert-danger': displayMessage.includes('❌') }">
        {{ displayMessage }}
      </div>

      <!-- 新增商品表單 -->
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
      <!-- 桌機版商品表格 -->
      <div class="table-responsive d-none d-md-block mt-4">
        <table class="table table-striped table-bordered">
          <thead>
            <tr>
              <th>商品ID</th>
              <th>名稱</th>
              <th>價格</th>
              <th>分類</th>
              <th>建立時間</th>
              <th class="text-end">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in pagedProducts" :key="product.id">
              <td>{{ product.id }}</td>
              <td>{{ product.name }}</td>
              <td>
                <span class="price-currency">NT$</span> {{ product.price }}
              </td>
              <td>
                <span v-if="product.category">
                  <span v-for="cat in (Array.isArray(product.category) ? [...new Set(product.category)] : [...new Set(product.category.split('#'))])" :key="cat" class="badge rounded-pill category-badge">{{ categoryMap[cat] || cat }}</span>
                </span>
              </td>
              <td class="nowrap">{{ formatDateTime(product.created_at) }}</td>
              <td class="text-end">
                <div class="action-btns flex-row gap-2">
                  <button class="btn btn-primary btn-sm me-1" @click="openEditModal(product)">編輯</button>
                  <button class="btn btn-danger btn-sm" @click="handleDeleteProduct(product.id)">刪除</button>
                </div>
              </td>
            </tr>
            <tr v-if="pagedProducts.length === 0">
              <td colspan="6" class="text-center text-muted">目前沒有商品</td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 分頁控制區（移到表格下方） -->
      <div class="d-flex justify-content-between align-items-center mt-2 mb-2">
        <div>
          <label class="me-2">每頁顯示</label>
          <select v-model="pageSize" class="form-select d-inline-block w-auto page-size-select" style="min-width: 70px;">
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
          <span class="ms-2">項</span>
        </div>
        <div>
          <button class="btn btn-outline-secondary btn-sm me-1" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">上一頁</button>
          <span>第 {{ currentPage }} / {{ totalPages }} 頁</span>
          <button class="btn btn-outline-secondary btn-sm ms-1" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">下一頁</button>
        </div>
      </div>
      <!-- 手機版卡片 -->
      <div class="d-block d-md-none mt-4">
        <AdminCardList :items="products" :fields="cardFields" key-field="id" />
      </div>
    </div>

    <!-- 編輯商品 Modal -->
    <div class="modal fade" :class="{ show: showEditModal }" tabindex="-1" style="display: block;" v-if="showEditModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">編輯商品</h5>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">商品名稱</label>
              <input v-model="editProduct.name" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">價格</label>
              <input v-model="editProduct.price" type="number" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">商品描述</label>
              <input v-model="editProduct.description" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">圖片網址</label>
              <input v-model="editProduct.image_url" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">分類</label>
              <div class="category-checkboxes">
                <label v-for="(label, key) in categoryMap" :key="key" class="category-tag">
                  <input type="checkbox" v-model="editProduct.categories" :value="key" />
                  <span>{{ label }}</span></label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" @click="closeEditModal">取消</button>
            <button type="button" class="btn btn-primary btn-sm" @click="saveEditProduct">儲存</button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/api';
import AdminCardList from '@/components/AdminCardList.vue';

const products = ref([]);
const userStore = useUserStore();
const displayMessage = ref(''); // 新增響應式變數用於顯示訊息

const newProduct = ref({
  name: '',
  price: '',
  description: '',
  image_url: '',
  categories: []
});

const cardFields = [
  { key: 'id', label: '商品ID' },
  { key: 'name', label: '名稱' },
  { key: 'price', label: '價格', formatter: v => `NT$ ${v}` },
  { key: 'category', label: '分類' },
  { key: 'created_at', label: '建立時間' },
];

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

const showEditModal = ref(false);
const editProduct = reactive({
  id: '',
  name: '',
  price: '',
  description: '',
  image_url: '',
  categories: []
});

const pageSize = ref(20);
const currentPage = ref(1);
const pagedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return products.value.slice(start, start + pageSize.value);
});
const totalPages = computed(() => Math.ceil(products.value.length / pageSize.value) || 1);

onMounted(() => {
  loadProducts();
  displayMessage.value = ''; // 在組件載入時清除訊息
});

async function loadProducts() {
  displayMessage.value = ''; // 清除之前的訊息
  const token = userStore.admin_token;
  if (!token) {
    console.error('未找到認證 token！');
    displayMessage.value = '❌ 請先登入！';
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
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else {
       displayMessage.value = '❌ 載入商品資料失敗！';
    }
  }
}

async function handleAddProduct() {
  displayMessage.value = ''; // 清除之前的訊息
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
     console.error('未找到認證 token！');
     displayMessage.value = '❌ 請先登入！';
     return;
  }

  try {
    const res = await api.post('/api/admin/products', { name, price, description, image_url, category });

    // 直接從 res.data 獲取結果，Axios 已自動解析
    const result = res.data;

    // 如果請求成功（Axios 狀態碼在 2xx），執行以下邏輯
    displayMessage.value = result.message || '✅ 商品新增成功！'; // 彈出成功提示
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
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else {
      // 嘗試從錯誤響應中獲取後端返回的錯誤信息
      const errorMessage = error.response?.data?.error || error.message || '新增商品失敗！';
      displayMessage.value = `❌ ${errorMessage}`;
    }
  }
}

async function handleSaveProduct(product) {
  displayMessage.value = ''; // 清除之前的訊息
  const { name, price, description, image_url, categories } = product;
  const category = categories.join("#");

  if (!name || !price) {
    displayMessage.value = "❌ 請填寫完整商品名稱與價格！";
    return;
  }

  if (category.length > 255) {
    displayMessage.value = "❌ 分類超過 255 字元限制，請刪減分類！";
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     displayMessage.value = '❌ 請先登入！';
     return;
  }

  try {
    const res = await api.put(`/api/admin/products/${product.id}`, { name, price, description, image_url, category });

    const result = res.data; // Axios 已自動解析為 JSON

    if (res.status !== 200) {
       console.error('更新商品失敗：', result);
       displayMessage.value = result.error || '❌ 更新商品失敗！';
    } else {
       displayMessage.value = result.message || '✅ 商品更新成功！';
       loadProducts(); // 更新成功後重新載入商品資料
    }

  } catch (error) {
    console.error('更新商品時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else {
      const errorMessage = error.response?.data?.error || error.message || '更新商品失敗！';
      displayMessage.value = `❌ ${errorMessage}`;
    }
  }
}

async function handleDeleteProduct(id) {
  displayMessage.value = ''; // 清除之前的訊息
  if (!confirm("確定刪除這個商品？")) {
    displayMessage.value = '取消刪除商品！';
    return;
  }

  const token = userStore.admin_token;
  if (!token) {
     console.error('未找到認證 token！');
     displayMessage.value = '❌ 請先登入！';
     return;
  }

  try {
    const res = await api.delete(`/api/admin/products/${id}`);

    const result = res.data; // Axios 已自動解析為 JSON

    if (res.status !== 200) {
      console.error('刪除商品失敗：', result);
      displayMessage.value = result.error || '❌ 刪除商品失敗！';
    } else {
      displayMessage.value = result.message || '✅ 商品刪除成功！';
      loadProducts(); // 刪除成功後重新載入商品資料
    }
  } catch (error) {
    console.error('刪除商品時發生錯誤：', error);
    if (error.response && error.response.status === 401) {
      displayMessage.value = '❌ 認證失敗，請重新登入！';
    } else {
      const errorMessage = error.response?.data?.error || error.message || '刪除商品失敗！';
      displayMessage.value = `❌ ${errorMessage}`;
    }
  }
}

function openEditModal(product) {
  editProduct.id = product.id;
  editProduct.name = product.name;
  editProduct.price = product.price;
  editProduct.description = product.description;
  editProduct.image_url = product.image_url;
  // 支援陣列或字串
  editProduct.categories = Array.isArray(product.category)
    ? [...product.category]
    : (product.category ? product.category.split('#') : []);
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
}

async function saveEditProduct() {
  await handleSaveProduct({
    id: editProduct.id,
    name: editProduct.name,
    price: editProduct.price,
    description: editProduct.description,
    image_url: editProduct.image_url,
    categories: editProduct.categories
  });
  showEditModal.value = false;
}

function changePage(page) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
}

watch([pageSize, products], () => {
  currentPage.value = 1;
});

function formatDateTime(dt) {
  if (!dt) return '';
  const date = new Date(dt);
  const twDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  return twDate.toLocaleString('zh-TW', { hour12: false });
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
}

/* 提升卡片的質感 */
.card {
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  /* 可以添加一些背景色或者留白 */
  background-color: var(--white); /* 使用白色背景 */
}

/* 商品管理表格美化：字體變小、欄寬變大 */
.table th, .table td {
  font-size: 0.92rem;
  padding: 10px 14px;
}
.table thead th {
  font-size: 0.97rem;
}

/* 表格樣式優化 */
.table {
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(56,48,46,0.10);
  border: 1px solid #e9e0d8;
  overflow: hidden;
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
  background-color: #faf7f3;
}

.table tbody tr:hover {
  background-color: #f3edea;
  transition: background 0.2s;
}

.table td {
  font-size: 0.97rem;
  color: #38302e;
}

/* 輸入框樣式微調 */
.form-control {
  border-radius: 5px;
  border-color: var(--light-brown); /* 輸入框邊框顏色 */
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  font-size: 0.97rem;
}

.form-control:focus {
  border-color: var(--accent-brown); /* 聚焦時邊框顏色 */
  box-shadow: 0 0 0 0.25rem rgba(161, 138, 123, 0.25); /* 根據 light-brown 調整陰影顏色 */
}

/* 按鈕樣式微調 */
.btn, .btn-success, .btn-danger, .btn-primary, .btn-secondary, .btn-outline-secondary {
  font-size: 0.97rem !important;
  padding: 0.35rem 1rem !important;
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

/* 成功按鈕 (新增商品) */
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

/* 美化分類checkbox標籤，讓每行最多4個，間距一致，自動換行且整齊對齊 */
.category-checkboxes {
  display: flex;
  flex-wrap: nowrap;
  gap: 12px;
  margin-top: 4px;
  overflow-x: auto;
  scrollbar-width: thin;
  scrollbar-color: #a18a7b #f3edea;
}
.category-checkboxes label {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 13px;
  background: #f3edea;
  color: #38302e;
  border: 1.5px solid #a18a7b;
  padding: 4px 0;
  font-size: 0.92rem;
  font-weight: 500;
  transition: background 0.2s, color 0.2s, border 0.2s, box-shadow 0.2s;
  user-select: none;
  position: relative;
  box-shadow: 0 1px 4px rgba(161,138,123,0.07);
}
.category-checkboxes input[type='checkbox'] {
  display: none;
}
.category-checkboxes input[type='checkbox']:checked + span,
.category-checkboxes input[type='checkbox']:checked ~ span {
  background: #a18a7b;
  color: #fff;
  border-color: #a18a7b;
  box-shadow: 0 2px 8px rgba(161, 138, 123, 0.15);
  padding: 4px 14px;
  border-radius: 16px;
}
.category-checkboxes label:hover {
  background: #e9e0d8;
  border-color: #c8a99a;
  color: #38302e;
}
.category-checkboxes input[type='checkbox']:checked + span:hover,
.category-checkboxes input[type='checkbox']:checked ~ span:hover {
  background: #38302e;
  color: #fff;
  border-color: #38302e;
}
.category-checkboxes span {
  padding: 0 2px;
  border-radius: 16px;
  transition: background 0.2s, color 0.2s;
  width: 100%;
  text-align: center;
  font-size: 0.92rem;
}

/* 無資料提示文字樣式 */
.text-muted {
  font-style: italic;
  color: #a18a7b !important;
}

/* 響應式調整表格 */
@media (max-width: 768px) {
  .table-responsive .table {
    /* 在小螢幕上可以考慮不顯示部分欄位或堆疊顯示 */
  }
}

.products-page-center {
  max-width: 1400px;
  margin: 0 auto;
  padding-top: 24px;
}

.category-badge {
  background: #a18a7b;
  color: #fff;
  font-size: 0.95rem;
  margin-right: 4px;
  margin-bottom: 2px;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.modal {
  display: block;
  background: rgba(0,0,0,0.2);
  z-index: 1051 !important;
}
.modal-backdrop {
  z-index: 1040 !important;
  pointer-events: none !important;
  background: transparent !important;
}

/* 新增商品按鈕靠右且更融入整體排版 */
.add-product-btn {
  height: 38px !important;
  min-width: 90px;
  padding: 0 18px;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  box-sizing: border-box;
}

/* 編輯、刪除按鈕並排顯示，間距更小 */
.action-btns {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 32px;
}

.action-btns .btn {
  height: 32px;
  min-width: 56px;
  padding: 0 14px;
  font-size: 0.98rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  border-radius: 7px;
  white-space: nowrap !important;
}

.action-btns .btn-primary {
  background-color: #a18a7b;
  border-color: #a18a7b;
  color: #38302e;
}
.action-btns .btn-primary:hover {
  background-color: #f3edea;
  border-color: #c8a99a;
  color: #38302e;
}

.pagination {
  margin: 0;
}

/* 新增搜尋列、select、按鈕高度統一 */
.search-input, .form-select, .add-product-btn, .page-size-select {
  height: 38px !important;
  font-size: 1rem;
  box-sizing: border-box;
}

/* 商品ID欄位更窄且字體自動縮小，保持水平排列 */
.table th:first-child, .table td:first-child {
  min-width: 80px;
  width: 90px;
  max-width: 120px;
  text-align: center;
  font-size: 0.88rem;
  white-space: nowrap;
  letter-spacing: 0.5px;
}
/* 名稱欄位自動換行、字體再小一點 */
.table td:nth-child(2) {
  font-size: 0.92rem;
  word-break: break-all;
  white-space: pre-line;
  line-height: 1.5;
}
/* 價格欄位寬度適中，字體縮小且不換行 */
.table th:nth-child(3), .table td:nth-child(3) {
  min-width: 80px;
  text-align: right;
  font-size: 0.90rem;
  white-space: nowrap;
}
.table th:nth-child(4), .table td:nth-child(4) {
  min-width: 120px;
}
/* 建立時間欄位字體更小、顏色偏灰 */
.table td:nth-child(5) {
  font-size: 0.88rem;
  color: #a18a7b;
}
/* 行高拉高，偶數行底色更淡 */
.table td, .table th {
  line-height: 1.7;
  vertical-align: middle;
}
/* 表格圓角、陰影、邊框更細緻 */
.table {
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(56,48,46,0.10);
  border: 1px solid #e9e0d8;
  overflow: hidden;
}
/* 操作欄標題與按鈕完全置中 */
.table th:last-child, .table td:last-child {
  text-align: center;
  vertical-align: middle;
}

.card-title {
  font-size: 1.18rem;
}

.price-currency {
  font-size: 0.82em;
  color: #a18a7b;
  margin-right: 2px;
  white-space: nowrap;
  vertical-align: middle;
}

.nowrap {
  white-space: nowrap;
}
</style> 