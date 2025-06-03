<template>
  <div class="container my-5">
    <div v-if="product" class="row">
      <div class="col-md-6">
        <img :src="product.image_url || 'https://via.placeholder.com/400'" :alt="product.name" class="img-fluid rounded">
      </div>
      <div class="col-md-6">
        <h1 class="mb-3">{{ product.name }}</h1>
        <p class="fs-4 text-danger">NT$ {{ product.price }}</p>
        <p>{{ product.description || '無商品描述' }}</p>
        
        <div class="mb-3">
          <label for="quantity" class="form-label">數量：</label>
          <input type="number" id="quantity" v-model.number="quantity" min="1" class="form-control w-auto">
        </div>
        
        <button class="btn btn-success btn-lg" @click="addItemToCart">
          <i class="fas fa-shopping-cart"></i> 加入購物車
        </button>
      </div>
    </div>
    <div v-else class="text-center">
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

async function loadProductDetail() {
  const productId = route.params.id;
  if (!productId) {
    console.error('商品 ID 未提供！');
    return;
  }
  
  try {
    // 假設後端 API 有 /products/:id 的端點來獲取單一商品資料
    const res = await fetch(`/products/${productId}`);

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`無法載入商品 ID ${productId} 的資料：`, res.status, errorText);
      product.value = null; // 表示商品不存在或載入失敗
      alert('無法載入商品資料！');
      return;
    }

    product.value = await res.json();
  } catch (error) {
    console.error(`載入商品 ID ${productId} 資料時發生錯誤：`, error);
    alert('載入商品資料時發生錯誤！');
    product.value = null; // 表示商品不存在或載入失敗
  }
}

function addItemToCart() {
  if (!product.value) return;
  
  // 確保添加到購物車的商品物件包含必要的屬性
  const productToAdd = {
    id: product.value.id,
    name: product.value.name,
    price: product.value.price,
    quantity: quantity.value
  };
  
  cartStore.addItem(productToAdd);
  alert(`${product.value.name} 已加入購物車！`);
}

onMounted(() => {
  loadProductDetail();
});
</script>

<style scoped>
/* 可以添加一些 ProductDetail.vue 特有的樣式 */
.form-control.w-auto {
  width: auto;
  display: inline-block;
}
</style> 