<template>
  <div class="pointer-events-none absolute inset-x-0 top-0 z-30 flex items-start justify-between gap-3 p-3 sm:p-4">
    <div v-if="showSearch" class="pointer-events-auto relative w-full max-w-xs">
      <SearchBar
        :model-value="search"
        placeholder="Find a person…"
        @update:model-value="$emit('update:search', $event)"
      />
      <div v-if="matches.length" class="absolute inset-x-0 top-full mt-2 max-h-64 overflow-auto card p-1.5">
        <button
          v-for="person in matches.slice(0, 10)"
          :key="person.id"
          class="flex w-full items-center gap-2.5 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-accent-50"
          @click="$emit('select', person)"
        >
          <PersonAvatar :person="person" :size="28" />
          <span class="truncate">{{ person.full_name }}</span>
          <span class="ml-auto shrink-0 text-xs text-ink-faint">{{ person.life_span }}</span>
        </button>
      </div>
    </div>

    <div class="pointer-events-auto ml-auto flex items-center gap-0.5 rounded-full border border-line bg-white/90 p-1 shadow-soft backdrop-blur">
      <button class="rounded-full p-2 text-ink-soft hover:bg-accent-50 hover:text-accent-700" title="Zoom out" @click="$emit('zoomOut')">
        <Icon name="zoomOut" :size="18" />
      </button>
      <span class="w-11 select-none text-center text-xs font-medium text-ink-muted">{{ zoom }}%</span>
      <button class="rounded-full p-2 text-ink-soft hover:bg-accent-50 hover:text-accent-700" title="Zoom in" @click="$emit('zoomIn')">
        <Icon name="zoomIn" :size="18" />
      </button>
      <div class="mx-1 h-5 w-px bg-line" />
      <button class="rounded-full p-2 text-ink-soft hover:bg-accent-50 hover:text-accent-700" title="Fit to screen" @click="$emit('fit')">
        <Icon name="fit" :size="18" />
      </button>
    </div>
  </div>
</template>

<script setup>
import Icon from '../Icon.vue'
import SearchBar from '../SearchBar.vue'
import PersonAvatar from '../PersonAvatar.vue'

defineProps({
  search: { type: String, default: '' },
  matches: { type: Array, default: () => [] },
  zoom: { type: Number, default: 100 },
  showSearch: { type: Boolean, default: true },
})
defineEmits(['update:search', 'select', 'zoomIn', 'zoomOut', 'fit'])
</script>
