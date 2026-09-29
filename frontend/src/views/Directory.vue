<template>
  <div class="mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-14">
    <header class="mb-8" v-reveal>
      <p class="text-sm font-medium uppercase tracking-widest text-accent-700">Directory</p>
      <h1 class="mt-1 font-display text-3xl font-semibold sm:text-4xl">Everyone in the family</h1>
      <p class="mt-2 max-w-2xl text-ink-muted">
        Browse every person we've recorded. Open a profile for photographs, biodata and their story.
      </p>
    </header>

    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center" v-reveal="60">
      <div class="w-full sm:max-w-sm">
        <SearchBar v-model="query" placeholder="Search by name, place or occupation…" />
      </div>
      <div class="flex items-center gap-2">
        <button
          v-for="option in filters"
          :key="option.value"
          class="chip"
          :class="{ '!border-accent !text-accent-700': status === option.value }"
          @click="status = option.value"
        >
          {{ option.label }}
        </button>
      </div>
      <span class="text-sm text-ink-faint sm:ml-auto">{{ total }} {{ total === 1 ? 'person' : 'people' }}</span>
    </div>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="n in 6" :key="n" class="card h-24 animate-pulse bg-white/60" />
    </div>

    <EmptyState
      v-else-if="!people.length"
      :title="query ? 'No matches' : 'No people yet'"
      :message="query ? 'Try a different name or place.' : 'Add family members from the admin panel to see them here.'"
      icon="search"
    />

    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <PersonCard
        v-for="(person, i) in people"
        :key="person.id"
        :person="person"
        v-reveal="Math.min(i * 40, 320)"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import PersonCard from '../components/PersonCard.vue'
import SearchBar from '../components/SearchBar.vue'
import EmptyState from '../components/EmptyState.vue'
import { api } from '../services/api'

const people = ref([])
const total = ref(0)
const query = ref('')
const status = ref('all')
const loading = ref(true)
let timer = null

const filters = [
  { label: 'Everyone', value: 'all' },
  { label: 'Living', value: 'living' },
  { label: 'Remembered', value: 'deceased' },
]

async function load() {
  loading.value = true
  try {
    const params = { q: query.value || undefined }
    if (status.value === 'living') params.is_living = true
    if (status.value === 'deceased') params.is_living = false
    const data = await api.getPersons(params)
    people.value = data.items
    total.value = data.total
  } catch {
    people.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

watch(query, () => {
  clearTimeout(timer)
  timer = setTimeout(load, 250)
})
watch(status, load)

onMounted(load)
</script>
