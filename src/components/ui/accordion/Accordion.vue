<script setup>
import { AccordionRoot, useForwardPropsEmits } from 'reka-ui'

const props = defineProps({
  type: {
    type: String,
    default: 'single',
  },
  collapsible: {
    type: Boolean,
    default: false,
  },
  modelValue: {
    type: [String, Array],
    default: undefined,
  },
  defaultValue: {
    type: [String, Array],
    default: undefined,
  },
})

const emits = defineEmits(['update:modelValue'])
const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <AccordionRoot v-bind="forwarded">
    <slot />
  </AccordionRoot>
</template>
