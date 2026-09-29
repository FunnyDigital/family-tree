<template>
  <RouterLink
    :to="`/person/${person.id}`"
    class="chip"
    :class="{ '!px-2 !py-1': small }"
  >
    <PersonAvatar :person="person" :size="small ? 20 : 24" />
    <span class="truncate">{{ person.full_name }}</span>
  </RouterLink>
</template>

<script setup>
import PersonAvatar from './PersonAvatar.vue'

defineProps({
  person: { type: Object, required: true },
  small: { type: Boolean, default: false },
})
</script>
