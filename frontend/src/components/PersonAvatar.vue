<template>
  <span
    class="relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-accent-50 font-display font-semibold text-accent-700"
    :class="containerClass"
    :style="{ width: px, height: px, fontSize: fontSize }"
  >
    <img
      v-if="person?.photo_url"
      :src="person.photo_url"
      :alt="person?.full_name || 'Portrait'"
      class="h-full w-full object-cover"
      :class="{ 'grayscale-[35%]': deceased }"
      loading="lazy"
    />
    <template v-else>{{ initials(person?.full_name) }}</template>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { initials } from '../utils/text'

const props = defineProps({
  person: { type: Object, default: null },
  size: { type: Number, default: 56 },
  ring: { type: Boolean, default: false },
})

const px = computed(() => `${props.size}px`)
const fontSize = computed(() => `${Math.round(props.size * 0.36)}px`)
const deceased = computed(() => props.person && props.person.is_living === false)
const containerClass = computed(() => (props.ring ? 'ring-2 ring-white shadow-soft' : ''))
</script>
