<template>
  <RouterLink
    :to="`/person/${node.person.id}`"
    data-no-pan
    class="group absolute block rounded-xl2 border bg-surface px-3.5 py-3 shadow-soft transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lift"
    :class="[stateClass]"
    :style="{ left: `${node.x}px`, top: `${node.y}px`, width: `${NODE_W}px`, height: `${NODE_H}px` }"
  >
    <div class="flex items-center gap-3">
      <PersonAvatar :person="node.person" :size="42" :ring="true" />
      <div class="min-w-0">
        <p class="line-clamp-2 font-display text-[13px] font-semibold leading-snug text-ink group-hover:text-accent-700">
          {{ node.person.full_name }}
        </p>
        <p v-if="node.person.life_span" class="truncate text-[11px] text-ink-muted">
          {{ node.person.life_span }}
        </p>
        <p v-if="node.person.occupation" class="truncate text-[10px] text-ink-faint">
          {{ node.person.occupation }}
        </p>
      </div>
    </div>
    <span
      v-if="!node.person.is_living"
      class="absolute right-2.5 top-2.5 text-ink-faint"
      title="Deceased"
    >
      <Icon name="heart" :size="13" />
    </span>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import Icon from '../Icon.vue'
import PersonAvatar from '../PersonAvatar.vue'
import { NODE_W, NODE_H } from '../../composables/useTreeLayout'

const props = defineProps({
  node: { type: Object, required: true },
  highlight: { type: Boolean, default: false },
})

const stateClass = computed(() =>
  props.highlight ? 'border-accent ring-2 ring-accent/40 z-10' : 'border-line',
)
</script>
