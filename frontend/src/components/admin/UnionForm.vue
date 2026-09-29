<template>
  <form class="rounded-xl border border-line bg-canvas/60 p-4" @submit.prevent="save">
    <div class="grid gap-3 sm:grid-cols-2">
      <div class="sm:col-span-2">
        <label class="label">Partner</label>
        <select v-model="form.partner_b_id" class="field" :disabled="isPrimaryFixed && !union">
          <option :value="null">— Unknown —</option>
          <option v-for="option in partnerOptions" :key="option.id" :value="option.id">
            {{ option.full_name }}{{ option.life_span ? ` (${option.life_span})` : '' }}
          </option>
        </select>
      </div>
      <div>
        <label class="label">Status</label>
        <select v-model="form.status" class="field">
          <option value="married">Married</option>
          <option value="partnered">Partnered</option>
          <option value="divorced">Divorced</option>
          <option value="widowed">Widowed</option>
          <option value="separated">Separated</option>
        </select>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="label">From</label>
          <input v-model="form.start_date" class="field" placeholder="1972" maxlength="32" />
        </div>
        <div>
          <label class="label">Until</label>
          <input v-model="form.end_date" class="field" placeholder="1985" maxlength="32" />
        </div>
      </div>
      <div class="sm:col-span-2">
        <label class="label">Notes</label>
        <input v-model="form.notes" class="field" placeholder="Optional notes" />
      </div>
    </div>

    <div class="mt-4 flex items-center gap-2">
      <button type="submit" class="btn-primary !py-2" :disabled="saving">
        {{ saving ? 'Saving…' : union ? 'Save union' : 'Add union' }}
      </button>
      <button v-if="union" type="button" class="btn-danger !py-2" @click="$emit('delete', union)">
        <Icon name="trash" :size="15" /> Remove
      </button>
      <button v-if="union" type="button" class="btn-ghost !py-2" @click="$emit('cancel')">Cancel</button>
      <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
    </div>
  </form>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import Icon from '../Icon.vue'
import { api } from '../../services/api'

const props = defineProps({
  personId: { type: Number, required: true },
  people: { type: Array, default: () => [] },
  union: { type: Object, default: null },
})
const emit = defineEmits(['saved', 'cancel', 'delete'])

const saving = ref(false)
const error = ref('')
const isPrimaryFixed = true

const form = reactive({
  partner_b_id: null,
  status: 'married',
  start_date: '',
  end_date: '',
  notes: '',
})

function reset() {
  if (props.union) {
    const partner =
      props.union.partner_a?.id === props.personId ? props.union.partner_b : props.union.partner_a
    form.partner_b_id = partner?.id ?? null
    form.status = props.union.status || 'married'
    form.start_date = props.union.start_date || ''
    form.end_date = props.union.end_date || ''
    form.notes = props.union.notes || ''
  } else {
    form.partner_b_id = null
    form.status = 'married'
    form.start_date = ''
    form.end_date = ''
    form.notes = ''
  }
}

watch(() => props.union, reset, { immediate: true })

const partnerOptions = computed(() => props.people.filter((person) => person.id !== props.personId))

async function save() {
  saving.value = true
  error.value = ''
  const payload = {
    partner_a_id: props.union?.partner_a_id ?? props.personId,
    partner_b_id: form.partner_b_id,
    status: form.status,
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    notes: form.notes || null,
  }
  try {
    if (props.union) await api.updateUnion(props.union.id, payload)
    else await api.createUnion(payload)
    emit('saved')
    reset()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
