<template>
  <div>
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      <button
        v-for="(photo, i) in photos"
        :key="photo.id"
        class="group relative aspect-square overflow-hidden rounded-xl border border-line bg-accent-50"
        @click="open(i)"
      >
        <img
          :src="photo.thumb_url || photo.url"
          :alt="photo.caption || 'Family photo'"
          class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
        />
        <span
          v-if="photo.is_primary"
          class="absolute left-2 top-2 inline-flex items-center gap-1 rounded-full bg-white/90 px-2 py-0.5 text-[11px] font-medium text-accent-700 shadow-sm"
        >
          <Icon name="star" :size="12" /> Primary
        </span>
        <span
          v-if="photo.caption"
          class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent px-3 pb-2 pt-6 text-left text-xs text-white opacity-0 transition-opacity group-hover:opacity-100"
        >
          {{ photo.caption }}
        </span>
      </button>
    </div>

    <Lightbox
      v-if="index !== null"
      :photos="photos"
      :index="index"
      @update:index="index = $event"
      @close="index = null"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Icon from './Icon.vue'
import Lightbox from './Lightbox.vue'

defineProps({
  photos: { type: Array, default: () => [] },
})

const index = ref(null)

function open(i) {
  index.value = i
}
</script>
