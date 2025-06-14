<template>
  <div class="category-filter-bar border-bottom shadow-sm">
    <div class="container py-2 d-flex flex-wrap gap-2 justify-content-center">
      <button
        v-for="category in categories"
        :key="category.value"
        class="btn btn-sm category-btn"
        :class="{ active: selectedCategory === category.value }"
        @click="filterCategory(category.value)"
      >
        {{ category.label }}
      </button>
    </div>
  </div>

  <div class="container py-4">
    <div class="page-title-container d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title fw-bold">商品列表</h1>
      <div class="page-title-underline"></div>
    </div>
    
    <div v-if="paginatedProducts.length" class="row row-cols-1 row-cols-md-3 g-4">
      <div v-if="addToCartMessage" class="alert alert-success text-center mb-3" role="alert">
        {{ addToCartMessage }}
      </div>
      <div v-for="product in paginatedProducts" :key="product.id" class="col">
        <div class="product-grid-card shadow-sm rounded bg-white h-100 d-flex flex-column align-items-center">
          <router-link :to="`/product/${product.id}`" class="product-grid-img-wrapper">
            <img :src="product.image_url || 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'" :alt="product.name" class="product-grid-img" />
          </router-link>
          <div class="product-grid-content flex-grow-1 d-flex flex-column justify-content-between p-2 w-100">
            <h6 class="product-grid-title mb-2 text-center">
              <router-link :to="`/product/${product.id}`" class="text-decoration-none">
                {{ product.name }}
              </router-link>
            </h6>
            <div class="product-grid-bottom mt-auto">
              <div class="product-grid-price mb-2 text-center">NT$ {{ product.price?.toFixed(0) || '未定價' }}</div>
              <button class="btn btn-success btn-sm w-100" @click="addToCart(product)">加入購物車</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-center text-muted">找不到符合條件的商品</p>
    
    <!-- 分頁控制項 和 每頁顯示控制項 -->
    <div v-if="filteredProducts.length > 0" class="d-flex justify-content-center align-items-center mt-4">
      <nav v-if="filteredProducts.length > itemsPerPage" class="me-4">
        <ul class="pagination mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">上一頁</button>
          </li>
          <li class="page-item disabled">
              <span class="page-link">{{ currentPage }} / {{ totalPages }}</span>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link" @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">下一頁</button>
          </li>
        </ul>
      </nav>

      <div class="d-flex align-items-center">
         <span class="me-2">共 {{ filteredProducts.length }} 項</span>
         <label for="itemsPerPage" class="form-label me-2 mb-0">每頁顯示:</label>
         <select id="itemsPerPage" v-model="itemsPerPage" class="form-select form-select-sm w-auto">
           <option :value="20">20</option>
           <option :value="50">50</option>
           <option :value="100">100</option>
         </select>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { useCartStore } from '@/stores/cartStore';
import { useCustomerStore } from '@/stores/customerStore';
import { useRoute, useRouter } from 'vue-router';

const allProducts = ref([]);
const selectedCategory = ref('');
const searchQuery = ref('');
const route = useRoute();
const router = useRouter();

const cartStore = useCartStore();
const customerStore = useCustomerStore();

const categories = ref([
  { label: '全部商品', value: '' },
  { label: '限時搶購', value: 'flashsale' },
  { label: '限定SALE', value: 'sale' },
  { label: '日本藥品', value: 'japan_medicine' },
  { label: '食品/飲料/酒', value: 'food_drink' },
  { label: '美妝/美髮/肌膚護理', value: 'beauty' },
  { label: '男士用品', value: 'men' },
  { label: '生活家用/沐浴&身體', value: 'home' },
  { label: '親子育兒', value: 'baby' },
]);

// --- 分頁相關狀態 ---
const currentPage = ref(1); // 當前頁碼
const itemsPerPage = ref(20); // 每頁顯示數量

// 監聽每頁顯示數量變化，回到第一頁
watch(itemsPerPage, () => {
    currentPage.value = 1;
});

// 根據篩選條件計算過濾後的商品
const filteredProducts = computed(() => {
  let products = allProducts.value;

  return products;
});

// 計算總頁數
const totalPages = computed(() => {
  return Math.ceil(filteredProducts.value.length / itemsPerPage.value);
});

// 計算當前頁顯示的商品
const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredProducts.value.slice(start, end);
});

// 切換頁碼
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};
// --- 分頁相關狀態結束 ---

const loadProducts = async () => {
  try {
    console.log('開始載入商品...');
    // 增加日誌以確認傳遞的搜尋參數
    console.log('傳遞給後端的搜尋查詢 (query): ', route.query.search);
    console.log('傳遞給後端的分類 (category): ', route.query.category);

    const res = await axios.get('/api/products', {
      params: {
        query: route.query.search || '', // 直接使用 route.query
        category: route.query.category || '' // 直接使用 route.query
      }
    });
    console.log('API 回應：', res.data);
    allProducts.value = res.data.map(p => ({
      id: p[0],
      name: p[1],
      price: p[2],
      description: p[3],
      image_url: p[4],
      created_at: p[5],
      category: p[6]
    }));
     // selectedCategory 和 searchQuery 的更新由 watch 處理
     // if (route.query.category) {
     //    selectedCategory.value = route.query.category;
     // }
  } catch (error) {
    console.error('載入商品時發生錯誤：', error);
    if (error.response) {
      console.error('錯誤狀態碼：', error.response.status);
      console.error('錯誤資料：', error.response.data);
    } else if (error.request) {
      console.error('請求已發送但沒有收到回應');
    } else {
      console.error('設定請求時發生錯誤：', error.message);
    }
  }
};

// 新增聯合監聽器，用於在路由查詢參數變化時重新載入商品
watch([() => route.query.search, () => route.query.category], ([newSearch, newCategory]) => {
  searchQuery.value = newSearch || ''; // 更新本地的 searchQuery
  selectedCategory.value = newCategory || ''; // 更新本地的 selectedCategory
  currentPage.value = 1; // 重置到第一頁
  loadProducts(); // 重新載入商品
}, { immediate: true }); // 立即執行一次，用於初始載入

const filterCategory = (category) => {
  // 不再直接修改 selectedCategory，而是通過路由監聽來更新
  searchQuery.value = ''; // 清空搜尋欄，因為正在進行分類過濾
  router.push({ path: '/products', query: { category: category === '' ? undefined : category } });
};

const addToCart = (product) => {
  cartStore.addItem({ ...product, quantity: 1 });
  alert('✅ 已加入購物車！');
};

// onMounted 不再需要呼叫 loadProducts，因為 watch 已經處理了初始載入
// onMounted(() => {
//   loadProducts();
// });
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
  --disabled-text: #6c757d; /* 用於禁用文字的顏色 */
}

/* 頁面標題樣式 */
.page-title-container {
  position: relative;
  margin-bottom: 20px;
}

.page-title {
  color: var(--dark-brown);
  font-size: 1.8rem;
  font-weight: bold;
  padding-bottom: 10px;
  margin-bottom: 0; /* 移除 h1 預設的 margin-bottom */
}

.page-title-underline {
  content: '';
  display: block;
  width: 100%; /* 調整下劃線長度 */
  height: 3px; /* 調整下劃線粗細 */
  background-color: var(--light-brown);
  position: absolute;
  left: 0;
  bottom: 0;
}

/* 類別篩選條樣式 */
.category-filter-bar {
  background-color: var(--white);
  padding: 15px 0; /* 增加上下內邊距 */
  margin-bottom: 2.5rem; /* 增加底部間距 */
  box-shadow: 0 4px 8px rgba(0,0,0,0.05); /* 增加陰影強度 */
}

.category-btn {
  background-color: var(--light-grey);
  color: var(--dark-brown);
  border: 1px solid var(--medium-grey);
  padding: 10px 20px; /* 增加內邊距 */
  border-radius: 25px; /* 更圓潤 */
  font-size: 1rem;
  transition: all 0.3s ease;
}

.category-btn:hover {
  background-color: var(--accent-brown);
  color: var(--white);
  border-color: var(--accent-brown);
}

.category-btn.active {
  background-color: var(--dark-brown);
  color: var(--white);
  border-color: var(--dark-brown);
}

/* 商品列表項樣式 */
.product-grid-card {
  border: 1px solid var(--medium-grey);
  border-radius: 10px;
  overflow: hidden;
  background-color: var(--white);
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  transition: box-shadow 0.3s;
}
.product-grid-card:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.12);
}
.product-grid-img-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--light-grey);
  padding: 16px 0 0 0;
}
.product-grid-img {
  width: 120px;
  height: 120px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
  transition: transform 0.3s;
}
.product-grid-card:hover .product-grid-img {
  transform: scale(1.08);
}
.product-grid-title {
  color: var(--dark-brown);
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-align: center;
}
.product-grid-desc {
  color: var(--disabled-text);
  font-size: 0.9rem;
  min-height: 2.5em;
  text-align: center;
  margin-bottom: 0.5rem;
}
.product-grid-price {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--accent-brown);
  text-align: center;
}
.product-grid-bottom {
  width: 100%;
}

/* 加入購物車按鈕樣式 */
.btn-success {
    background-color: var(--dark-brown); /* 使用深棕色 */
    border-color: var(--dark-brown);
    color: var(--white);
    border-radius: 20px; /* 圓潤按鈕 */
    padding: 8px 18px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.btn-success:hover {
    background-color: #2a2523; /* 懸停時更深一點 */
    border-color: #2a2523;
    color: var(--white);
}

/* 分頁樣式 */
.pagination .page-item .page-link {
    color: var(--dark-brown);
    background-color: var(--white);
    border: 1px solid var(--medium-grey);
    border-radius: 5px; /* 輕微圓角 */
    margin: 0 2px; /* 頁碼間距 */
    transition: all 0.3s ease;
}

.pagination .page-item.disabled .page-link {
    color: var(--disabled-text);
    background-color: var(--light-grey);
    border-color: var(--medium-grey);
    cursor: not-allowed;
}

.pagination .page-item.active .page-link,
.pagination .page-item .page-link:hover {
    background-color: var(--light-brown);
    border-color: var(--light-brown);
    color: var(--white);
}

.form-select.form-select-sm {
  border-color: var(--medium-grey);
  color: var(--dark-brown);
}

/* RWD 調整 */
@media (max-width: 992px) {
  .row-cols-md-3 > .col {
    flex: 0 0 50%;
    max-width: 50%;
  }
}
@media (max-width: 768px) {
  .row-cols-md-3 > .col {
    flex: 0 0 100%;
    max-width: 100%;
  }
  .product-grid-img {
    width: 90px;
    height: 90px;
  }
}

@media (max-width: 576px) {
  .page-title {
    font-size: 1.5rem;
  }

  .page-title-underline {
    width: 60px; /* 小螢幕調整下劃線長度 */
  }

  .category-filter-bar {
    padding: 10px 0;
    margin-bottom: 2rem;
  }

  .category-btn {
    padding: 8px 15px;
    font-size: 0.9rem;
  }

  .product-grid-img {
    width: 150px; /* 小螢幕圖片寬度 */
    height: 150px; /* 小螢幕圖片高度 */
  }

  .product-grid-title {
    font-size: 1.1rem;
  }

  .product-grid-desc {
    font-size: 0.85rem;
  }

  .product-grid-price {
    font-size: 1.2rem;
  }
}
</style> 