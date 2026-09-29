<template>
  <header class="sticky top-0 z-40 border-b border-line bg-canvas/85 backdrop-blur">
    <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
      <RouterLink to="/" class="flex items-center gap-2.5 text-ink">
        <span class="flex h-9 w-9 items-center justify-center rounded-full bg-accent-50 text-accent-700">
          <Icon name="tree" :size="20" />
        </span>
        <span class="font-display text-lg font-semibold tracking-tight">{{ site.value }}</span>
      </RouterLink>

      <nav class="hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="link in links"
          :key="link.name"
          :to="link.to"
          class="rounded-full px-3.5 py-2 text-sm font-medium text-ink-soft transition-colors hover:bg-accent-50 hover:text-accent-700"
          :class="{ 'text-accent-700': isActive(link) }"
        >
          {{ link.label }}
        </RouterLink>
        <div class="mx-2 h-5 w-px bg-line" />
        <template v-if="isAuthed">
          <RouterLink to="/admin" class="btn-ghost !px-4 !py-2">
            <Icon name="edit" :size="16" /> Admin
          </RouterLink>
          <button class="ml-1 rounded-full p-2 text-ink-muted hover:text-ink" title="Log out" @click="onLogout">
            <Icon name="logout" :size="18" />
          </button>
        </template>
        <RouterLink v-else to="/login" class="btn-ghost !px-4 !py-2">
          <Icon name="login" :size="16" /> Admin
        </RouterLink>
      </nav>

      <button class="rounded-lg p-2 text-ink-soft md:hidden" @click="open = !open" aria-label="Menu">
        <Icon :name="open ? 'close' : 'chevronDown'" :size="22" />
      </button>
    </div>

    <div v-if="open" class="border-t border-line bg-canvas px-4 py-3 md:hidden">
      <RouterLink
        v-for="link in links"
        :key="link.name"
        :to="link.to"
        class="block rounded-lg px-3 py-2.5 text-sm font-medium text-ink-soft hover:bg-accent-50"
        @click="open = false"
      >
        {{ link.label }}
      </RouterLink>
      <RouterLink
        v-if="!isAuthed"
        to="/login"
        class="mt-1 block rounded-lg px-3 py-2.5 text-sm font-medium text-accent-700 hover:bg-accent-50"
        @click="open = false"
      >
        Admin login
      </RouterLink>
      <template v-else>
        <RouterLink
          to="/admin"
          class="mt-1 block rounded-lg px-3 py-2.5 text-sm font-medium text-accent-700 hover:bg-accent-50"
          @click="open = false"
        >
          Admin panel
        </RouterLink>
        <button class="block w-full rounded-lg px-3 py-2.5 text-left text-sm font-medium text-ink-soft hover:bg-accent-50" @click="onLogout">
          Log out
        </button>
      </template>
    </div>
  </header>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from './Icon.vue'
import { useAuth } from '../composables/useAuth'
import { loadSiteTitle } from '../composables/useSite'

const route = useRoute()
const router = useRouter()
const { isAuthed, logout } = useAuth()

const open = ref(false)
const site = ref('Family Tree')

const links = [
  { name: 'Home', label: 'Home', to: '/' },
  { name: 'Tree', label: 'Family Tree', to: '/tree' },
  { name: 'Directory', label: 'People', to: '/people' },
]

function isActive(link) {
  return route.name === link.name || (link.name === 'Directory' && route.name === 'Person')
}

function onLogout() {
  logout()
  open.value = false
  router.push('/')
}

onMounted(async () => {
  site.value = await loadSiteTitle()
})
</script>
