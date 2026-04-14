<script setup>
import { TabsList } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <TabsList
    :class="
      cn(
        'inline-flex h-10 items-center justify-center rounded-full bg-slate-100 p-1 text-slate-600',
        $props.class,
      )
    "
  >
    <slot />
  </TabsList>
</template>
