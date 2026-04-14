<script setup>
import { ChevronDown } from 'lucide-vue-next'
import { AccordionHeader, AccordionTrigger } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <AccordionHeader class="flex">
    <AccordionTrigger
      :class="
        cn(
          'group flex flex-1 items-center justify-between px-4 py-3 text-left text-sm font-semibold text-slate-900 transition hover:text-brand-700',
          $props.class,
        )
      "
    >
      <slot />
      <ChevronDown class="h-4 w-4 shrink-0 text-slate-400 transition duration-200 group-data-[state=open]:rotate-180" />
    </AccordionTrigger>
  </AccordionHeader>
</template>
