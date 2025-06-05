<template>
  <div class="container my-5">
    <div v-if="product" class="row product-detail-container">
      <div class="col-md-6">
        <img :src="product.image_url || 'https://picsum.photos/400'" :alt="product.name" class="img-fluid rounded product-image">
      </div>
      <div class="col-md-6 product-info">
        <h1 class="product-title mb-3">{{ product.name }}</h1>
        <p class="product-price fs-4">NT$ {{ product.price }}</p>
        <p class="product-description">{{ product.description || '無商品描述' }}</p>
        
        <div v-if="errorMessage" class="alert alert-danger text-center mt-3 mb-3" role="alert">
          {{ errorMessage }}
        </div>

        <div class="mb-3">
          <label for="quantity" class="form-label product-quantity-label">數量：</label>
          <input type="number" id="quantity" v-model.number="quantity" min="1" class="form-control w-auto product-quantity-input">
        </div>
        
        <button class="btn btn-success btn-lg add-to-cart-btn" @click="addItemToCart">
          <i class="fas fa-shopping-cart"></i> 加入購物車
        </button>
      </div>
    </div>
    <div v-else class="text-center text-muted">
      載入商品資料中或商品不存在...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useCartStore } from '@/stores/cartStore';

const route = useRoute();
const cartStore = useCartStore();

const product = ref(null);
const quantity = ref(1);
const errorMessage = ref(''); // 新增響應式變數用於顯示錯誤訊息

async function loadProductDetail() {
  errorMessage.value = ''; // 清除之前的訊息
  const productId = route.params.id;
  if (!productId) {
    console.error('商品 ID 未提供！');
    errorMessage.value = '❌ 商品 ID 未提供！';
    return;
  }
  
  try {
    // 假設後端 API 有 /products/:id 的端點來獲取單一商品資料
    const res = await fetch(`/api/products/${productId}`);

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`無法載入商品 ID ${productId} 的資料：`, res.status, errorText);
      product.value = null; // 表示商品不存在或載入失敗
      errorMessage.value = '❌ 無法載入商品資料！';
      return;
    }

    product.value = await res.json();
  } catch (error) {
    console.error(`載入商品 ID ${productId} 資料時發生錯誤：`, error);
    errorMessage.value = '❌ 載入商品資料時發生錯誤！';
    product.value = null; // 表示商品不存在或載入失敗
  }
}

function addItemToCart() {
  errorMessage.value = ''; // 清除之前的訊息
  if (!product.value) return;
  
  // 確保添加到購物車的商品物件包含必要的屬性
  const productToAdd = {
    id: product.value.id,
    name: product.value.name,
    price: product.value.price,
    quantity: quantity.value
  };
  
  cartStore.addItem(productToAdd);
  // 替換 alert 為內部訊息，這裡可以顯示成功訊息
  errorMessage.value = `✅ ${product.value.name} 已加入購物車！`;
}

onMounted(() => {
  loadProductDetail();
  errorMessage.value = ''; // 在組件載入時清除錯誤訊息
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

.container {
    background-color: var(--white); /* 容器背景色 */
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 30px;
}

.product-detail-container {
    align-items: center; /* 讓圖片與右側內容垂直置中 */
}

.product-image {
    border: 1px solid var(--light-grey); /* 圖片邊框 */
    border-radius: 8px; /* 圖片圓角 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* 圖片陰影 */
    max-width: 220px;
    width: 100%;
    height: auto;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

.product-title {
    color: var(--dark-brown); /* 標題顏色 */
    font-weight: bold;
    border-bottom: 2px solid var(--light-brown); /* 底部裝飾線 */
    padding-bottom: 10px;
    margin-bottom: 20px;
    font-size: 1.6rem; /* 原本很大，改小一點 */
}

.product-price {
    color: #d32f2f; /* 金額顏色改為紅色 */
    font-weight: bold;
    margin-bottom: 20px;
    font-size: 1.15rem;
}

.product-description {
    color: var(--disabled-text); /* 描述文字顏色 */
    margin-bottom: 20px;
}

.product-quantity-label {
    color: var(--dark-brown); /* 數量標籤顏色 */
    font-weight: bold;
    margin-right: 10px;
}

.product-quantity-input {
    border-radius: 5px;
    border-color: var(--light-brown); /* 輸入框邊框顏色 */
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    color: var(--dark-brown); /* 輸入框文字顏色 */
}

.product-quantity-input:focus {
    border-color: var(--accent-brown); /* 聚焦時邊框顏色 */
    box-shadow: 0 0 0 0.25rem rgba(161, 138, 123, 0.25); /* 根據 light-brown 調整陰影顏色 */
}

/* 加入購物車按鈕 - 與首頁保持一致 */
.add-to-cart-btn {
   background-color: var(--dark-brown); /* 按鈕背景色 */
   border-color: var(--dark-brown); /* 按鈕邊框顏色 */
   color: var(--white); /* 按鈕文字顏色 */
   border-radius: 5px;
   transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, color 0.15s ease-in-out;
   font-size: 1.25rem; /* 調整字體大小 */
}

.add-to-cart-btn:hover {
    background-color: #2a2523; /* 懸停時深一點的棕色 */
    border-color: #2a2523;
    color: var(--white);
}

/* 載入中和無資料提示文字樣式 */
.text-muted {
  font-style: italic;
  color: #6c757d !important; /* 保持灰色，與棕色調協調 */
}

/* RWD 調整 */
@media (max-width: 768px) {
  .product-detail-container {
    flex-direction: column; /* 小螢幕下堆疊 */
    align-items: center; /* 堆疊時居中對齊 */
  }
  .product-image {
      max-width: 80%; /* 圖片最大寬度 */
      margin-bottom: 20px; /* 添加底部間距 */
  }
  .product-info {
      text-align: center; /* 文字居中 */
  }
  .product-quantity-label {
      display: block; /* 數量標籤佔滿一行 */
      margin-bottom: 5px; /* 添加底部間距 */
  }
  .product-quantity-input {
      width: 100% !important; /* 輸入框佔滿寬度 */
  }
}

</style> 