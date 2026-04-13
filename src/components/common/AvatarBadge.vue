<template>
  <div
    class="flex shrink-0 items-center justify-center overflow-hidden bg-slate-100 text-slate-600"
    :class="[roundedClass, textClass]"
    :style="{ width: `${size}px`, height: `${size}px` }"
  >
    <img v-if="avatarAsset" :src="avatarAsset.src" :alt="avatarAsset.label" class="h-full w-full object-cover" />
    <span v-else>{{ fallbackText }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getAvatarByValue } from '../../config/avatarLibrary'

const props = defineProps({
  icon: { type: String, default: '' },
  label: { type: String, default: '' },
  size: { type: Number, default: 44 },
  rounded: { type: String, default: 'xl' },
  textClass: { type: String, default: 'text-xl font-semibold' },
})

const avatarAsset = computed(() => getAvatarByValue(props.icon))
const fallbackText = computed(() => props.icon || props.label?.slice(0, 2) || '?')
const roundedClass = computed(() => {
  return {
    full: 'rounded-full',
    xl: 'rounded-xl',
    '2xl': 'rounded-2xl',
  }[props.rounded] || 'rounded-xl'
})
</script>
