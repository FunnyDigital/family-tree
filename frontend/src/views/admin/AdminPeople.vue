<template>
  <div>
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl font-semibold">People</h1>
        <p class="mt-1 text-ink-muted">{{ total }} recorded in the family tree.</p>
      </div>
      <RouterLink to="/admin/people/new" class="btn-primary">
        <Icon name="userPlus" :size="18" /> Add a person
      </RouterLink>
    </div>

    <div class="mb-6 max-w-sm">
      <SearchBar v-model="query" placeholder="Search people…" />
    </div>

    <div v-if="loading" class="card divide-y divide-line">
      <div v-for="n in 5" :key="n" class="h-16 animate-pulse bg-white/60" />
    </div>

    <EmptyState
      v-else-if="!people.length"
      :title="query ? 'No matches' : 'No people yet'"
      :message="query ? 'Try another search.' : 'Add your first family member to get started.'"
      icon="users"
    >
      <template #action>
        <RouterLink to="/admin/people/new" class="btn-primary">Add a person</RouterLink>
      </template>
    </EmptyState>

    <div v-else class="card divide-y divide-line">
      <div
        v-for="person in people"
        :key="person.id"
        class="flex items-center gap-4 p-4"
      >
        <PersonAvatar :person="person" :size="44" />
        <div class="min-w-0 flex-1">
          <p class="truncate font-medium">{{ person.full_name }}</p>
          <p class="truncate text-sm text-ink-muted">
            {{ [person.life_span, person.occupation].filter(Boolean).join(' · ') || '—' }}
          </p>
        </div>
        <RouterLink :to="`/admin/people/${person.id}`" class="btn-ghost !px-3.5 !py-2">
          <Icon name="edit" :size="16" /> Edit
        </RouterLink>
        <button class="rounded-full p-2 text-ink-faint hover:text-red-600" title="Delete" @click="confirmDelete(person)">
          <Icon name="trash" :size="17" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import Icon from '../../components/Icon.vue'
import PersonAvatar from '../../components/PersonAvatar.vue'
import SearchBar from '../../components/SearchBar.vue'
import EmptyState from '../../components/EmptyState.vue'
import { api } from '../../services/api'

const people = ref([])
const total = ref(0)
const query = ref('')
const loading = ref(true)
let timer = null

async function load() {
  loading.value = true
  try {
    const data = await api.getPersons({ q: query.value || undefined })
    people.value = data.items
    total.value = data.total
  } catch {
    people.value = []
  } finally {
    loading.value = false
  }
}

async function confirmDelete(person) {
  const ok = window.confirm(
    `Delete ${person.full_name}? This also removes their photographs, stories and marriage records.`,
  )
  if (!ok) return
  try {
    await api.deletePerson(person.id)
    await load()
  } catch (e) {
    window.alert(e.message)
  }
}

watch(query, () => {
  clearTimeout(timer)
  timer = setTimeout(load, 250)
})

onMounted(load)
</script>
