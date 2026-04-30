<template>
  <div class="pointer-events-none fixed right-5 top-5 z-[80] flex w-[340px] max-w-[calc(100vw-2.5rem)] flex-col gap-3">
    <div
      v-for="item in messageStore.visibleMessages"
      :key="item.id"
      class="pointer-events-auto rounded-2xl border bg-white/95 px-4 py-3 shadow-lg backdrop-blur"
      :class="typeClass(item.type)"
    >
      <div class="flex items-start gap-3">
        <div class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full" :class="iconClass(item.type)">
          <Loader2 v-if="item.type === 'loading'" class="h-4 w-4 animate-spin" />
          <Check v-else-if="item.type === 'success'" class="h-4 w-4" />
          <TriangleAlert v-else-if="item.type === 'error'" class="h-4 w-4" />
          <Info v-else class="h-4 w-4" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="text-sm font-semibold">{{ item.title }}</div>
          <div v-if="item.message" class="mt-1 text-xs leading-5 opacity-80">{{ item.message }}</div>
        </div>
        <button
          class="cursor-pointer rounded-lg p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
          type="button"
          @click="messageStore.remove(item.id)"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Check, Info, Loader2, TriangleAlert, X } from 'lucide-vue-next'
import { useMessageStore } from '../../stores/messages'

const messageStore = useMessageStore()

function typeClass(type) {
  if (type === 'success') return 'border-emerald-200 text-emerald-800'
  if (type === 'error') return 'border-rose-200 text-rose-800'
  if (type === 'loading') return 'border-indigo-200 text-indigo-800'
  return 'border-slate-200 text-slate-800'
}

function iconClass(type) {
  if (type === 'success') return 'bg-emerald-50 text-emerald-600'
  if (type === 'error') return 'bg-rose-50 text-rose-600'
  if (type === 'loading') return 'bg-indigo-50 text-indigo-600'
  return 'bg-slate-100 text-slate-600'
}
</script>
