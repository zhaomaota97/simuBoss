<script setup>
import { DropdownMenuContent, DropdownMenuPortal } from 'reka-ui'
import { cn } from '../../../lib/utils'

defineProps({
  class: {
    type: String,
    default: '',
  },
  sideOffset: {
    type: Number,
    default: 8,
  },
})
</script>

<template>
  <DropdownMenuPortal>
    <DropdownMenuContent
      :side-offset="sideOffset"
      :class="
        cn(
          'z-50 min-w-[12rem] rounded-2xl border border-slate-200 bg-white p-2 text-slate-700 shadow-[0_20px_40px_rgba(15,23,42,0.18)] outline-none',
          $props.class,
        )
      "
    >
      <slot />
    </DropdownMenuContent>
  </DropdownMenuPortal>
</template>
