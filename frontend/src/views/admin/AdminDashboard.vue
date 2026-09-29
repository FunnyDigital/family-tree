<template>
  <div>
    <div class="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="font-display text-3xl font-semibold">Dashboard</h1>
        <p class="mt-1 text-ink-muted">An overview of everything recorded in the family tree.</p>
      </div>
      <RouterLink to="/admin/people/new" class="btn-primary">
        <Icon name="userPlus" :size="18" /> Add a person
      </RouterLink>
    </div>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div v-for="n in 4" :key="n" class="card h-24 animate-pulse bg-white/60" />
    </div>

    <template v-else>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="card in cards" :key="card.label" class="card flex items-center gap-4 p-5">
          <span class="flex h-11 w-11 items-center justify-center rounded-full bg-accent-50 text-accent-700">
            <Icon :name="card.icon" :size="22" />
          </span>
          <div>
            <p class="font-display text-2xl font-semibold">{{ card.value }}</p>
            <p class="text-sm text-ink-muted">{{ card.label }}</p>
          </div>
        </div>
      </div>

      <section class="mt-10">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="font-display text-xl font-semibold">Recently added</h2>
          <RouterLink to="/admin/people" class="text-sm font-medium text-accent-700 hover:text-accent-600">
            Manage all people
          </RouterLink>
        </div>
        <div v-if="recent.length" class="card divide-y divide-line">
          <RouterLink
            v-for="person in recent"
            :key="person.id"
            :to="`/admin/people/${person.id}`"
            class="flex items-center gap-4 p-4 transition-colors hover:bg-accent-50/50"
          >
            <PersonAvatar :person="person" :size="44" />
            <div class="min-w-0">
              <p class="truncate font-medium">{{ person.full_name }}</p>
              <p class="truncate text-sm text-ink-muted">{{ person.life_span || '—' }}</p>
            </div>
            <Icon name="arrowRight" :size="18" class="ml-auto text-ink-faint" />
          </RouterLink>
        </div>
        <EmptyState
          v-else
          title="No people yet"
          message="Add the first member of your family tree."
          icon="userPlus"
        >
          <template #action>
            <RouterLink to="/admin/people/new" class="btn-primary">Add a person</RouterLink>
          </template>
        </EmptyState>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Icon from '../../components/Icon.vue'
import PersonAvatar from '../../components/PersonAvatar.vue'
import EmptyState from '../../components/EmptyState.vue'
import { api } from '../../services/api'

const stats = ref({})
const recent = ref([])
const loading = ref(true)

const cards = computed(() => [
  { label: 'People', value: stats.value.total_people ?? 0, icon: 'users' },
  { label: 'Generations', value: stats.value.generations ?? 0, icon: 'generations' },
  { label: 'Photographs', value: stats.value.total_photos ?? 0, icon: 'image' },
  { label: 'Stories', value: stats.value.total_stories ?? 0, icon: 'leaf' },
])

onMounted(async () => {
  try {
    const [statsData, peopleData] = await Promise.all([api.getStats(), api.getPersons({ limit: 6 })])
    stats.value = statsData
    recent.value = peopleData.items
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
})
</script>
