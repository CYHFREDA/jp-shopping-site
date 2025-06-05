<template>
  <div>
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container d-flex flex-column justify-content-center align-items-center text-center">
        <h1 class="hero-title">探索日本好物，盡在 Clevora</h1>
        <p class="hero-subtitle">我們為您精選最新、最熱門的日本商品</p>
        <router-link to="/products" class="btn btn-lg btn-light-brown mt-3">立即選購</router-link>
      </div>
    </section>

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
  router.push({ path: '/', query: { category: category === '' ? undefined : category } });
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

/* 英雄區域樣式 */
.hero-section {
  background: linear-gradient(rgba(56, 48, 46, 0.7), rgba(56, 48, 46, 0.7)), url('/images/hero-bg.jpg'); /* 深棕色半透明疊加圖片背景 */
  background-size: cover;
  background-position: center;
  color: var(--white); /* 白色文字 */
  padding: 80px 15px; /* 內邊距 */
  margin-bottom: 2rem; /* 底部間距 */
}

.hero-title {
  font-size: 3rem; /* 加大字體 */
  font-weight: bold;
  margin-bottom: 15px;
  color: var(--white); /* 白色標題 */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* 添加文字陰影 */
}

.hero-subtitle {
  font-size: 1.5rem; /* 加大副標題字體 */
  margin-bottom: 20px;
  color: var(--light-brown); /* 淺棕色副標題 */
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5); /* 添加文字陰影 */
}

/* 立即選購按鈕，使用 light-brown 風格 */
.btn-light-brown {
  background-color: var(--light-brown); /* 淺棕色背景 */
  border-color: var(--light-brown); /* 淺棕色邊框 */
  color: var(--dark-brown); /* 深棕色文字 */
  font-weight: bold;
  padding: 10px 30px;
  border-radius: 5px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.btn-light-brown:hover {
  background-color: #8b7a6c; /* 懸停時深一點的淺棕色 */
  border-color: #8b7a6c;
  color: var(--dark-brown);
}

/* 分類篩選欄樣式 */
.category-filter-bar {
  background-color: var(--light-grey); /* 淺色背景 */
  border-bottom: 1px solid var(--medium-grey); /* 底部邊框 */
  margin-bottom: 2rem; /* 添加底部間距 */
}

.category-btn {
  border-radius: 20px; /* 藥丸形狀按鈕 */
  padding: 0.375rem 1rem; /* 調整內邊距 */
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out;
}

/* 非激活按鈕 */
.category-btn {
  color: var(--dark-brown); /* 文字顏色 */
  border-color: var(--light-brown); /* 邊框顏色 */
  background-color: transparent; /* 透明背景 */
}

.category-btn:hover {
  color: var(--white); /* 懸停文字顏色 */
  background-color: var(--accent-brown); /* 懸停背景色 */
  border-color: var(--accent-brown); /* 懸停邊框顏色 */
}

/* 激活按鈕 */
.category-btn.active {
  color: var(--white); /* 激活文字顏色 */
  background-color: var(--light-brown); /* 激活背景色 */
  border-color: var(--light-brown); /* 激活邊框顏色 */
  font-weight: bold;
}

/* 頁面標題樣式 */
.page-title {
  color: var(--dark-brown); /* 深棕色標題 */
  padding-bottom: 10px; /* 標題與線的間距 */
  margin-bottom: 20px; /* 標題與內容的間距 */
  font-size: 1.8rem; /* 調整字體大小 */
  text-align: left; /* 文字靠左對齊 */
  position: relative; /* Added position: relative for pseudo-element positioning */
}

.page-title::after {
  content: '';
  display: block;
  width: 150px; /* Set a fixed width for the underline */
  height: 2px; /* Same height as the original border */
  background-color: var(--light-brown); /* Same color as the original border */
  position: absolute;
  left: 0;
  bottom: 0; /* Position the underline at the bottom */
}

/* 商品列表項樣式 */
.product-list-item {
  display: flex;
  flex-wrap: wrap; /* 允許在小螢幕換行 */
  align-items: flex-start;
  gap: 1.5rem; /* 增加間距 */
  background-color: var(--white); /* 白色背景 */
  border: 1px solid var(--light-grey); /* 淺灰色邊框 */
  border-radius: 8px; /* 圓角 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* 細微陰影 */
  transition: box-shadow 0.3s ease;
  padding: 20px; /* 內邊距 */
}

.product-list-item:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 懸停時更明顯陰影 */
}

.product-list-img {
  flex: 0 0 auto; /* 不固定寬度 */
  max-width: 200px; /* 調整圖片最大寬度 */
  border-radius: 8px; /* 圖片圓角 */
  overflow: hidden; /* 確保圖片圓角生效 */
}

.product-list-img img {
  display: block; /* 移除圖片底部的空隙 */
  width: 100%;
  height: auto;
  object-fit: cover; /* 圖片適應容器 */
  transition: transform 0.3s ease;
}

.product-list-img img:hover {
  transform: scale(1.05); /* 懸停時輕微放大 */
}

.product-list-content {
  display: flex;
  flex-direction: column;
  flex: 1; /* 佔據剩餘空間 */
}

.product-list-title {
  font-size: 1.4rem; /* 調整標題字體大小 */
  font-weight: bold;
  margin-bottom: 0.5rem; /* 調整間距 */
}

.product-list-title a {
    color: var(--dark-brown); /* 標題連結顏色 */
    text-decoration: none; /* 移除下劃線 */
    transition: color 0.2s ease;
}

.product-list-title a:hover {
    color: var(--light-brown); /* 懸停時變色 */
}

.product-list-desc {
    font-size: 1rem; /* 調整描述字體大小 */
    color: var(--disabled-text); /* 使用禁用文字顏色 */
    margin-bottom: 1rem; /* 調整間距 */
}

.product-list-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto; /* 推到底部 */
}

.product-list-price {
    font-size: 1.2rem; /* 調整價格字體大小 */
    font-weight: bold;
    color: var(--accent-brown); /* 使用強調棕色 */
}

/* 加入購物車按鈕 */
.btn-success {
   background-color: var(--dark-brown); /* 按鈕背景色 */
   border-color: var(--dark-brown); /* 按鈕邊框顏色 */
   color: var(--white); /* 按鈕文字顏色 */
   border-radius: 5px;
   transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, color 0.15s ease-in-out;
}

.btn-success:hover {
    background-color: #2a2523; /* 懸停時深一點的棕色 */
    border-color: #2a2523;
    color: var(--white);
}

/* 無資料提示文字樣式 */
.text-muted {
  font-style: italic;
  color: #6c757d !important; /* 保持灰色，與棕色調協調 */
}

/* RWD 調整 */
@media (max-width: 768px) {
  .hero-section {
    padding: 60px 15px; /* 小螢幕調整內邊距 */
  }

  .hero-title {
    font-size: 2.2rem; /* 小螢幕調整字體大小 */
  }

  .hero-subtitle {
    font-size: 1.2rem; /* 小螢幕調整字體大小 */
  }

  .product-list-item {
    flex-direction: column; /* 小螢幕圖片和內容垂直排列 */
    align-items: center; /* 小螢幕居中 */
  }

  .product-list-img {
    max-width: 150px; /* 小螢幕調整圖片最大寬度 */
    margin-bottom: 1rem; /* 小螢幕圖片下方間距 */
    margin-right: 0; /* 移除右側間距 */
  }

  .product-list-content {
    text-align: center; /* 小螢幕內容文字居中 */
    width: 100%; /* 小螢幕佔滿寬度 */
  }

  .product-list-bottom {
    flex-direction: column; /* 小螢幕價格和按鈕垂直排列 */
    align-items: center; /* 小螢幕居中 */
    gap: 10px; /* 添加間距 */
  }

  .product-list-price {
      margin-bottom: 0.5rem; /* 小螢幕價格下方間距 */
  }
}

@media (max-width: 576px) {
  .hero-section {
    padding: 40px 10px; /* 更小的螢幕調整內邊距 */
  }

  .hero-title {
    font-size: 1.8rem; /* 更小的螢幕調整字體大小 */
  }

  .hero-subtitle {
    font-size: 1rem; /* 更小的螢幕調整字體大小 */
  }
}
</style>
