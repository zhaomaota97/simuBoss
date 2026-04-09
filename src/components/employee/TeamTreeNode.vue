<template>
  <div
    class="rounded-xl border-2 bg-white shadow-sm"
    :class="isContainer ? 'min-w-[260px]' : 'border-slate-200'"
    :style="isContainer ? { borderColor: accentColor } : undefined"
    draggable="true"
    @dragstart="emit('drag-start', { kind: 'existing', path })"
  >
    <div
      v-if="isContainer"
      class="flex items-center gap-2 px-4 py-3 text-sm font-semibold text-white"
      :style="{ backgroundColor: accentColor }"
    >
      <span class="cursor-grab opacity-70">☰</span>
      <span>{{ resolved.icon }}</span>
      <span class="flex-1">{{ resolved.name }}</span>
      <span class="rounded bg-black/15 px-2 py-0.5 text-[11px]">{{ badgeText }}</span>
      <button class="text-base opacity-80 transition hover:opacity-100" @click="emit('remove', path)">
        ×
      </button>
    </div>

    <template v-if="isContainer">
      <div
        v-if="rawNode.type === 'team_ref'"
        class="rounded-b-xl bg-slate-50 px-4 py-5 text-center text-xs text-slate-400"
      >
        🔒 引用团队若要修改内部结构，请回到团队编辑器中调整
      </div>
      <div
        v-else
        class="flex min-h-16 flex-wrap gap-3 rounded-b-xl bg-slate-50 p-4"
        :class="dropHint === path + ':children' ? 'ring-2 ring-brand-500/40' : ''"
        @dragover.prevent
        @drop="emit('drop-children', path)"
      >
        <div
          v-if="!rawNode.children?.length"
          class="w-full text-center text-xs text-slate-400"
        >
          拖拽经理、工人或团队到这里归属该节点管理
        </div>

        <TeamTreeNode
          v-for="(child, index) in rawNode.children || []"
          :key="`${path}-${index}`"
          :raw-node="child"
          :path="`${path}-${index}`"
          :emps="emps"
          :teams="teams"
          :drop-hint="dropHint"
          @remove="emit('remove', $event)"
          @drag-start="emit('drag-start', $event)"
          @drop-before="emit('drop-before', $event)"
          @drop-children="emit('drop-children', $event)"
        />
      </div>
    </template>

    <div
      v-else
      class="flex items-center gap-2 px-3 py-2 text-sm"
      :class="dropHint === path ? 'ring-2 ring-brand-500/40' : ''"
      @dragover.prevent
      @drop="emit('drop-before', path)"
    >
      <span class="cursor-grab text-slate-300">☰</span>
      <span>{{ resolved.icon }}</span>
      <span class="font-medium">{{ resolved.name }}</span>
      <button class="ml-auto text-sm text-rose-500 transition hover:text-rose-600" @click="emit('remove', path)">
        删除
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { resolveNode } from '../../utils/tree'

defineOptions({ name: 'TeamTreeNode' })

const props = defineProps({
  rawNode: { type: Object, required: true },
  path: { type: String, required: true },
  emps: { type: Array, required: true },
  teams: { type: Array, required: true },
  dropHint: { type: String, default: '' },
})

const emit = defineEmits(['remove', 'drag-start', 'drop-before', 'drop-children'])

const resolved = computed(() => resolveNode(props.rawNode, props.emps, props.teams))
const isContainer = computed(
  () => resolved.value?.role === 'manager' || resolved.value?.type === 'team_resolved',
)
const accentColor = computed(() => (resolved.value?.type === 'team_resolved' ? '#64748b' : '#3b82f6'))
const badgeText = computed(() => (resolved.value?.type === 'team_resolved' ? '团队引用' : '经理'))
</script>
