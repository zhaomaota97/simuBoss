<template>
  <div
    class="select-none rounded-2xl border bg-white shadow-sm transition-colors"
    :class="[absolute ? 'absolute' : '', kindSurfaceClass, statusFrameClass, clickableClass]"
    :style="wrapperStyle"
    data-placement-card="true"
    @mousedown="handleMouseDown"
    @dragover.prevent="handleDragOver"
    @drop="handleDrop"
  >
    <div class="p-3" :class="headerClickableClass" data-card-header="true" @click="handleClick">
      <div class="flex items-start gap-3">
        <AvatarBadge
          :icon="displayIcon"
          :label="displayName"
          :size="40"
          rounded="2xl"
          text-class="text-xs font-bold"
        />
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full" :class="statusDotClass" />
            <div class="min-w-0 truncate text-sm font-semibold text-slate-800">
              {{ displayName }}
            </div>
          </div>
          <div class="mt-1 flex items-center gap-2">
            <span class="text-[11px] text-slate-400">{{ kindLabel }}</span>
            <span
              class="rounded-full px-2 py-0.5 text-[10px] font-medium"
              :class="statusBadgeClass"
            >
              {{ statusText }}
            </span>
          </div>
        </div>
        <button
          v-if="mode === 'edit'"
          class="text-sm leading-none text-slate-400 transition hover:text-rose-500"
          @click.stop="$emit('remove', placement.id)"
        >
          ×
        </button>
      </div>

      <div
        v-if="mode === 'edit' && canAcceptChildren && !renderChildren.length"
        class="mt-3 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-3 py-2 text-[11px] text-slate-500"
      >
        {{ ui.addSubordinate }}
      </div>
    </div>

    <div
      v-if="renderChildren.length"
      class="mx-3 mb-3 rounded-2xl border border-slate-100 bg-slate-50/80 p-3"
    >
      <div class="mb-3 text-[11px] font-medium text-slate-400">{{ ui.memberHierarchy }}</div>
      <div
        v-if="placement.kind === 'team'"
        class="rounded-2xl bg-white/70 px-3 py-4"
      >
        <div class="space-y-5">
          <HierarchyBranch
            v-for="child in renderChildren"
            :key="child.id"
            :placement="child"
            :mode="mode"
            @task-drop="$emit('task-drop', $event)"
            @select="$emit('select', $event)"
          />
        </div>
      </div>
      <div v-else class="grid gap-3" :class="childGridClass">
        <PlacementNode
          v-for="child in renderChildren"
          :key="child.id"
          :placement="child"
          :mode="mode"
          :absolute="false"
          @remove="$emit('remove', $event)"
          @drop-into="$emit('drop-into', $event)"
          @task-drop="$emit('task-drop', $event)"
          @select="$emit('select', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AvatarBadge from '../common/AvatarBadge.vue'
import HierarchyBranch from './HierarchyBranch.vue'
import { resolveNode } from '../../utils/tree'
import { useRuntimeStore } from '../../stores/runtime'
import { useSimuBossStore } from '../../stores/simuBoss'

const props = defineProps({
  placement: { type: Object, required: true },
  mode: { type: String, default: 'edit' },
  absolute: { type: Boolean, default: false },
})

const emit = defineEmits(['remove', 'drop-into', 'task-drop', 'select', 'start-move'])

const store = useSimuBossStore()
const runtime = useRuntimeStore()

const ui = {
  addSubordinate: '\u62d6\u62fd\u6dfb\u52a0\u4e0b\u5c5e',
  memberHierarchy: '\u6210\u5458\u5c42\u7ea7',
}

const displayName = computed(() => {
  if (props.placement.kind === 'team') {
    return store.teamMap[props.placement.refId]?.name || props.placement.name || 'Team'
  }
  return store.employeeMap[props.placement.refId]?.name || props.placement.name || 'Employee'
})

const displayIcon = computed(() => {
  if (props.placement.kind === 'team') {
    return store.teamMap[props.placement.refId]?.icon || props.placement.icon || 'TM'
  }
  return store.employeeMap[props.placement.refId]?.icon || props.placement.icon || 'EMP'
})

const kindLabel = computed(() => {
  return {
    team: '\u56e2\u961f',
    manager: '\u7ecf\u7406',
    employee: '\u5de5\u4eba',
  }[props.placement.kind] || '\u5de5\u4eba'
})

const statusState = computed(() => runtime.teamStatuses[props.placement.id]?.state || 'idle')
const statusText = computed(
  () => runtime.teamStatuses[props.placement.id]?.text || '\u7a7a\u95f2',
)

const statusDotClass = computed(() => {
  return {
    idle: 'bg-slate-300',
    working: 'bg-emerald-500',
    blocked: 'bg-amber-400',
    error: 'bg-rose-500',
  }[statusState.value]
})

const statusBadgeClass = computed(() => {
  return {
    idle: 'bg-slate-100 text-slate-500',
    working: 'bg-emerald-100 text-emerald-700',
    blocked: 'bg-amber-100 text-amber-700',
    error: 'bg-rose-100 text-rose-700',
  }[statusState.value]
})

const statusFrameClass = computed(() => {
  return {
    idle: 'border-slate-200',
    working: 'border-emerald-300 shadow-emerald-100/80',
    blocked: 'border-amber-300 shadow-amber-100/80',
    error: 'border-rose-300 shadow-rose-100/80',
  }[statusState.value]
})

const canAcceptChildren = computed(() => props.placement.kind === 'manager')
const clickableClass = computed(() =>
  props.mode === 'runtime' && props.placement.kind !== 'team' ? 'cursor-pointer' : '',
)
const headerClickableClass = computed(() => (props.mode === 'runtime' ? 'cursor-pointer' : ''))

function nextLocalId(prefix) {
  return `${prefix}-${crypto.randomUUID()}`
}

function buildTreeFromRaw(nodes, scope = 'tree', branch = 'root') {
  return (nodes || [])
    .map((rawNode, index) => {
      const node = resolveNode(rawNode, store.employees, store.teams)
      if (!node) return null
      const nodeScope = `${scope}-${branch}-${index}-${rawNode.type}-${rawNode.refId ?? node.id}`

      if (node.role === 'team') {
        return {
          id: `${nodeScope}-team`,
          kind: 'team',
          refId: node.id,
          name: node.name,
          icon: node.icon,
          children: buildTreeFromRaw(node.members || [], nodeScope, 'members'),
        }
      }

      return {
        id: `${nodeScope}-${node.role === 'manager' ? 'manager' : 'employee'}`,
        kind: node.role === 'manager' ? 'manager' : 'employee',
        refId: node.id,
        name: node.name,
        icon: node.icon,
        children: buildTreeFromRaw(rawNode.children || [], nodeScope, 'children'),
      }
    })
    .filter(Boolean)
}

const renderChildren = computed(() => {
  if (props.placement.kind === 'team') {
    const team = store.teamMap[props.placement.refId]
    return buildTreeFromRaw(team?.members || [], props.placement.id, 'team').map((item) =>
      item.kind === 'manager'
        ? {
            ...item,
            x: props.placement.x,
            y: props.placement.y,
            infoSourceId: props.placement.id,
          }
        : item,
    )
  }
  return props.placement.children || []
})

const primarySelectablePlacement = computed(() => {
  if (props.placement.kind !== 'team') return props.placement
  const managerRoot =
    renderChildren.value.find((item) => item.kind === 'manager') || renderChildren.value[0]
  if (!managerRoot) return props.placement
  return {
    ...managerRoot,
    x: props.placement.x,
    y: props.placement.y,
    infoSourceId: props.placement.id,
  }
})

const childGridClass = computed(() => {
  return 'grid-cols-[repeat(auto-fit,minmax(176px,1fr))]'
})

const wrapperStyle = computed(() => {
  const width =
    props.placement.kind === 'team' ? 560 : props.placement.kind === 'manager' ? 320 : 188
  const minHeight =
    props.placement.kind === 'team' ? 176 : props.placement.kind === 'manager' ? 132 : 88

  if (!props.absolute) {
    return {
      width: '100%',
      minHeight: `${minHeight}px`,
    }
  }

  return {
    left: `${props.placement.x}px`,
    top: `${props.placement.y}px`,
    width: `${width}px`,
    minHeight: `${minHeight}px`,
  }
})

const kindSurfaceClass = computed(() => {
  return {
    team: 'ring-1 ring-sky-100',
    manager: 'ring-1 ring-amber-100',
    employee: '',
  }[props.placement.kind]
})

function handleDragOver(event) {
  if (props.mode === 'runtime') return
  if (!canAcceptChildren.value) return
  event.preventDefault()
}

function handleDrop() {
  if (props.mode === 'runtime') {
    emit('task-drop', props.placement)
    return
  }
  if (!canAcceptChildren.value) return
  emit('drop-into', props.placement.id)
}

function handleMouseDown(event) {
  if (props.mode !== 'edit' || !props.absolute) return
  if (event.target.closest('button')) return
  emit('start-move', { event, placement: props.placement })
}

function handleClick(event) {
  if (props.mode !== 'runtime') return
  if (event.target.closest('button')) return
  if (props.placement.kind === 'team' && !event.target.closest('[data-card-header="true"]')) return
  emit('select', primarySelectablePlacement.value)
}
</script>
