<script setup>
import { DialogTitle } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <DialogTitle :class="cn('text-lg font-semibold text-slate-900', $props.class)">
    <slot />
  </DialogTitle>
</template>
