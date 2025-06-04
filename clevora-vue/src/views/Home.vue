<template>
  <div>
    <div class="bg-white border-bottom shadow-sm">
      <div class="container py-2 d-flex flex-wrap gap-2 justify-content-center">
        <button
          v-for="category in categories"
          :key="category.value"
          class="btn btn-outline-secondary btn-sm category-btn"
          :class="{ active: selectedCategory === category.value }"
          @click="filterCategory(category.value)"
        >
          {{ category.label }}
        </button>
      </div>
    </div>

    <div class="container py-4">
      <h1 class="mb-4 fw-bold text-center">商品列表</h1>
      <div v-if="filteredProducts.length" class="row row-cols-1 g-3">
        <div v-for="product in filteredProducts" :key="product.id" class="col">
          <div class="product-list-item shadow-sm rounded mb-3 p-3 bg-white">
            <div class="product-list-img me-3 mb-3 mb-md-0">
              <router-link :to="`/product/${product.id}`">
                <img :src="product.image_url || 'https://via.placeholder.com/150'" :alt="product.name" class="img-fluid" />
              </router-link>
            </div>
            <div class="product-list-content">
              <h5 class="product-list-title mb-2">
                <router-link :to="`/product/${product.id}`" class="text-decoration-none text-dark">
                  {{ product.name }}
                </router-link>
              </h5>
              <p class="product-list-desc mb-2">{{ product.description || '' }}</p>
              <div class="product-list-bottom">
                <div class="product-list-price">NT$ {{ product.price }}</div>
                <button class="btn btn-success btn-sm" @click="addToCart(product)">加入購物車</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-center text-muted">找不到符合條件的商品</p>
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

// 監聽路由變化以更新搜尋查詢
watch(() => route.query.search, (newSearch) => {
  if (newSearch) {
    searchQuery.value = newSearch;
  } else {
    searchQuery.value = '';
  }
}, { immediate: true });

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

const loadProducts = async () => {
  try {
    console.log('開始載入商品...');
    const res = await axios.get('/products');
    console.log('API 回應：', res.data);
    allProducts.value = res.data;
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
  selectedCategory.value = category;
  searchQuery.value = '';
  router.push({ path: '/', query: { category: category === '' ? undefined : category } });
};

const addToCart = (product) => {
  cartStore.addItem(product);
};

onMounted(() => {
  loadProducts();
});
</script>

<style scoped>
/* 可以在這裡添加 Home.vue 特有的樣式 */
/* 參考 index.css 中的商品列表等相關樣式 */
.product-list-item {
  display: flex;
  flex-wrap: nowrap;
  align-items: flex-start;
  gap: 1rem;
}

.product-list-img {
  flex: 0 0 150px;
  max-width: 150px;
}

.product-list-img img {
  width: 100%;
  height: auto;
  object-fit: contain;
  border-radius: 0.25rem;
  transition: transform 0.3s ease;
}

.product-list-img img:hover {
  transform: scale(1.1);
}

.product-list-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.product-list-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.product-list-desc {
  font-size: 0.95rem;
  color: #555;
  flex-grow: 1;
}

.product-list-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.product-list-price {
  font-size: 1rem;
  font-weight: bold;
  color: #d63384;
}

#searchInput {
  width: 120px;
}

/* Removed .bg-white override as it should be a global style */
/* .bg-white {
  background-color: #9c8282;
} */

#categoryFilters label {
  display: inline-flex;
  align-items: center;
}

/* RWD */
@media (max-width: 576px) {
  .product-list-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .product-list-img {
    margin-right: 0;
    margin-bottom: 1rem;
  }
}
</style>
