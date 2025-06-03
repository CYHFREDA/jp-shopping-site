<template>
  <div>
    <div class="mb-3">
      <input v-model="searchQuery" placeholder="請輸入搜尋關鍵字" class="form-control" />
      <button @click="searchProducts" class="btn btn-primary mt-2">搜尋</button>
    </div>

    <div v-if="products.length">
      <div v-for="product in products" :key="product.id" class="product-list-item shadow-sm rounded mb-3 p-3 bg-white">
        <div class="d-flex flex-column flex-md-row">
          <img :src="product.image_url || 'https://via.placeholder.com/150'" :alt="product.name" class="me-3 mb-3 mb-md-0" style="width:150px; height:auto;">
          <div class="flex-grow-1">
            <h5>{{ product.name }}</h5>
            <p>{{ product.description }}</p>
            <div class="d-flex justify-content-between align-items-center">
              <div class="fw-bold text-success">NT$ {{ product.price }}</div>
              <button class="btn btn-success btn-sm" @click="addToCart(product)">加入購物車</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <p v-else class="text-center text-muted">找不到符合條件的商品</p>
  </div>
</template>

<script>
import axios from 'axios';
import { useCartStore } from '@/stores/cartStore';

export default {
  data() {
    return {
      searchQuery: '', // 使用者輸入的關鍵字
      products: []     // 搜尋結果
    };
  },
  methods: {
    searchProducts() {
      if (!this.searchQuery.trim()) {
        alert('請輸入關鍵字');
        return;
      }
      axios.get(`/api/products?query=${encodeURIComponent(this.searchQuery)}`)
        .then(res => {
          this.products = res.data;
        })
        .catch(err => {
          console.error('搜尋失敗', err);
        });
    },
    addToCart(product) {
      const cartStore = useCartStore();
      cartStore.addToCart(product);
      alert('✅ 已加入購物車！');
    }
  }
};
</script>