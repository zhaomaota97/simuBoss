<script setup>
import { DialogDescription } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <DialogDescription :class="cn('text-sm text-slate-500', $props.class)">
    <slot />
  </DialogDescription>
</template>
