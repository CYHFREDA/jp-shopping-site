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
    <div v-if="loading" class="text-center text-muted my-3">
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <span class="ms-2">載入門市資料中...</span>
    </div>
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    <ul v-else-if="filteredStores.length" class="list-group mb-2" style="max-height: 300px; overflow-y: auto;">
      <li
        v-for="store in filteredStores"
        :key="store.cvs + '-' + store.id"
        class="list-group-item list-group-item-action"
        @click="selectStore(store)"
        style="cursor: pointer;"
      >
        <span class="badge bg-primary me-2">{{ store.cvs }}</span>
        <strong>{{ store.store }}</strong>
        <small class="text-muted">（{{ store.address }}）</small>
      </li>
    </ul>
    <div v-else-if="keyword || selectedCvs" class="text-muted text-center my-2">
      找不到符合條件的門市
    </div>
    <div v-if="selectedStore" class="alert alert-success p-2">
      已選擇：<span class="badge bg-primary me-2">{{ selectedStore.cvs }}</span>
      <strong>{{ selectedStore.store }}</strong>（{{ selectedStore.address }}）
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const stores = ref([])
const filteredStores = ref([])
const keyword = ref('')
const selectedStore = ref(null)
const selectedCvs = ref('')
const cvsTypes = ref(["7-11", "全家", "萊爾富", "OK超商"])
const loading = ref(false)
const error = ref('')

const emit = defineEmits(['select'])

// 接收外部傳入的已選擇門市
const props = defineProps({
  selectedStore: {
    type: Object,
    default: null
  }
})

// 監聽外部傳入的已選擇門市
watch(() => props.selectedStore, (newStore) => {
  if (newStore) {
    selectedStore.value = newStore
    keyword.value = newStore.name
  } else {
    selectedStore.value = null
    keyword.value = ''
  }
}, { immediate: true })

onMounted(async () => {
  try {
    loading.value = true
    error.value = ''
    const res = await fetch('/all_cvs_stores.json')
    if (!res.ok) {
      throw new Error('載入門市資料失敗')
    }
    stores.value = await res.json()
    searchStore()  // 初始化搜尋結果
  } catch (e) {
    console.error('載入門市資料錯誤：', e)
    error.value = '載入門市資料失敗，請重新整理頁面試試'
  } finally {
    loading.value = false
  }
})

function searchStore() {
  let result = stores.value
  
  // 根據選擇的超商類型過濾
  if (selectedCvs.value) {
    result = result.filter(s => s.cvs === selectedCvs.value)
  }
  
  // 根據關鍵字過濾（店名或地址）
  if (keyword.value) {
    const kw = keyword.value.trim().toLowerCase()
    result = result.filter(s =>
      s.store.toLowerCase().includes(kw) || 
      s.address.toLowerCase().includes(kw)
    )
  }
  
  // 最多顯示 30 筆結果
  filteredStores.value = result.slice(0, 30)
}

// 超商類型代碼轉換
const cvsTypeMapping = {
  '7-11': 'UNIMART',
  '全家': 'FAMI',
  '萊爾富': 'HILIFE',
  'OK超商': 'OKMART'
}

function selectStore(store) {
  selectedStore.value = store
  keyword.value = store.store
  filteredStores.value = []
  
  emit('select', {
    id: store.id,
    name: store.store,
    type: cvsTypeMapping[store.cvs] || store.cvs
  })
}
</script>

<style scoped>
.list-group-item:hover {
  background: #f5f5f5;
}
.badge.bg-primary {
  background-color: #007bff !important;
}
.text-muted {
  color: #6c757d !important;
}
</style> 