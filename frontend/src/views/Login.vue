<template>
  <div class="flex min-h-screen items-center justify-center bg-canvas px-4">
    <div class="w-full max-w-sm">
      <RouterLink to="/" class="mb-8 flex items-center justify-center gap-2.5">
        <span class="flex h-10 w-10 items-center justify-center rounded-full bg-accent-50 text-accent-700">
          <Icon name="tree" :size="22" />
        </span>
        <span class="font-display text-xl font-semibold">{{ site }}</span>
      </RouterLink>

      <div class="card p-8">
        <h1 class="font-display text-2xl font-semibold">Admin sign in</h1>
        <p class="mt-1 text-sm text-ink-muted">Manage people, photographs and stories.</p>

        <form class="mt-6 space-y-4" @submit.prevent="onSubmit">
          <div>
            <label class="label" for="username">Username</label>
            <input id="username" v-model="username" type="text" required class="field" autocomplete="username" />
          </div>
          <div>
            <label class="label" for="password">Password</label>
            <input id="password" v-model="password" type="password" required class="field" autocomplete="current-password" />
          </div>
          <button type="submit" class="btn-primary w-full" :disabled="loading">
            {{ loading ? 'Signing in…' : 'Sign in' }}
          </button>
          <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{{ error }}</p>
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-ink-faint">
        <RouterLink to="/" class="hover:text-accent-700">← Back to the family tree</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import { useAuth } from '../composables/useAuth'
import { loadSiteTitle } from '../composables/useSite'

const route = useRoute()
const router = useRouter()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const site = ref('Family Tree')

async function onSubmit() {
  loading.value = true
  error.value = ''
  try {
    await login(username.value, password.value)
    router.push(route.query.redirect || { name: 'AdminDashboard' })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  site.value = await loadSiteTitle()
})
</script>
