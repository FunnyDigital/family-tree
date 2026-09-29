<template>
  <div class="min-h-screen bg-canvas">
    <header class="sticky top-0 z-40 border-b border-line bg-white/90 backdrop-blur">
      <div class="mx-auto flex h-16 max-w-6xl items-center justify-between gap-3 px-4 sm:px-6">
        <RouterLink to="/admin" class="flex min-w-0 items-center gap-2.5">
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent-50 text-accent-700">
            <Icon name="tree" :size="20" />
          </span>
          <span class="truncate font-display text-lg font-semibold">
            {{ site }} <span class="font-sans text-xs font-medium uppercase tracking-wide text-ink-faint">Admin</span>
          </span>
        </RouterLink>

        <nav class="flex items-center gap-1">
          <RouterLink
            v-for="link in links"
            :key="link.name"
            :to="link.to"
            class="hidden rounded-full px-3.5 py-2 text-sm font-medium transition-colors sm:block"
            :class="isActive(link) ? 'bg-accent-50 text-accent-700' : 'text-ink-soft hover:bg-accent-50 hover:text-accent-700'"
          >
            {{ link.label }}
          </RouterLink>
          <div class="mx-1 hidden h-5 w-px bg-line sm:block" />
          <RouterLink to="/" class="btn-ghost !px-3.5 !py-2">
            <Icon name="arrowRight" :size="16" /> <span class="hidden sm:inline">View site</span>
          </RouterLink>
          <button class="rounded-full p-2 text-ink-muted hover:text-ink" title="Log out" @click="onLogout">
            <Icon name="logout" :size="18" />
          </button>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../../components/Icon.vue'
import { useAuth } from '../../composables/useAuth'
import { loadSiteTitle } from '../../composables/useSite'

const route = useRoute()
const router = useRouter()
const { logout } = useAuth()

const site = ref('Family Tree')
const links = [
  { name: 'AdminDashboard', label: 'Dashboard', to: '/admin' },
  { name: 'AdminPeople', label: 'People', to: '/admin/people' },
]

function isActive(link) {
  return route.name === link.name || (link.name === 'AdminPeople' && route.name === 'AdminPersonEdit')
}

function onLogout() {
  logout()
  router.push('/')
}

onMounted(async () => {
  site.value = await loadSiteTitle()
})
</script>
