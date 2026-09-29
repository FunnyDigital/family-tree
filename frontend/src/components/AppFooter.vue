<template>
  <footer class="border-t border-line bg-white">
    <div class="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between">
      <div class="flex items-center gap-2.5">
        <span class="flex h-8 w-8 items-center justify-center rounded-full bg-accent-50 text-accent-700">
          <Icon name="tree" :size="18" />
        </span>
        <div>
          <p class="font-display text-base font-semibold">{{ site }}</p>
          <p class="text-xs text-ink-faint">Keeping our history in one place.</p>
        </div>
      </div>

      <nav class="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-ink-muted">
        <RouterLink to="/" class="hover:text-accent-700">Home</RouterLink>
        <RouterLink to="/tree" class="hover:text-accent-700">Family Tree</RouterLink>
        <RouterLink to="/people" class="hover:text-accent-700">People</RouterLink>
        <RouterLink to="/login" class="hover:text-accent-700">Admin</RouterLink>
      </nav>
    </div>
    <div class="border-t border-line">
      <div class="mx-auto max-w-6xl px-4 py-4 text-xs text-ink-faint sm:px-6">
        {{ site }} · {{ year }}
      </div>
    </div>
  </footer>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Icon from './Icon.vue'
import { loadSiteTitle } from '../composables/useSite'

const site = ref('Family Tree')
const year = new Date().getFullYear()

onMounted(async () => {
  site.value = await loadSiteTitle()
})
</script>
