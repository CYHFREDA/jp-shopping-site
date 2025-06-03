import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCartStore = defineStore('cart', () => {
  // 從 localStorage 載入初始狀態
  const items = ref([]);

  const totalItems = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0);
  });

  const totalAmount = computed(() => {
    return items.value.reduce((total, item) => total + (item.price * item.quantity), 0);
  });

  function loadCart() {
    const storedCart = localStorage.getItem('cart');
    if (storedCart) {
      items.value = JSON.parse(storedCart);
    }
  }

  function addItem(product) {
    const existingItemIndex = items.value.findIndex(item => item.id === product.id);
    if (existingItemIndex > -1) {
      // 使用 splice 替換元素，更明確地觸發響應式更新
      const updatedItem = { ...items.value[existingItemIndex] };
      updatedItem.quantity++;
      items.value.splice(existingItemIndex, 1, updatedItem);
    } else {
      items.value.push({
        id: product.id,
        name: product.name,
        price: product.price,
        quantity: 1
      });
    }
    saveCart(); // 保存到 localStorage
  }

  function removeItem(productId) {
    const index = items.value.findIndex(item => item.id === productId);
    if (index > -1) {
      items.value.splice(index, 1);
      saveCart(); // 保存到 localStorage
    }
  }

  function updateQuantity(productId, quantity) {
    const item = items.value.find(item => item.id === productId);
    if (item) {
      item.quantity = quantity;
      saveCart(); // 保存到 localStorage
    }
  }

  function clearCart() {
    items.value = [];
    saveCart(); // 保存到 localStorage
  }

  // Helper function to save cart to localStorage
  function saveCart() {
    localStorage.setItem('cart', JSON.stringify(items.value));
  }

  return {
    items,
    totalItems,
    totalAmount,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    loadCart
  };
});
