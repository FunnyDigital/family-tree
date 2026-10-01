<template>
  <div class="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-12">
    <div v-if="loading" class="py-20 text-center text-ink-muted">Loading profile…</div>

    <EmptyState
      v-else-if="error"
      title="Profile not found"
      :message="error"
      icon="info"
    >
      <template #action>
        <RouterLink to="/people" class="btn-primary">Back to directory</RouterLink>
      </template>
    </EmptyState>

    <template v-else-if="person">
      <RouterLink to="/people" class="mb-6 inline-flex items-center gap-1.5 text-sm text-ink-muted hover:text-accent-700">
        <Icon name="arrowLeft" :size="16" /> All people
      </RouterLink>

      <header class="card overflow-hidden">
        <div class="flex flex-col gap-6 p-6 sm:flex-row sm:items-center sm:p-8">
          <PersonAvatar :person="person" :size="132" ring class="self-start" />
          <div class="min-w-0">
            <h1 class="font-display text-3xl font-semibold leading-tight sm:text-4xl">
              {{ person.full_name }}
            </h1>
            <p v-if="person.maiden_name" class="mt-1 text-sm italic text-ink-faint">
              née {{ person.maiden_name }}
            </p>
            <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-ink-muted">
              <span v-if="person.life_span" class="inline-flex items-center gap-1.5">
                <Icon name="calendar" :size="15" class="text-accent" /> {{ person.life_span }}
              </span>
              <span v-if="person.occupation" class="inline-flex items-center gap-1.5">
                <Icon name="briefcase" :size="15" class="text-accent" /> {{ person.occupation }}
              </span>
              <span v-if="person.birth_place" class="inline-flex items-center gap-1.5">
                <Icon name="mapPin" :size="15" class="text-accent" /> {{ person.birth_place }}
              </span>
            </div>
            <div class="mt-5 flex flex-wrap gap-2">
              <button class="btn-primary !py-2" @click="toggleTree">
                <Icon name="generations" :size="16" />
                {{ showTree ? 'Hide family tree' : 'Show family tree from here' }}
              </button>
              <RouterLink :to="{ name: 'Tree', query: { focus: person.id } }" class="btn-ghost !py-2">
                <Icon name="tree" :size="16" /> View in full tree
              </RouterLink>
              <RouterLink
                v-if="isAuthed"
                :to="`/admin/people/${person.id}`"
                class="btn-ghost !py-2"
              >
                <Icon name="edit" :size="16" /> Edit profile
              </RouterLink>
            </div>
          </div>
        </div>
      </header>

      <section v-if="showTree" class="mt-8" v-reveal>
        <div class="mb-3 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 class="font-display text-2xl font-semibold">
              Down from {{ person.first_name }}
            </h2>
            <p class="mt-1 text-sm text-ink-muted">
              {{ person.first_name }} and partners, then every descendant beneath them.
            </p>
          </div>
          <span class="text-sm text-ink-faint">
            {{ subtree.persons.length }} {{ subtree.persons.length === 1 ? 'person' : 'people' }}
          </span>
        </div>
        <div class="h-[560px] overflow-hidden rounded-xl2 border border-line bg-canvas shadow-soft">
          <div v-if="treeLoading" class="flex h-full items-center justify-center text-ink-muted">
            Loading family tree…
          </div>
          <div
            v-else-if="subtree.persons.length <= 1"
            class="flex h-full items-center justify-center p-6 text-center text-sm text-ink-muted"
          >
            No descendants recorded for {{ person.first_name }} yet.
          </div>
          <FamilyTree
            v-else
            :persons="subtree.persons"
            :unions="subtree.unions"
            :show-search="false"
          />
        </div>
      </section>

      <div class="mt-8 grid gap-8 lg:grid-cols-[1.5fr_1fr]">
        <div class="space-y-10">
          <section v-if="stories.length || person.bio" v-reveal>
            <h2 class="mb-4 font-display text-2xl font-semibold">Their story</h2>
            <div v-if="person.bio" class="prose-story space-y-4" v-html="formatStory(person.bio)" />
            <StoryList v-if="stories.length" class="mt-6" :stories="stories" />
          </section>

          <section v-reveal="80">
            <h2 class="mb-4 font-display text-2xl font-semibold">Photographs</h2>
            <PhotoGallery v-if="photos.length" :photos="photos" />
            <p v-else class="rounded-xl border border-dashed border-line bg-white/60 px-5 py-8 text-center text-sm text-ink-muted">
              No photographs added yet.
            </p>
          </section>
        </div>

        <aside class="space-y-8">
          <section v-if="hasBiodata" class="card p-6" v-reveal="60">
            <h2 class="mb-4 font-display text-xl font-semibold">Biodata</h2>
            <BiodataTable :person="person" />
          </section>

          <section class="card p-6" v-reveal="120">
            <h2 class="mb-4 font-display text-xl font-semibold">Family</h2>
            <div class="space-y-5 text-sm">
              <div v-if="parents.length">
                <p class="label">Parents</p>
                <div class="flex flex-wrap gap-2">
                  <RelationChip v-for="relative in parents" :key="relative.id" :person="relative" />
                </div>
              </div>

              <div v-if="spouseUnions.length">
                <p class="label">Spouse{{ spouseUnions.length > 1 ? 's' : '' }} & children</p>
                <div v-for="union in spouseUnions" :key="union.partner?.id ?? union.id ?? 'unknown'" class="mb-3 last:mb-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <RelationChip v-if="union.partner" :person="union.partner" />
                    <span class="text-xs text-ink-faint">{{ unionLabel(union) }}</span>
                  </div>
                  <div v-if="union.children.length" class="mt-2 flex flex-wrap gap-2 pl-3">
                    <RelationChip
                      v-for="child in union.children"
                      :key="child.id"
                      :person="child"
                      small
                    />
                  </div>
                </div>
              </div>

              <div v-if="children.length">
                <p class="label">Children</p>
                <div class="flex flex-wrap gap-2">
                  <RelationChip v-for="child in children" :key="child.id" :person="child" small />
                </div>
              </div>

              <div v-if="person.siblings.length">
                <p class="label">Siblings</p>
                <div class="flex flex-wrap gap-2">
                  <RelationChip v-for="sibling in person.siblings" :key="sibling.id" :person="sibling" small />
                </div>
              </div>

              <p v-if="!parents.length && !spouseUnions.length && !children.length && !person.siblings.length" class="text-ink-muted">
                No family connections recorded yet.
              </p>
            </div>
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import PersonAvatar from '../components/PersonAvatar.vue'
import PhotoGallery from '../components/PhotoGallery.vue'
import BiodataTable from '../components/BiodataTable.vue'
import StoryList from '../components/StoryList.vue'
import RelationChip from '../components/RelationChip.vue'
import EmptyState from '../components/EmptyState.vue'
import FamilyTree from '../components/tree/FamilyTree.vue'
import { api } from '../services/api'
import { useAuth } from '../composables/useAuth'
import { descendantSubset } from '../composables/useDescendants'
import { formatStory, yearOf } from '../utils/text'

const route = useRoute()
const { isAuthed } = useAuth()

const person = ref(null)
const loading = ref(true)
const error = ref('')

const showTree = ref(false)
const treeData = ref(null)
const treeLoading = ref(false)

const subtree = computed(() => {
  if (!treeData.value || !person.value) return { persons: [], unions: [] }
  return descendantSubset(person.value.id, treeData.value.persons, treeData.value.unions)
})

async function toggleTree() {
  showTree.value = !showTree.value
  if (!showTree.value || treeData.value) return
  treeLoading.value = true
  try {
    treeData.value = await api.getTree()
  } catch {
    treeData.value = { persons: [], unions: [] }
  } finally {
    treeLoading.value = false
  }
}

const photos = computed(() => person.value?.photos || [])
const stories = computed(() => person.value?.stories || [])
const hasBiodata = computed(() => {
  const p = person.value
  if (!p) return false
  return Boolean(
    p.birth_date || p.death_date || p.birth_place || p.death_place || p.occupation || p.maiden_name,
  )
})

const parents = computed(() => {
  const p = person.value
  return [p?.father, p?.mother].filter(Boolean)
})

const spouseUnions = computed(() => {
  const p = person.value
  if (!p) return []
  return p.unions.map((union) => ({
    ...union,
    partner:
      union.partner_a && union.partner_a.id !== p.id
        ? union.partner_a
        : union.partner_b && union.partner_b.id !== p.id
          ? union.partner_b
          : null,
  }))
})

const children = computed(() => person.value?.children || [])

function unionLabel(union) {
  const start = yearOf(union.start_date)
  const end = yearOf(union.end_date)
  const status = union.status && union.status !== 'married' ? union.status : 'married'
  if (start && end) return `${status} ${start}–${end}`
  if (start) return `${status} since ${start}`
  return status
}

async function load() {
  loading.value = true
  error.value = ''
  person.value = null
  showTree.value = false
  try {
    person.value = await api.getPerson(route.params.id)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.params.id, load)
</script>
