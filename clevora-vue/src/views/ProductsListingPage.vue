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
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title fw-bold">商品列表</h1>
    </div>
    
    <div v-if="paginatedProducts.length" class="row row-cols-1 g-3">
      <div v-for="product in paginatedProducts" :key="product.id" class="col">
        <div class="product-list-item shadow-sm rounded mb-3 p-3 bg-white">
          <div class="product-list-img me-3 mb-3 mb-md-0">
            <router-link :to="`/product/${product.id}`">
              <img :src="product.image_url || 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'" :alt="product.name" class="img-fluid" />
            </router-link>
          </div>
          <div class="product-list-content">
            <h5 class="product-list-title mb-2">
              <router-link :to="`/product/${product.id}`" class="text-decoration-none">
                {{ product.name }}
              </router-link>
            </h5>
            <p class="product-list-desc mb-2">{{ product.description || '' }}</p>
            <div class="product-list-bottom">
              <div class="product-list-price">NT$ {{ product.price?.toFixed(0) || '未定價' }}</div>
              <button class="btn btn-success btn-sm" @click="addToCart(product)">加入購物車</button>
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

// 監聽路由變化以更新搜尋查詢和分頁
watch(() => route.query.search, (newSearch) => {
  if (newSearch) {
    searchQuery.value = newSearch;
  } else {
    searchQuery.value = '';
  }
  currentPage.value = 1; // 搜尋或分類變化時回到第一頁
}, { immediate: true });

watch(() => route.query.category, (newCategory) => {
  selectedCategory.value = newCategory || '';
  searchQuery.value = '';
  currentPage.value = 1; // 搜尋或分類變化時回到第一頁
}, { immediate: true });

// 監聽每頁顯示數量變化，回到第一頁
watch(itemsPerPage, () => {
    currentPage.value = 1;
});

// 根據篩選條件計算過濾後的商品
const filteredProducts = computed(() => {
  let products = allProducts.value;

  if (selectedCategory.value) {
    products = products.filter(p => {
      const categories = (p.category || '').split('#');
      return categories.includes(selectedCategory.value);
    });
  }

  if (searchQuery.value) {
    const keyword = searchQuery.value.toLowerCase();
    products = products.filter(p => 
      p.name.toLowerCase().includes(keyword) || 
      (p.description && p.description.toLowerCase().includes(keyword))
    );
  }

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
    const res = await axios.get('/api/products');
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
     // 初始化時根據路由設定分類
     if (route.query.category) {
        selectedCategory.value = route.query.category;
     }
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

const filterCategory = (category) => {
  // 不再直接修改 selectedCategory，而是通過路由監聽來更新
  // selectedCategory.value = category;
  searchQuery.value = '';
  router.push({ path: '/products', query: { category: category === '' ? undefined : category } }); // Change path to /products
};

const addToCart = (product) => {
  cartStore.addItem(product);
  alert('✅ 已加入購物車！');
};

onMounted(() => {
  loadProducts();
});
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

/* 類別篩選條樣式 */
.category-filter-bar {
  background-color: var(--white);
  padding: 10px 0;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.category-btn {
  background-color: var(--light-grey);
  color: var(--dark-brown);
  border: 1px solid var(--medium-grey);
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
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
.product-list-item {
  display: flex;
  align-items: flex-start; /* 讓圖片和內容從頂部對齊 */
  border: 1px solid var(--medium-grey);
  border-radius: 8px;
  overflow: hidden; /* 防止內容溢出圓角 */
  background-color: var(--white);
}

.product-list-img {
  flex-shrink: 0; /* 防止圖片縮小 */
  width: 150px; /* 固定圖片寬度 */
  height: 150px; /* 固定圖片高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--light-grey); /* 圖片背景色 */
  border-right: 1px solid var(--medium-grey); /* 右側邊框 */
  padding: 10px; /* 圖片內邊距 */
}

.product-list-img img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain; /* 確保圖片內容完整顯示 */
}

.product-list-content {
  flex-grow: 1;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-list-title {
  color: var(--dark-brown);
  font-size: 1.15rem;
  font-weight: bold;
}

.product-list-desc {
  color: #6c757d; /* 描述文字顏色 */
  font-size: 0.9rem;
  line-height: 1.5;
  flex-grow: 1; /* 讓描述佔據剩餘空間 */
}

.product-list-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.product-list-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--accent-brown); /* 價格顏色 */
}

/* 頁碼 */
.pagination .page-item .page-link {
    color: var(--dark-brown);
    background-color: var(--white);
    border: 1px solid var(--medium-grey);
}

.pagination .page-item.disabled .page-link {
    color: var(--disabled-text);
}

.pagination .page-item.active .page-link,
.pagination .page-item .page-link:hover {
    background-color: var(--light-brown);
    border-color: var(--light-brown);
    color: var(--white);
}

/* RWD 調整 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  .hero-subtitle {
    font-size: 1rem;
  }

  .product-list-item {
    flex-direction: column; /* 小螢幕堆疊 */
    align-items: center;
    text-align: center;
  }

  .product-list-img {
    width: 100%; /* 小螢幕圖片佔滿寬度 */
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--medium-grey); /* 底部邊框 */
    margin-bottom: 10px;
  }

  .product-list-content {
    padding: 10px;
  }

  .product-list-bottom {
    flex-direction: column; /* 小螢幕按鈕堆疊 */
    gap: 10px;
  }

  .product-list-price {
    margin-bottom: 5px;
  }
}

@media (max-width: 576px) {
  .hero-title {
    font-size: 2rem;
  }
  .hero-subtitle {
    font-size: 0.9rem;
  }

  .category-filter-bar {
    padding: 8px 0;
  }

  .category-btn {
    padding: 6px 12px;
    font-size: 0.8rem;
  }
}
</style> 