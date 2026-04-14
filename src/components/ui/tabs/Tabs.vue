<script setup>
import { TabsRoot, useForwardPropsEmits } from 'reka-ui'

const props = defineProps({
  modelValue: {
    type: String,
    default: undefined,
  },
  defaultValue: {
    type: String,
    default: undefined,
  },
  orientation: {
    type: String,
    default: 'horizontal',
  },
})

const emits = defineEmits(['update:modelValue'])
const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <TabsRoot v-bind="forwarded">
    <slot />
  </TabsRoot>
</template>
