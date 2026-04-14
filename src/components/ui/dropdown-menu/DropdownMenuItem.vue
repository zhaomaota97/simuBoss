<script setup>
import { DropdownMenuItem } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  class: {
    type: String,
    default: '',
  },
  inset: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <DropdownMenuItem
    :class="
      cn(
        'relative flex cursor-default select-none items-center rounded-xl px-3 py-2 text-sm outline-none transition focus:bg-slate-50 data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        inset && 'pl-8',
        $props.class,
      )
    "
  >
    <slot />
  </DropdownMenuItem>
</template>
