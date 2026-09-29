<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex flex-col bg-ink/95 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      @click.self="$emit('close')"
    >
      <div class="flex items-center justify-between px-4 py-3 text-white/80">
        <span class="text-sm">{{ index + 1 }} / {{ photos.length }}</span>
        <button class="rounded-full p-2 hover:bg-white/10" aria-label="Close" @click="$emit('close')">
          <Icon name="close" :size="22" />
        </button>
      </div>

      <div class="relative flex flex-1 items-center justify-center px-4 pb-6">
        <button
          v-if="photos.length > 1"
          class="absolute left-2 rounded-full bg-white/10 p-3 text-white hover:bg-white/20 sm:left-6"
          aria-label="Previous"
          @click="step(-1)"
        >
          <Icon name="chevronLeft" :size="24" />
        </button>

        <figure class="max-h-full max-w-4xl text-center" @click.stop>
          <img
            :src="current.url"
            :alt="current.caption || 'Family photo'"
            class="mx-auto max-h-[76vh] w-auto rounded-lg object-contain shadow-lift"
          />
          <figcaption v-if="current.caption" class="mt-3 text-sm text-white/80">
            {{ current.caption }}
          </figcaption>
        </figure>

        <button
          v-if="photos.length > 1"
          class="absolute right-2 rounded-full bg-white/10 p-3 text-white hover:bg-white/20 sm:right-6"
          aria-label="Next"
          @click="step(1)"
        >
          <Icon name="chevronRight" :size="24" />
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  photos: { type: Array, required: true },
  index: { type: Number, required: true },
})
const emit = defineEmits(['update:index', 'close'])

const current = computed(() => props.photos[props.index] || {})

function step(delta) {
  const next = (props.index + delta + props.photos.length) % props.photos.length
  emit('update:index', next)
}

function onKey(event) {
  if (event.key === 'Escape') emit('close')
  else if (event.key === 'ArrowRight') step(1)
  else if (event.key === 'ArrowLeft') step(-1)
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  document.body.style.overflow = 'hidden'
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>
