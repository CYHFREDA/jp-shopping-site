<template>
  <div class="d-block d-md-none">
    <div v-for="item in items" :key="item[keyField]" class="card mb-3 shadow-sm">
      <div class="card-body">
        <div v-for="field in fields" :key="field.key" class="mb-2">
          <strong>{{ field.label }}：</strong>
          <span v-if="field.formatter">{{ field.formatter(item[field.key], item) }}</span>
          <span v-else>{{ item[field.key] }}</span>
        </div>
        <slot name="actions" :item="item"></slot>
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
.card {
  font-size: 1rem;
}
</style> 