<template>
  <div class="d-block d-md-none">
    <div v-for="item in items" :key="item[keyField]" class="admin-card card mb-3 shadow-sm">
      <div class="card-body">
        <div v-for="field in fields" :key="field.key" class="admin-card-field mb-2">
          <span class="admin-card-label">{{ field.label }}：</span>
          <span class="admin-card-value" v-if="field.formatter">{{ field.formatter(item[field.key], item) }}</span>
          <span class="admin-card-value" v-else>{{ item[field.key] }}</span>
        </div>
        <div class="admin-card-actions mt-2">
          <slot name="actions" :item="item"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// props: items (array), fields (array of {key, label, formatter?}), keyField (string)
const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  fields: {
    type: Array,
    required: true
  },
  keyField: {
    type: String,
    required: true
  }
});
</script>

<style scoped>
.admin-card {
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(56,48,46,0.10);
  background: #fff;
  font-size: 0.98rem;
  padding: 10px 12px;
}
.admin-card-field {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  margin-bottom: 6px;
}
.admin-card-label {
  font-weight: bold;
  color: #a18a7b;
  min-width: 80px;
  font-size: 1.01em;
}
.admin-card-value {
  color: #38302e;
  word-break: break-all;
  font-size: 0.98em;
  margin-left: 2px;
}
.admin-card-actions {
  display: flex;
  flex-direction: row;
  gap: 10px;
  margin-top: 8px;
  justify-content: flex-end;
}
.admin-card-actions .btn {
  min-width: 64px;
  font-size: 1rem;
  padding: 6px 0;
  border-radius: 7px;
  white-space: nowrap;
}
@media (max-width: 480px) {
  .admin-card {
    font-size: 0.95rem;
    padding: 8px 6px;
  }
  .admin-card-label {
    min-width: 60px;
    font-size: 0.98em;
  }
  .admin-card-actions .btn {
    min-width: 54px;
    font-size: 0.97rem;
    padding: 5px 0;
  }
}
</style> 