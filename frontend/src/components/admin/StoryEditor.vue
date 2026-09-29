<template>
  <div class="space-y-5">
    <div v-for="story in stories" :key="story.id" class="rounded-xl border border-line bg-canvas/60 p-4">
      <template v-if="editingId === story.id">
        <input v-model="draft.title" class="field mb-2" placeholder="Title (optional)" maxlength="200" />
        <textarea v-model="draft.body" rows="5" class="field" placeholder="Write the story…" />
        <div class="mt-4 flex items-center gap-2">
          <button class="btn-primary !py-2" :disabled="saving" @click="save(story.id)">Save</button>
          <button class="btn-ghost !py-2" @click="cancel">Cancel</button>
        </div>
      </template>
      <template v-else>
        <div class="flex items-start justify-between gap-3">
          <h4 v-if="story.title" class="font-display text-lg font-semibold">{{ story.title }}</h4>
          <span v-else class="font-display text-lg font-semibold text-ink-faint">Untitled</span>
          <div class="flex shrink-0 gap-1">
            <button class="rounded-full p-1.5 text-ink-faint hover:text-accent-700" title="Edit" @click="startEdit(story)">
              <Icon name="edit" :size="16" />
            </button>
            <button class="rounded-full p-1.5 text-ink-faint hover:text-red-600" title="Delete" @click="$emit('delete', story)">
              <Icon name="trash" :size="16" />
            </button>
          </div>
        </div>
        <p class="mt-1 line-clamp-3 whitespace-pre-line text-sm text-ink-muted">{{ story.body }}</p>
      </template>
    </div>

    <p v-if="!stories.length && !creating" class="text-sm text-ink-muted">No stories yet.</p>

    <div v-if="creating" class="rounded-xl border border-accent/40 bg-accent-50/40 p-4">
      <input v-model="draft.title" class="field mb-2" placeholder="Title (optional)" maxlength="200" />
      <textarea v-model="draft.body" rows="5" class="field" placeholder="Write the story…" />
      <div class="mt-4 flex items-center gap-2">
        <button class="btn-primary !py-2" :disabled="saving || !draft.body.trim()" @click="save(null)">Add story</button>
        <button class="btn-ghost !py-2" @click="cancel">Cancel</button>
      </div>
    </div>
    <button v-else class="btn-ghost" @click="startCreate">
      <Icon name="plus" :size="16" /> Add a story
    </button>

    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import Icon from '../Icon.vue'
import { api } from '../../services/api'

const props = defineProps({
  personId: { type: Number, required: true },
  stories: { type: Array, default: () => [] },
})
const emit = defineEmits(['changed', 'delete'])

const editingId = ref(null)
const creating = ref(false)
const saving = ref(false)
const error = ref('')
const draft = reactive({ title: '', body: '' })

function startCreate() {
  creating.value = true
  editingId.value = null
  draft.title = ''
  draft.body = ''
}

function startEdit(story) {
  editingId.value = story.id
  creating.value = false
  draft.title = story.title || ''
  draft.body = story.body || ''
}

function cancel() {
  editingId.value = null
  creating.value = false
  draft.title = ''
  draft.body = ''
}

async function save(id) {
  saving.value = true
  error.value = ''
  try {
    const payload = { title: draft.title || null, body: draft.body }
    if (id) await api.updateStory(id, payload)
    else await api.createStory(props.personId, payload)
    cancel()
    emit('changed')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
