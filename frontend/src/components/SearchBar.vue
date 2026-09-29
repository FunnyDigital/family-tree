<template>
  <div class="relative">
    <Icon name="search" :size="18" class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-faint" />
    <input
      :value="modelValue"
      type="search"
      :placeholder="placeholder"
      class="field !py-2.5 !pl-10"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </div>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Search…' },
})
defineEmits(['update:modelValue'])
</script>
