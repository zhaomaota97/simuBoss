<template>
  <div
    class="rounded-xl border-2 bg-white shadow-sm"
    :class="[isContainer ? 'min-w-[260px]' : 'border-slate-200', !readOnly && 'cursor-grab']"
    :style="isContainer ? { borderColor: accentColor } : undefined"
    :draggable="!readOnly"
    @dragstart="!readOnly && emit('drag-start', { kind: 'existing', path })"
  >
    <div
      v-if="isContainer"
      class="flex items-center gap-2 px-4 py-3 text-sm font-semibold text-white"
      :style="{ backgroundColor: accentColor }"
    >
      <span v-if="!readOnly" class="cursor-grab opacity-70">⋮⋮</span>
      <AvatarBadge :icon="resolved.icon" :label="resolved.name" :size="24" rounded="xl" text-class="text-xs font-semibold" />
      <span class="flex-1">{{ resolved.name }}</span>
      <span class="rounded bg-black/15 px-2 py-0.5 text-[11px]">{{ badgeText }}</span>
      <button
        v-if="!readOnly"
        class="text-base opacity-80 transition hover:opacity-100"
        @click="emit('remove', path)"
      >
        ×
      </button>
    </div>

    <template v-if="isContainer">
      <div
        v-if="rawNode.type === 'team_ref'"
        class="rounded-b-xl bg-slate-50 px-4 py-5 text-center text-xs text-slate-400"
      >
        团队引用如需修改内部结构，请回到该团队本身进行编辑。
      </div>
      <div
        v-else
        class="flex min-h-16 flex-wrap gap-3 rounded-b-xl bg-slate-50 p-4"
        :class="!readOnly && dropHint === path + ':children' ? 'ring-2 ring-brand-500/40' : ''"
        @dragover.prevent="!readOnly"
        @drop="!readOnly && emit('drop-children', path)"
      >
        <div
          v-if="!rawNode.children?.length"
          class="w-full text-center text-xs text-slate-400"
        >
          {{ readOnly ? '当前节点没有下属成员' : '拖拽经理、员工或团队到这里归属该节点管理' }}
        </div>

        <TeamTreeNode
          v-for="(child, index) in rawNode.children || []"
          :key="`${path}-${index}`"
          :raw-node="child"
          :path="`${path}-${index}`"
          :emps="emps"
          :teams="teams"
          :drop-hint="dropHint"
          :read-only="readOnly"
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
      :class="!readOnly && dropHint === path ? 'ring-2 ring-brand-500/40' : ''"
      @dragover.prevent="!readOnly"
      @drop="!readOnly && emit('drop-before', path)"
    >
      <span v-if="!readOnly" class="cursor-grab text-slate-300">⋮⋮</span>
      <AvatarBadge :icon="resolved.icon" :label="resolved.name" :size="24" rounded="xl" text-class="text-xs font-semibold" />
      <span class="font-medium">{{ resolved.name }}</span>
      <button
        v-if="!readOnly"
        class="ml-auto text-sm text-rose-500 transition hover:text-rose-600"
        @click="emit('remove', path)"
      >
        删除
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AvatarBadge from '../common/AvatarBadge.vue'
import { resolveNode } from '../../utils/tree'

defineOptions({ name: 'TeamTreeNode' })

const props = defineProps({
  rawNode: { type: Object, required: true },
  path: { type: String, required: true },
  emps: { type: Array, required: true },
  teams: { type: Array, required: true },
  dropHint: { type: String, default: '' },
  readOnly: { type: Boolean, default: false },
})

const emit = defineEmits(['remove', 'drag-start', 'drop-before', 'drop-children'])

const resolved = computed(() => resolveNode(props.rawNode, props.emps, props.teams))
const isContainer = computed(
  () => resolved.value?.role === 'manager' || resolved.value?.type === 'team_resolved',
)
const accentColor = computed(() => (resolved.value?.type === 'team_resolved' ? '#64748b' : '#3b82f6'))
const badgeText = computed(() => (resolved.value?.type === 'team_resolved' ? '团队引用' : '经理'))
</script>
