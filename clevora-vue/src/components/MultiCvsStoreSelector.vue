<template>
  <div>
    <div class="mb-2">
      <label class="me-2">選擇超商：</label>
      <select v-model="selectedCvs" class="form-select d-inline-block w-auto" @change="searchStore">
        <option value="">全部</option>
        <option v-for="cvs in cvsTypes" :key="cvs" :value="cvs">{{ cvs }}</option>
      </select>
    </div>
    <input
      v-model="keyword"
      @input="searchStore"
      placeholder="輸入門市名稱或地址"
      class="form-control mb-2"
    />
    <ul v-if="filteredStores.length" class="list-group mb-2" style="max-height: 300px; overflow-y: auto;">
      <li
        v-for="store in filteredStores"
        :key="store.cvs + '-' + store.id"
        class="list-group-item list-group-item-action"
        @click="selectStore(store)"
        style="cursor: pointer;"
      >
        <span class="badge bg-primary me-2">{{ store.cvs }}</span>
        <strong>{{ store.store }}</strong>（{{ store.address }}）
      </li>
    </ul>
    <div v-if="selectedStore" class="alert alert-success p-2">
      已選擇：<span class="badge bg-primary me-2">{{ selectedStore.cvs }}</span>
      <strong>{{ selectedStore.store }}</strong>（{{ selectedStore.address }}）
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const stores = ref([])
const filteredStores = ref([])
const keyword = ref('')
const selectedStore = ref(null)
const selectedCvs = ref('')
const cvsTypes = ref(["7-11", "全家", "萊爾富", "OK超商"])

onMounted(async () => {
  const res = await fetch('/all_cvs_stores.json')
  stores.value = await res.json()
})

function searchStore() {
  let result = stores.value
  if (selectedCvs.value) {
    result = result.filter(s => s.cvs === selectedCvs.value)
  }
  if (keyword.value) {
    const kw = keyword.value.trim()
    result = result.filter(s =>
      s.store.includes(kw) || s.address.includes(kw)
    )
  }
  filteredStores.value = result.slice(0, 30) // 最多顯示 30 筆
}

function selectStore(store) {
  selectedStore.value = store
  keyword.value = store.store
  filteredStores.value = []
  // emit event 給父元件
  // emit('select', store)
}
</script>

<style scoped>
.list-group-item:hover {
  background: #f5f5f5;
}
.badge.bg-primary {
  background-color: #007bff !important;
}
</style> 