<script setup>
import { TabsTrigger } from 'reka-ui'
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
  <TabsTrigger
    :value="value"
    :class="
      cn(
        'inline-flex items-center justify-center rounded-full px-3 py-1.5 text-sm font-semibold transition outline-none data-[state=active]:bg-brand-500 data-[state=active]:text-white data-[state=inactive]:text-slate-600',
        $props.class,
      )
    "
  >
    <slot />
  </TabsTrigger>
</template>
