<template>
  <div class="h-[calc(100vh-4rem)]">
    <div v-if="loading" class="flex h-full items-center justify-center text-ink-muted">
      Loading family tree…
    </div>
    <div v-else-if="error" class="flex h-full items-center justify-center p-6">
      <EmptyState title="Could not load the tree" :message="error" icon="info" />
    </div>
    <FamilyTree v-else :persons="tree.persons" :unions="tree.unions" :focus-id="focusId" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import FamilyTree from '../components/tree/FamilyTree.vue'
import EmptyState from '../components/EmptyState.vue'
import { api } from '../services/api'

const route = useRoute()
const tree = ref({ persons: [], unions: [] })
const loading = ref(true)
const error = ref('')

const focusId = computed(() => route.query.focus || null)

onMounted(async () => {
  try {
    tree.value = await api.getTree()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
