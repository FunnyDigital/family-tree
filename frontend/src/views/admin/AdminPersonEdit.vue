<template>
  <div>
    <RouterLink to="/admin/people" class="mb-6 inline-flex items-center gap-1.5 text-sm text-ink-muted hover:text-accent-700">
      <Icon name="arrowLeft" :size="16" /> All people
    </RouterLink>

    <div v-if="loading" class="py-16 text-center text-ink-muted">Loading…</div>

    <template v-else>
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <PersonAvatar v-if="!isNew" :person="person" :size="64" ring />
        <div class="min-w-0">
          <h1 class="font-display text-3xl font-semibold">
            {{ isNew ? 'Add a person' : person.full_name }}
          </h1>
          <p class="mt-0.5 text-ink-muted">
            {{ isNew ? 'Record a new family member.' : person.life_span || 'Edit their details below.' }}
          </p>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <RouterLink v-if="!isNew" :to="`/person/${person.id}`" class="btn-ghost !py-2">
            <Icon name="user" :size="16" /> View profile
          </RouterLink>
          <button v-if="!isNew" class="btn-danger !py-2" @click="removePerson">
            <Icon name="trash" :size="16" /> Delete
          </button>
        </div>
      </div>

      <PersonForm
        v-model="form"
        :people="people"
        :exclude-id="person?.id ?? null"
        :saving="saving"
        :error="formError"
        @submit="savePerson"
      />

      <template v-if="!isNew">
        <section class="mt-10">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="font-display text-xl font-semibold">Marriages & partnerships</h2>
            <button v-if="!addingUnion" class="btn-ghost !py-2" @click="addingUnion = true">
              <Icon name="plus" :size="16" /> Add union
            </button>
          </div>

          <div v-if="addingUnion" class="mb-4">
            <UnionForm :person-id="person.id" :people="people" @saved="onUnionChanged" @cancel="addingUnion = false" />
          </div>

          <div v-if="person.unions.length" class="space-y-3">
            <div v-for="union in person.unions" :key="unionKey(union)" class="card p-4">
              <template v-if="union.id != null && editingUnionId === union.id">
                <UnionForm
                  :person-id="person.id"
                  :people="people"
                  :union="union"
                  @saved="onUnionChanged"
                  @cancel="editingUnionId = null"
                  @delete="removeUnion"
                />
              </template>
              <template v-else>
                <div class="flex flex-wrap items-center gap-3">
                  <RelationChip :person="partnerOf(union)" />
                  <span class="text-sm text-ink-muted">{{ unionSummary(union) }}</span>
                  <span v-if="union.children.length" class="text-sm text-ink-faint">
                    · {{ union.children.length }} child{{ union.children.length > 1 ? 'ren' : '' }}
                  </span>
                  <div class="ml-auto flex gap-1">
                    <button
                      v-if="union.derived"
                      class="rounded-full px-3 py-1.5 text-xs font-medium text-accent-700 hover:bg-accent-50"
                      title="Record this marriage so you can add a date or status"
                      @click="recordMarriage(union)"
                    >
                      Add details
                    </button>
                    <button v-else class="rounded-full p-1.5 text-ink-faint hover:text-accent-700" title="Edit" @click="editingUnionId = union.id">
                      <Icon name="edit" :size="16" />
                    </button>
                    <button v-if="!union.derived" class="rounded-full p-1.5 text-ink-faint hover:text-red-600" title="Remove" @click="removeUnion(union)">
                      <Icon name="trash" :size="16" />
                    </button>
                  </div>
                </div>
                <div v-if="union.children.length" class="mt-2 flex flex-wrap gap-2 pl-2">
                  <RelationChip v-for="child in union.children" :key="child.id" :person="child" small />
                </div>
              </template>
            </div>
          </div>
          <p v-else-if="!addingUnion" class="text-sm text-ink-muted">
            No marriages or partnerships recorded.
          </p>
        </section>

        <section class="mt-10">
          <h2 class="mb-4 font-display text-xl font-semibold">Photographs</h2>
          <PhotoUploader
            :person-id="person.id"
            :photos="person.photos"
            @changed="reload"
            @primary="setPrimary"
            @remove="deletePhoto"
            @caption="updateCaption"
          />
        </section>

        <section class="mt-10">
          <h2 class="mb-4 font-display text-xl font-semibold">Stories & write-ups</h2>
          <StoryEditor :person-id="person.id" :stories="person.stories" @changed="reload" @delete="deleteStory" />
        </section>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../../components/Icon.vue'
import PersonAvatar from '../../components/PersonAvatar.vue'
import RelationChip from '../../components/RelationChip.vue'
import PersonForm from '../../components/admin/PersonForm.vue'
import UnionForm from '../../components/admin/UnionForm.vue'
import PhotoUploader from '../../components/admin/PhotoUploader.vue'
import StoryEditor from '../../components/admin/StoryEditor.vue'
import { api } from '../../services/api'
import { yearOf } from '../../utils/text'

const route = useRoute()
const router = useRouter()

const person = ref(null)
const people = ref([])
const loading = ref(true)
const saving = ref(false)
const formError = ref('')
const addingUnion = ref(false)
const editingUnionId = ref(null)

const isNew = computed(() => route.params.id === 'new')

const blankForm = () => ({
  first_name: '',
  last_name: '',
  maiden_name: '',
  gender: null,
  birth_date: '',
  death_date: '',
  birth_place: '',
  death_place: '',
  occupation: '',
  bio: '',
  is_living: true,
  father_id: null,
  mother_id: null,
})

const form = reactive(blankForm())

function fillForm(source) {
  Object.assign(form, blankForm(), {
    first_name: source.first_name || '',
    last_name: source.last_name || '',
    maiden_name: source.maiden_name || '',
    gender: source.gender || null,
    birth_date: source.birth_date || '',
    death_date: source.death_date || '',
    birth_place: source.birth_place || '',
    death_place: source.death_place || '',
    occupation: source.occupation || '',
    bio: source.bio || '',
    is_living: source.is_living ?? true,
    father_id: source.father_id ?? null,
    mother_id: source.mother_id ?? null,
  })
}

function toPayload() {
  const clean = (value) => (value === '' || value === undefined ? null : value)
  return {
    first_name: form.first_name.trim(),
    last_name: clean(form.last_name?.trim()),
    maiden_name: clean(form.maiden_name?.trim()),
    gender: clean(form.gender),
    birth_date: clean(form.birth_date?.trim()),
    death_date: clean(form.death_date?.trim()),
    birth_place: clean(form.birth_place?.trim()),
    death_place: clean(form.death_place?.trim()),
    occupation: clean(form.occupation?.trim()),
    bio: clean(form.bio),
    is_living: form.is_living,
    father_id: form.father_id ?? null,
    mother_id: form.mother_id ?? null,
  }
}

async function loadPeople() {
  const data = await api.getPersons({ limit: 1000 })
  people.value = data.items
}

async function reload() {
  if (isNew.value) {
    loading.value = false
    return
  }
  person.value = await api.getPerson(route.params.id)
  fillForm(person.value)
  loading.value = false
}

async function savePerson() {
  saving.value = true
  formError.value = ''
  try {
    if (isNew.value) {
      const created = await api.createPerson(toPayload())
      router.replace(`/admin/people/${created.id}`)
    } else {
      await api.updatePerson(person.value.id, toPayload())
      await reload()
    }
  } catch (e) {
    formError.value = e.message
  } finally {
    saving.value = false
  }
}

async function removePerson() {
  if (!window.confirm(`Delete ${person.value.full_name}? This cannot be undone.`)) return
  await api.deletePerson(person.value.id)
  router.push('/admin/people')
}

function partnerOf(union) {
  return union.partner_a?.id === person.value.id ? union.partner_b : union.partner_a
}

// Couples derived from shared children have no id of their own, so build a stable key.
function unionKey(union) {
  if (union.id != null) return `union-${union.id}`
  const partner = partnerOf(union)
  const ids = [person.value.id, partner?.id].filter((id) => id != null).sort((a, b) => a - b)
  return `derived-${ids.join('-')}`
}

async function recordMarriage(union) {
  const partner = partnerOf(union)
  if (!partner) return
  await api.createUnion({
    partner_a_id: person.value.id,
    partner_b_id: partner.id,
    status: 'married',
  })
  await reload()
}

function unionSummary(union) {
  const start = yearOf(union.start_date)
  const end = yearOf(union.end_date)
  const status = union.status && union.status !== 'married' ? union.status : 'married'
  if (start && end) return `${status} ${start}–${end}`
  if (start) return `${status} since ${start}`
  return status
}

async function onUnionChanged() {
  addingUnion.value = false
  editingUnionId.value = null
  await reload()
}

async function removeUnion(union) {
  if (!window.confirm('Remove this marriage/partnership record?')) return
  await api.deleteUnion(union.id)
  await onUnionChanged()
}

async function setPrimary(photo) {
  await api.setPrimaryPhoto(photo.id)
  await reload()
}

async function deletePhoto(photo) {
  if (!window.confirm('Delete this photograph?')) return
  await api.deletePhoto(photo.id)
  await reload()
}

async function updateCaption({ photo, caption }) {
  await api.updatePhoto(photo.id, { caption })
  await reload()
}

async function deleteStory(story) {
  if (!window.confirm('Delete this story?')) return
  await api.deleteStory(story.id)
  await reload()
}

onMounted(async () => {
  await loadPeople()
  await reload()
})

watch(
  () => route.params.id,
  async () => {
    loading.value = true
    editingUnionId.value = null
    addingUnion.value = false
    await reload()
  },
)
</script>
