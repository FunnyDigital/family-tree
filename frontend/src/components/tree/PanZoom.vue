<template>
  <div
    ref="viewport"
    class="relative h-full w-full touch-none overflow-hidden"
    :class="dragging ? 'cursor-grabbing' : 'cursor-grab'"
    @wheel.prevent="onWheel"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
  >
    <div class="absolute left-0 top-0 origin-top-left" :style="innerStyle">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  contentWidth: { type: Number, default: 0 },
  contentHeight: { type: Number, default: 0 },
  minScale: { type: Number, default: 0.25 },
  maxScale: { type: Number, default: 2 },
})

const emit = defineEmits(['update:scale'])

const viewport = ref(null)
const scale = ref(1)
const offset = reactive({ x: 0, y: 0 })
const dragging = ref(false)
let pointerStart = null

const innerStyle = computed(() => ({
  transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale.value})`,
  width: `${props.contentWidth}px`,
  height: `${props.contentHeight}px`,
}))

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function setScale(next, originX = null, originY = null) {
  const clamped = clamp(next, props.minScale, props.maxScale)
  if (originX != null && originY != null) {
    const ratio = clamped / scale.value
    offset.x = originX - (originX - offset.x) * ratio
    offset.y = originY - (originY - offset.y) * ratio
  }
  scale.value = clamped
  emit('update:scale', clamped)
}

function onWheel(event) {
  const rect = viewport.value.getBoundingClientRect()
  const factor = event.deltaY < 0 ? 1.12 : 1 / 1.12
  setScale(scale.value * factor, event.clientX - rect.left, event.clientY - rect.top)
}

function onPointerDown(event) {
  if (event.target.closest('[data-no-pan]')) return
  dragging.value = true
  pointerStart = { x: event.clientX, y: event.clientY, ox: offset.x, oy: offset.y }
  viewport.value.setPointerCapture(event.pointerId)
}

function onPointerMove(event) {
  if (!dragging.value || !pointerStart) return
  offset.x = pointerStart.ox + (event.clientX - pointerStart.x)
  offset.y = pointerStart.oy + (event.clientY - pointerStart.y)
}

function onPointerUp(event) {
  dragging.value = false
  pointerStart = null
  if (viewport.value?.hasPointerCapture?.(event.pointerId)) {
    viewport.value.releasePointerCapture(event.pointerId)
  }
}

function fit() {
  if (!viewport.value || !props.contentWidth || !props.contentHeight) return
  const vw = viewport.value.clientWidth
  const vh = viewport.value.clientHeight
  const padding = 48
  const next = Math.min(
    (vw - padding * 2) / props.contentWidth,
    (vh - padding * 2) / props.contentHeight,
  )
  scale.value = clamp(next, props.minScale, props.maxScale)
  offset.x = (vw - props.contentWidth * scale.value) / 2
  offset.y = Math.max(24, (vh - props.contentHeight * scale.value) / 2)
  emit('update:scale', scale.value)
}

function zoomBy(factor) {
  if (!viewport.value) return
  setScale(scale.value * factor, viewport.value.clientWidth / 2, viewport.value.clientHeight / 2)
}

function centerOn(x, y) {
  if (!viewport.value) return
  offset.x = viewport.value.clientWidth / 2 - x * scale.value
  offset.y = viewport.value.clientHeight / 2 - y * scale.value
}

onMounted(() => {
  fit()
})

defineExpose({ fit, zoomBy, centerOn, scale })
</script>
