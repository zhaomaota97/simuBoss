<template>
  <div class="flex flex-col items-center">
    <div
      class="w-full min-w-[176px] max-w-[220px] select-none rounded-xl border bg-white shadow-sm transition-colors"
      :class="[frameClass, clickableClass]"
      data-placement-card="true"
      :data-entity-id="placement.id"
      :data-ref-id="placement.refId || undefined"
      :data-info-source-id="placement.infoSourceId || undefined"
      @click="handleClick"
      @dragover.prevent="handleDragOver"
      @drop="handleDrop"
    >
      <div class="p-3">
        <div class="flex items-start gap-3">
        <AvatarBadge
          :icon="displayIcon"
          :label="displayName"
          :size="36"
          rounded="2xl"
          text-class="text-[11px] font-bold"
        />
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <span class="h-2 w-2 rounded-full" :class="statusDotClass" />
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
        </div>
      </div>
    </div>

    <div v-if="children.length" class="mt-3 flex w-full flex-col items-center">
      <div class="h-4 w-px bg-slate-200" />
      <div class="relative flex w-full justify-center px-3">
        <div
          v-if="children.length > 1"
          class="absolute left-10 right-10 top-0 h-px bg-slate-200"
        />
        <div class="flex flex-wrap justify-center gap-x-3 gap-y-4 pt-4">
          <div
            v-for="child in children"
            :key="child.id"
            class="relative flex flex-col items-center"
          >
            <div
              v-if="child.children?.length"
              class="absolute left-1/2 top-0 h-4 w-px -translate-x-1/2 bg-slate-200"
            />
            <HierarchyBranch
              :placement="child"
              :mode="mode"
              @task-drop="$emit('task-drop', $event)"
              @select="$emit('select', $event)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AvatarBadge from '../common/AvatarBadge.vue'
import { useRuntimeStore } from '../../stores/runtime'
import { useSimuBossStore } from '../../stores/simuBoss'

defineOptions({ name: 'HierarchyBranch' })

const props = defineProps({
  placement: { type: Object, required: true },
  mode: { type: String, default: 'edit' },
})

const emit = defineEmits(['task-drop', 'select'])

const store = useSimuBossStore()
const runtime = useRuntimeStore()

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

const children = computed(() => props.placement.children || [])
const workerStatusKeys = computed(() => [...new Set([props.placement.id, props.placement.refId].filter(Boolean))])
const activeWorkerState = computed(
  () => workerStatusKeys.value.map((key) => runtime.workerStates[key]).find((item) => item?.isWorking) || null,
)
const activeTeamStatus = computed(
  () =>
    workerStatusKeys.value
      .map((key) => runtime.teamStatuses[key])
      .find((item) => item && item.state && item.state !== 'idle') ||
    workerStatusKeys.value.map((key) => runtime.teamStatuses[key]).find(Boolean) ||
    null,
)
const statusState = computed(() => {
  if (activeWorkerState.value?.isWorking) {
    return 'working'
  }
  if (activeTeamStatus.value?.state) {
    return activeTeamStatus.value.state
  }
  return 'idle'
})
const statusText = computed(() => {
  if (activeWorkerState.value?.isWorking) {
    return activeTeamStatus.value?.text || '执行中'
  }
  if (activeTeamStatus.value?.text) {
    return activeTeamStatus.value.text
  }
  return '\u7a7a\u95f2'
})

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

const frameClass = computed(() => {
  const roleClass = {
    team: 'border-sky-200',
    manager: 'border-amber-200',
    employee: 'border-slate-200',
  }[props.placement.kind]

  const stateClass = {
    idle: '',
    working: 'shadow-emerald-100/80',
    blocked: 'shadow-amber-100/80',
    error: 'shadow-rose-100/80',
  }[statusState.value]

  return `${roleClass} ${stateClass}`.trim()
})

const clickableClass = computed(() => (props.mode === 'runtime' ? 'cursor-pointer' : ''))

function handleDragOver(event) {
  if (props.mode !== 'runtime') return
  event.preventDefault()
}

function handleDrop() {
  if (props.mode !== 'runtime') return
  emit('task-drop', props.placement)
}

function handleClick(event) {
  if (props.mode !== 'runtime') return
  if (event.target.closest('button')) return
  emit('select', props.placement)
}
</script>
