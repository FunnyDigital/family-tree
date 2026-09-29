<template>
  <form class="card p-6" @submit.prevent="$emit('submit')">
    <div class="grid gap-4 sm:grid-cols-2">
      <div>
        <label class="label">First name *</label>
        <input v-model="form.first_name" class="field" required maxlength="100" />
      </div>
      <div>
        <label class="label">Last name</label>
        <input v-model="form.last_name" class="field" maxlength="100" />
      </div>
      <div>
        <label class="label">Maiden name</label>
        <input v-model="form.maiden_name" class="field" maxlength="100" />
      </div>
      <div>
        <label class="label">Gender</label>
        <select v-model="form.gender" class="field">
          <option :value="null">—</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
          <option value="unknown">Unknown</option>
        </select>
      </div>
      <div>
        <label class="label">Date of birth</label>
        <input v-model="form.birth_date" class="field" placeholder="1948 or 1948-04-05" maxlength="32" />
      </div>
      <div>
        <label class="label">Date of death</label>
        <input v-model="form.death_date" class="field" placeholder="Leave blank if living" maxlength="32" />
      </div>
      <div>
        <label class="label">Place of birth</label>
        <input v-model="form.birth_place" class="field" maxlength="160" />
      </div>
      <div>
        <label class="label">Place of death</label>
        <input v-model="form.death_place" class="field" maxlength="160" />
      </div>
      <div>
        <label class="label">Occupation</label>
        <input v-model="form.occupation" class="field" maxlength="160" />
      </div>
      <div class="flex items-end pb-1">
        <label class="inline-flex cursor-pointer items-center gap-2 text-sm text-ink-soft">
          <input
            v-model="form.is_living"
            type="checkbox"
            class="h-4 w-4 rounded border-line text-accent focus:ring-accent"
          />
          Still living
        </label>
      </div>
      <div>
        <label class="label">Father</label>
        <select v-model="form.father_id" class="field">
          <option :value="null">— Unknown —</option>
          <option v-for="option in parentOptions" :key="option.id" :value="option.id">
            {{ option.full_name }}{{ option.life_span ? ` (${option.life_span})` : '' }}
          </option>
        </select>
      </div>
      <div>
        <label class="label">Mother</label>
        <select v-model="form.mother_id" class="field">
          <option :value="null">— Unknown —</option>
          <option v-for="option in parentOptions" :key="option.id" :value="option.id">
            {{ option.full_name }}{{ option.life_span ? ` (${option.life_span})` : '' }}
          </option>
        </select>
      </div>
    </div>

    <div class="mt-5">
      <label class="label">Biography / write-up</label>
      <textarea
        v-model="form.bio"
        rows="6"
        class="field"
        placeholder="Write about their life, character and memories…"
      />
      <p class="mt-1.5 text-xs text-ink-faint">
        Plain text. Use blank lines for paragraphs, **bold**, *italic* and [links](https://example.com).
      </p>
    </div>

    <div class="mt-6 flex flex-wrap items-center gap-3">
      <button type="submit" class="btn-primary" :disabled="saving">
        {{ saving ? 'Saving…' : 'Save details' }}
      </button>
      <slot name="actions" />
      <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'

const form = defineModel({ type: Object, required: true })

const props = defineProps({
  people: { type: Array, default: () => [] },
  excludeId: { type: Number, default: null },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['submit'])

const parentOptions = computed(() =>
  props.people.filter((person) => person.id !== props.excludeId),
)
</script>
