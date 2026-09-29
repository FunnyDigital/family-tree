<template>
  <div class="mx-auto flex max-w-2xl flex-col items-center px-4 py-24 text-center">
    <span class="flex h-16 w-16 items-center justify-center rounded-full bg-accent-50 text-accent-700">
      <Icon name="tree" :size="30" />
    </span>
    <h1 class="mt-5 font-display text-4xl font-semibold">Page not found</h1>
    <p class="mt-2 text-ink-muted">That branch doesn't lead anywhere.</p>
    <RouterLink to="/" class="btn-primary mt-6">Back home</RouterLink>
  </div>
</template>

<script setup>
import Icon from '../components/Icon.vue'
</script>
