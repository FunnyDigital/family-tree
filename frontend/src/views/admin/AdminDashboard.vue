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

      <section class="mt-10">
        <h2 class="mb-4 font-display text-xl font-semibold">Backup &amp; restore</h2>
        <div class="card p-5">
          <div class="flex flex-wrap items-start gap-5">
            <div class="min-w-0 flex-1">
              <p class="font-medium">Download a backup</p>
              <p class="mt-1 text-sm text-ink-muted">
                Save every person, marriage, photograph record and story as a single file you can
                keep safe or move to another machine.
              </p>
            </div>
            <button class="btn-ghost shrink-0 !py-2" :disabled="backupBusy" @click="downloadBackup">
              <Icon name="download" :size="16" />
              {{ backupBusy ? 'Preparing…' : 'Download backup' }}
            </button>
          </div>

          <div class="mt-6 flex flex-wrap items-start gap-5 border-t border-line pt-6">
            <div class="min-w-0 flex-1">
              <p class="font-medium">Restore from a backup</p>
              <p class="mt-1 text-sm text-ink-muted">
                Replace the current people, marriages, photographs and stories with the contents of a
                backup file. Your admin login is left as it is.
              </p>
            </div>
            <div class="flex shrink-0 flex-col items-end gap-2">
              <label
                class="btn-primary cursor-pointer !py-2"
                :class="{ 'pointer-events-none opacity-60': restoreBusy }"
              >
                <Icon name="upload" :size="16" />
                {{ restoreBusy ? 'Restoring…' : 'Choose a backup file…' }}
                <input
                  type="file"
                  accept=".db,application/octet-stream,application/x-sqlite3"
                  class="hidden"
                  @change="onRestoreFile"
                />
              </label>
              <p
                v-if="message"
                class="max-w-xs text-right text-sm"
                :class="messageError ? 'text-red-600' : 'text-accent-700'"
              >
                {{ message }}
              </p>
            </div>
          </div>
        </div>
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

const backupBusy = ref(false)
const restoreBusy = ref(false)
const message = ref('')
const messageError = ref(false)

const cards = computed(() => [
  { label: 'People', value: stats.value.total_people ?? 0, icon: 'users' },
  { label: 'Generations', value: stats.value.generations ?? 0, icon: 'generations' },
  { label: 'Photographs', value: stats.value.total_photos ?? 0, icon: 'image' },
  { label: 'Stories', value: stats.value.total_stories ?? 0, icon: 'leaf' },
])

async function load() {
  const [statsData, peopleData] = await Promise.all([api.getStats(), api.getPersons({ limit: 6 })])
  stats.value = statsData
  recent.value = peopleData.items
}

async function downloadBackup() {
  backupBusy.value = true
  message.value = ''
  try {
    const blob = await api.downloadBackup()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'family-tree-backup.db'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    messageError.value = false
    message.value = 'Backup downloaded.'
  } catch (e) {
    messageError.value = true
    message.value = e.message
  } finally {
    backupBusy.value = false
  }
}

async function onRestoreFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const ok = window.confirm(
    `Replace all current family data with "${file.name}"?\n\nThis overwrites the people, marriages, ` +
      `photographs and stories currently on this site. It cannot be undone.`,
  )
  if (!ok) {
    event.target.value = ''
    return
  }
  restoreBusy.value = true
  message.value = ''
  try {
    const result = await api.restoreBackup(file)
    messageError.value = false
    message.value =
      `Restored ${result.people} ${result.people === 1 ? 'person' : 'people'}, ` +
      `${result.unions} ${result.unions === 1 ? 'marriage' : 'marriages'} and ` +
      `${result.stories} ${result.stories === 1 ? 'story' : 'stories'}.`
    await load()
  } catch (e) {
    messageError.value = true
    message.value = e.message
  } finally {
    restoreBusy.value = false
    event.target.value = ''
  }
}

onMounted(async () => {
  try {
    await load()
  } catch {
    /* leave the dashboard empty */
  } finally {
    loading.value = false
  }
})
</script>
