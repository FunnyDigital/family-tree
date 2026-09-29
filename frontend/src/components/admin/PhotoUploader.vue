<template>
  <div>
    <label
      class="flex cursor-pointer flex-col items-center justify-center rounded-xl2 border border-dashed border-line bg-canvas/60 px-4 py-8 text-center transition-colors hover:border-accent hover:bg-accent-50/40"
      :class="{ 'pointer-events-none opacity-60': uploading }"
    >
      <Icon name="upload" :size="24" class="text-accent" />
      <span class="mt-2 text-sm font-medium text-ink-soft">
        {{ uploading ? 'Uploading…' : 'Click or drop photographs here' }}
      </span>
      <span class="mt-0.5 text-xs text-ink-faint">JPG, PNG, WEBP or GIF · up to 25 MB each</span>
      <input ref="input" type="file" accept="image/*" multiple class="hidden" @change="onFiles" />
    </label>

    <div v-if="photos.length" class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
      <div
        v-for="photo in photos"
        :key="photo.id"
        class="group relative overflow-hidden rounded-xl border border-line bg-white"
        :class="{ 'border-accent ring-1 ring-accent/40': photo.is_primary }"
      >
        <img :src="photo.thumb_url || photo.url" alt="" class="aspect-square w-full object-cover" />
        <span
          v-if="photo.is_primary"
          class="absolute left-2 top-2 inline-flex items-center gap-1 rounded-full bg-white/90 px-2 py-0.5 text-[11px] font-medium text-accent-700"
        >
          <Icon name="star" :size="12" /> Primary
        </span>
        <div class="absolute right-2 top-2 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
          <button
            v-if="!photo.is_primary"
            class="rounded-full bg-white/90 p-1.5 text-ink-soft hover:text-accent-700"
            title="Set as primary"
            @click="$emit('primary', photo)"
          >
            <Icon name="star" :size="15" />
          </button>
          <button
            class="rounded-full bg-white/90 p-1.5 text-ink-soft hover:text-red-600"
            title="Delete"
            @click="$emit('remove', photo)"
          >
            <Icon name="trash" :size="15" />
          </button>
        </div>
        <div class="border-t border-line p-2">
          <input
            :value="photo.caption || ''"
            class="w-full rounded-md border border-transparent bg-transparent px-1.5 py-1 text-xs text-ink-soft hover:border-line focus:border-accent focus:outline-none"
            placeholder="Add a caption…"
            @change="$emit('caption', { photo, caption: $event.target.value })"
          />
        </div>
      </div>
    </div>

    <p v-else class="mt-3 text-sm text-ink-muted">No photographs yet.</p>
    <p v-if="error" class="mt-2 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Icon from '../Icon.vue'
import { api } from '../../services/api'

const props = defineProps({
  personId: { type: Number, required: true },
  photos: { type: Array, default: () => [] },
})
const emit = defineEmits(['changed', 'primary', 'remove', 'caption'])

const input = ref(null)
const uploading = ref(false)
const error = ref('')

async function onFiles(event) {
  const files = Array.from(event.target.files || [])
  if (!files.length) return
  uploading.value = true
  error.value = ''
  try {
    for (const file of files) {
      await api.uploadPhoto(props.personId, file)
    }
    emit('changed')
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
    if (input.value) input.value.value = ''
  }
}
</script>
