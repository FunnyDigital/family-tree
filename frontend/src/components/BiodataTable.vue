<template>
  <dl class="divide-y divide-line">
    <div v-for="row in rows" :key="row.label" class="flex gap-4 py-3 first:pt-0 last:pb-0">
      <dt class="flex w-32 shrink-0 items-center gap-2 text-sm text-ink-muted">
        <Icon :name="row.icon" :size="16" class="text-accent" />
        {{ row.label }}
      </dt>
      <dd class="text-sm text-ink">
        <span>{{ row.value }}</span>
        <span v-if="row.detail" class="block text-ink-faint">{{ row.detail }}</span>
      </dd>
    </div>
  </dl>
</template>

<script setup>
import { computed } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({
  person: { type: Object, required: true },
})

const rows = computed(() => {
  const p = props.person
  const list = []
  if (p.birth_date || p.birth_place) {
    list.push({ label: 'Born', icon: 'calendar', value: p.birth_date || '—', detail: p.birth_place })
  }
  if (p.death_date || p.death_place) {
    list.push({ label: 'Died', icon: 'calendar', value: p.death_date || '—', detail: p.death_place })
  }
  if (p.occupation) list.push({ label: 'Occupation', icon: 'briefcase', value: p.occupation })
  if (p.maiden_name) list.push({ label: 'Maiden name', icon: 'user', value: p.maiden_name })
  return list
})
</script>
