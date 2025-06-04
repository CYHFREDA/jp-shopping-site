<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-warning border-bottom shadow-sm">
    <div class="container-fluid">
      <router-link class="navbar-brand fw-bold d-flex align-items-center" to="/">
        <img src="/images/LOGO.png" alt="LOGO" class="me-2" />
        <span>Clevora 日本代購</span>
      </router-link>
      <form id="searchForm" class="d-flex ms-auto me-3" @submit.prevent="handleSearch">
        <input 
          id="searchInput" 
          class="form-control form-control-sm me-2" 
          type="search" 
          placeholder="搜尋" 
          v-model="searchQuery"
        />
        <button class="btn btn-outline-dark btn-sm" type="submit"><i class="fas fa-search"></i></button>
      </form>
      <div class="d-flex align-items-center">
        <template v-if="customerStore.isAuthenticated">
          <span class="me-2 text-dark fw-bold">你好, {{ customerStore.customer?.name }}</span>
          <router-link to="/orderHistory" class="me-3 text-dark text-decoration-none">我的訂單</router-link>
          <a href="#" class="me-3 text-dark text-decoration-none" @click.prevent="handleLogout">登出</a>
        </template>
        <template v-else>
          <router-link to="/login" class="me-3 text-dark text-decoration-none">會員登入</router-link>
          <router-link to="/admin/login" class="me-3 text-dark text-decoration-none">管理員登入</router-link>
        </template>
        <router-link to="/cart" class="text-dark text-decoration-none position-relative">
          <i class="fas fa-shopping-cart"></i>
          <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
            {{ cartStore.totalItems }}
          </span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useCustomerStore } from '@/stores/customerStore';
import { useCartStore } from '@/stores/cartStore';
import { useRouter } from 'vue-router';

const customerStore = useCustomerStore();
const cartStore = useCartStore();
const router = useRouter();
const searchQuery = ref('');

function handleLogout() {
  customerStore.logout();
  router.push('/');
}

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/', query: { search: searchQuery.value.trim() } });
  }
}
</script>

<style scoped>
.navbar-brand img {
  height: 40px;
}
</style>
