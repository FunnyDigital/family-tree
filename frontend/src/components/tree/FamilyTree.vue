<template>
  <div class="relative h-full w-full bg-canvas">
    <PanZoom
      ref="pz"
      :content-width="layout.width"
      :content-height="layout.height"
      @update:scale="zoom = Math.round($event * 100)"
    >
      <svg
        :width="layout.width"
        :height="layout.height"
        class="absolute left-0 top-0 overflow-visible"
      >
        <g fill="none" stroke="#a8a29e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path v-for="path in layout.paths" :key="path.key" :d="path.d" />
        </g>
        <g fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path v-for="link in layout.coupleLinks" :key="link.id" :d="link.d" />
        </g>
        <g fill="#78716c" font-size="11" text-anchor="middle" stroke="none">
          <text
            v-for="link in layout.coupleLinks"
            :key="`label-${link.id}`"
            :x="link.midX"
            :y="link.y - 7"
          >
            {{ barLabel(link) }}
          </text>
        </g>
      </svg>

      <TreeNode
        v-for="node in layout.nodes"
        :key="node.person.id"
        :node="node"
        :highlight="node.person.id === highlightId"
      />
    </PanZoom>

    <TreeControls
      :search="search"
      :matches="matches"
      :zoom="zoom"
      :show-search="showSearch"
      @update:search="onSearch"
      @select="selectPerson"
      @zoom-in="pz?.zoomBy(1.2)"
      @zoom-out="pz?.zoomBy(1 / 1.2)"
      @fit="pz?.fit()"
    />

    <div class="pointer-events-none absolute inset-x-0 bottom-0 z-30 flex flex-wrap items-end justify-between gap-3 p-3 sm:p-4">
      <div class="pointer-events-auto rounded-full border border-line bg-white/90 px-3.5 py-1.5 text-xs text-ink-muted shadow-soft backdrop-blur">
        <span class="font-medium text-ink-soft">{{ layout.nodes.length }}</span> people ·
        <span class="font-medium text-ink-soft">{{ layout.generations }}</span> generations
      </div>
      <div class="hidden rounded-full border border-line bg-white/90 px-3.5 py-1.5 text-xs text-ink-faint shadow-soft backdrop-blur sm:block">
        Drag to pan · Scroll to zoom · Click a card for the profile
      </div>
    </div>

    <div
      v-if="!layout.nodes.length"
      class="absolute inset-0 z-20 flex items-center justify-center p-6"
    >
      <EmptyState
        title="No family members yet"
        message="Once people are added, the tree will appear here."
        icon="tree"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import PanZoom from './PanZoom.vue'
import TreeNode from './TreeNode.vue'
import TreeControls from './TreeControls.vue'
import EmptyState from '../EmptyState.vue'
import { NODE_H, NODE_W, computeLayout } from '../../composables/useTreeLayout'
import { yearOf } from '../../utils/text'

const props = defineProps({
  persons: { type: Array, default: () => [] },
  unions: { type: Array, default: () => [] },
  focusId: { type: [Number, String], default: null },
  showSearch: { type: Boolean, default: true },
})

const pz = ref(null)
const zoom = ref(100)
const search = ref('')
const highlightId = ref(null)

const layout = computed(() => computeLayout(props.persons, props.unions))

const matches = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return []
  return props.persons.filter((person) => person.full_name.toLowerCase().includes(query))
})

const STATUS_LABEL = {
  married: '',
  partnered: 'part.',
  divorced: 'div.',
  widowed: 'wid.',
  separated: 'sep.',
}

function barLabel(bar) {
  const year = yearOf(bar.start_date)
  const suffix = STATUS_LABEL[bar.status] ? ` ${STATUS_LABEL[bar.status]}` : ''
  return `${year || ''}${suffix}`.trim()
}

function onSearch(value) {
  search.value = value
}

function selectPerson(person) {
  highlightId.value = person.id
  search.value = ''
  const node = layout.value.nodes.find((n) => n.person.id === person.id)
  if (node) pz.value?.centerOn(node.x + NODE_W / 2, node.y + NODE_H / 2)
}

function focus(id) {
  const numeric = Number(id)
  const node = layout.value.nodes.find((n) => n.person.id === numeric)
  if (!node) return
  highlightId.value = numeric
  pz.value?.centerOn(node.x + NODE_W / 2, node.y + NODE_H / 2)
}

watch(
  () => props.focusId,
  (value) => {
    if (value) nextTick(() => focus(value))
  },
)

onMounted(() => {
  if (props.focusId) focus(props.focusId)
})

defineExpose({ focus })
</script>
