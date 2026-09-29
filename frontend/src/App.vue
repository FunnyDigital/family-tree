<template>
  <div class="flex min-h-screen flex-col bg-canvas">
    <AppHeader v-if="!route.meta.bare" />
    <main class="flex-1">
      <RouterView />
    </main>
    <AppFooter v-if="!route.meta.bare && !route.meta.hideFooter" />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'

const route = useRoute()
</script>
