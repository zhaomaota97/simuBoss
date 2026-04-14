<script setup>
import { AccordionContent } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <AccordionContent :class="cn('overflow-hidden border-t border-slate-200 bg-white text-sm', $props.class)">
    <div class="px-4 py-4">
      <slot />
    </div>
  </AccordionContent>
</template>
