<template>
  <div class="flex flex-col items-center justify-center rounded-xl2 border border-dashed border-line bg-white/60 px-6 py-16 text-center">
    <span class="flex h-14 w-14 items-center justify-center rounded-full bg-accent-50 text-accent-700">
      <Icon :name="icon" :size="26" />
    </span>
    <h3 class="mt-4 font-display text-xl font-semibold text-ink">{{ title }}</h3>
    <p v-if="message" class="mt-1.5 max-w-md text-sm text-ink-muted">{{ message }}</p>
    <div v-if="$slots.action" class="mt-5">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  title: { type: String, required: true },
  message: { type: String, default: '' },
  icon: { type: String, default: 'users' },
})
</script>
