<template>
  <div class="space-y-8">
    <article v-for="story in stories" :key="story.id">
      <h3 v-if="story.title" class="font-display text-xl font-semibold text-ink">{{ story.title }}</h3>
      <div class="prose-story mt-2 space-y-4" v-html="formatStory(story.body)" />
    </article>
  </div>
</template>

<script setup>
import { formatStory } from '../utils/text'

defineProps({
  stories: { type: Array, default: () => [] },
})
</script>
