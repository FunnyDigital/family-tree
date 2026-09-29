<template>
  <RouterLink
    :to="`/person/${person.id}`"
    class="group card flex items-center gap-4 p-4 transition-all hover:-translate-y-0.5 hover:shadow-lift"
  >
    <PersonAvatar :person="person" :size="64" :ring="true" />
    <div class="min-w-0">
      <p class="truncate font-display text-lg font-semibold leading-tight text-ink group-hover:text-accent-700">
        {{ person.full_name }}
      </p>
      <p v-if="person.maiden_name" class="truncate text-xs italic text-ink-faint">
        née {{ person.maiden_name }}
      </p>
      <p v-if="person.life_span" class="mt-0.5 text-sm text-ink-muted">{{ person.life_span }}</p>
      <p v-if="person.occupation" class="truncate text-sm text-ink-faint">{{ person.occupation }}</p>
    </div>
    <Icon
      name="arrowRight"
      :size="18"
      class="ml-auto shrink-0 text-ink-faint transition-transform group-hover:translate-x-0.5 group-hover:text-accent"
    />
  </RouterLink>
</template>

<script setup>
import Icon from './Icon.vue'
import PersonAvatar from './PersonAvatar.vue'

defineProps({
  person: { type: Object, required: true },
})
</script>
