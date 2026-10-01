<template>
  <div>
    <section class="relative overflow-hidden border-b border-line bg-white">
      <div
        class="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-accent-50 opacity-70 blur-3xl"
      />
      <div class="relative mx-auto max-w-6xl px-4 py-20 sm:px-6 sm:py-28">
        <p class="text-sm font-medium uppercase tracking-widest text-accent-700" v-reveal>Our family</p>
        <h1 class="mt-3 max-w-3xl font-display text-4xl font-semibold leading-[1.05] sm:text-6xl" v-reveal="80">
          {{ site }}
        </h1>
        <p class="mt-5 max-w-2xl text-lg text-ink-muted" v-reveal="160">
          A living record of who we are — every branch, every face, and every story worth keeping.
        </p>
        <div class="mt-8 flex flex-wrap gap-3" v-reveal="240">
          <RouterLink to="/tree" class="btn-primary">
            <Icon name="tree" :size="18" /> Explore the family tree
          </RouterLink>
          <RouterLink to="/people" class="btn-ghost">
            <Icon name="users" :size="18" /> Browse people
          </RouterLink>
        </div>

        <dl class="mt-14 grid max-w-3xl grid-cols-2 gap-8 sm:grid-cols-4" v-reveal="320">
          <div v-for="stat in statCards" :key="stat.label">
            <dd class="font-display text-3xl font-semibold text-ink sm:text-4xl">{{ stat.value }}</dd>
            <dt class="mt-1 text-sm text-ink-muted">{{ stat.label }}</dt>
          </div>
        </dl>
      </div>
    </section>

    <section v-if="featured.length" class="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <div class="mb-6 flex items-end justify-between gap-4">
        <div>
          <h2 class="font-display text-2xl font-semibold sm:text-3xl">Faces in the family</h2>
          <p class="mt-1 text-ink-muted">A few of the people in our tree.</p>
        </div>
        <RouterLink
          to="/people"
          class="hidden shrink-0 items-center gap-1 text-sm font-medium text-accent-700 hover:text-accent-600 sm:inline-flex"
        >
          See all <Icon name="arrowRight" :size="16" />
        </RouterLink>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <PersonCard
          v-for="(person, i) in featured"
          :key="person.id"
          :person="person"
          v-reveal="Math.min(i * 50, 300)"
        />
      </div>
    </section>

    <section class="border-t border-line bg-white">
      <div class="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <div class="grid gap-10 sm:grid-cols-3">
          <div v-for="(feature, i) in features" :key="feature.title" v-reveal="i * 80">
            <span class="flex h-11 w-11 items-center justify-center rounded-full bg-accent-50 text-accent-700">
              <Icon :name="feature.icon" :size="22" />
            </span>
            <h3 class="mt-4 font-display text-xl font-semibold">{{ feature.title }}</h3>
            <p class="mt-1.5 text-sm leading-relaxed text-ink-muted">{{ feature.text }}</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="!loading && !stats.total_people" class="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <EmptyState
        title="Start your family tree"
        message="Sign in as admin to add the first person, then watch the branches grow."
        icon="tree"
      >
        <template #action>
          <RouterLink to="/login" class="btn-primary">Admin sign in</RouterLink>
        </template>
      </EmptyState>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Icon from '../components/Icon.vue'
import PersonCard from '../components/PersonCard.vue'
import EmptyState from '../components/EmptyState.vue'
import { api } from '../services/api'
import { loadSiteTitle } from '../composables/useSite'

const site = ref('Family Tree')
const stats = ref({})
const people = ref([])
const loading = ref(true)

const statCards = computed(() => [
  { label: 'Family members', value: stats.value.total_people ?? 0 },
  { label: 'Generations', value: stats.value.generations ?? 0 },
  { label: 'Marriages', value: stats.value.total_marriages ?? 0 },
  { label: 'Photographs', value: stats.value.total_photos ?? 0 },
])

const featured = computed(() => {
  const withPhotos = people.value.filter((p) => p.photo_url)
  const withoutPhotos = people.value.filter((p) => !p.photo_url)
  return [...withPhotos, ...withoutPhotos].slice(0, 6)
})

const features = [
  {
    icon: 'tree',
    title: 'The whole family tree',
    text: 'Couples, remarriages and every child in one connected view you can pan, zoom and explore.',
  },
  {
    icon: 'image',
    title: 'Photographs that live on',
    text: 'Build an album per person — portraits, moments, and the faces behind the names.',
  },
  {
    icon: 'leaf',
    title: 'Stories and biodata',
    text: 'Record birth, life and places, and write the memories you want future generations to read.',
  },
]

onMounted(async () => {
  site.value = await loadSiteTitle()
  try {
    const [statsData, peopleData] = await Promise.all([
      api.getStats(),
      api.getPersons({ limit: 24 }),
    ])
    stats.value = statsData
    people.value = peopleData.items
  } catch {
    /* leave defaults */
  } finally {
    loading.value = false
  }
})
</script>
