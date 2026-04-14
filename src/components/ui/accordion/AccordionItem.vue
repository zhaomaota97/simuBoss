<script setup>
import { AccordionItem } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  value: {
    type: String,
    required: true,
  },
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <AccordionItem :value="value" :class="cn('rounded-2xl border border-slate-200 bg-slate-50', $props.class)">
    <slot />
  </AccordionItem>
</template>
