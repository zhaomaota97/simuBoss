<script setup>
import { TabsContent } from 'reka-ui'
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
  <TabsContent :value="value" :class="cn('outline-none', $props.class)">
    <slot />
  </TabsContent>
</template>
