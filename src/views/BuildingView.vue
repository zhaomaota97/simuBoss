<template>
  <div class="flex h-full min-h-0 bg-slate-100 text-slate-900">
    <div class="pointer-events-none fixed right-6 top-20 z-50 flex w-[320px] flex-col gap-3">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="rounded-2xl border px-4 py-3 shadow-lg backdrop-blur"
        :class="
          toast.type === 'success'
            ? 'border-emerald-200 bg-white/95 text-emerald-700'
            : toast.type === 'error'
              ? 'border-rose-200 bg-white/95 text-rose-700'
              : 'border-slate-200 bg-white/95 text-slate-700'
        "
      >
        <div class="text-sm font-semibold">{{ toast.title }}</div>
        <div v-if="toast.message" class="mt-1 text-xs leading-5 text-slate-500">{{ toast.message }}</div>
      </div>
    </div>

    <aside class="w-[280px] border-r border-slate-200 bg-white p-4">
      <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div class="text-lg font-semibold">{{ ui.title }}</div>
        <p class="mt-2 text-xs leading-5 text-slate-500">{{ ui.desc }}</p>
        <button
          class="mt-4 w-full rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white"
          @click="addFloorAndToast"
        >
          {{ ui.addFloor }}
        </button>
      </div>

      <div class="mt-4 space-y-3">
        <button
          v-for="floor in store.floors"
          :key="floor.id"
          class="block w-full rounded-2xl border px-4 py-3 text-left shadow-sm transition"
          :class="
            selectedFloorId === floor.id
              ? 'border-brand-500 bg-brand-50 text-brand-700'
              : 'border-slate-200 bg-white hover:bg-slate-50'
          "
          @click="selectedFloorId = floor.id"
        >
          <div class="font-semibold">{{ getFloorLabel(floor.id) }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ getSavedCount(floor.id) }}{{ ui.savedCount }}</div>
        </button>
      </div>
    </aside>

    <main class="flex min-w-0 flex-1 flex-col">
      <div class="border-b border-slate-200 bg-white px-6 py-4">
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex min-w-[320px] items-center overflow-hidden rounded-xl border border-slate-200 bg-white">
            <div class="border-r border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-500">
              {{ selectedFloorLabelPrefix }}
            </div>
            <input
              :value="selectedFloor?.name || ''"
              class="min-w-0 flex-1 px-3 py-2 text-sm font-medium outline-none focus:border-brand-500"
              :placeholder="ui.floorName"
              @change="store.updateFloorName(selectedFloorId, $event.target.value)"
            />
          </div>
          <button
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium"
            @click="discardDraft"
            :disabled="!isDirty"
          >
            {{ ui.discard }}
          </button>
          <button
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium"
            @click="clearCurrentFloor"
            :disabled="!draftAssignments.length"
          >
            {{ ui.clearFloor }}
          </button>
          <button
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:text-slate-300"
            @click="autoArrangeFloor"
            :disabled="!draftAssignments.length"
          >
            {{ ui.autoArrange }}
          </button>
          <button
            class="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-emerald-300"
            @click="saveFloor"
          >
            {{ ui.save }}
          </button>
          <button
            v-if="store.floors.length > 1"
            class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-600"
            @click="removeCurrentFloor"
          >
            {{ ui.deleteFloor }}
          </button>
          <div class="ml-auto text-xs text-slate-500">
            {{ isDirty ? ui.unsaved : ui.saved }}
          </div>
        </div>
        <div v-if="saveError" class="mt-3 text-xs text-rose-600">{{ saveError }}</div>
      </div>

      <div class="flex min-h-0 flex-1">
        <section class="flex min-w-0 flex-1 flex-col overflow-hidden p-4">
          <div class="mb-3 flex items-center justify-between">
            <div>
              <div class="text-sm font-semibold text-slate-800">{{ ui.canvasTitle }}</div>
              <div class="mt-1 text-xs text-slate-500">{{ ui.canvasHint }}</div>
            </div>
            <div class="flex items-center gap-2">
              <button
                class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600"
                @click="focusContentAndToast"
              >
                {{ ui.focusContent }}
              </button>
              <div class="text-xs text-slate-500">{{ ui.zoom }} {{ Math.round(view.scale * 100) }}%</div>
            </div>
          </div>

          <div
            ref="viewportRef"
            class="relative min-h-0 flex-1 overflow-hidden rounded-3xl border border-slate-200 bg-white"
            @mousedown="startPan"
            @dragover.prevent
            @drop="handleRootDrop"
            @wheel.prevent="handleWheel"
          >
            <div class="absolute inset-0" :style="worldStyle">
              <div
                class="relative bg-[radial-gradient(circle_at_1px_1px,#cbd5e1_1.2px,transparent_0)] bg-[length:24px_24px] bg-white"
                :style="{ width: `${canvasWidth}px`, height: `${canvasHeight}px` }"
              >
                <div ref="canvasContentRef" class="absolute inset-0" :style="canvasOffsetStyle">
                  <PlacementNode
                    v-for="placement in draftAssignments"
                    :key="placement.id"
                    :placement="placement"
                    mode="edit"
                    absolute
                    @remove="removePlacement"
                    @drop-into="dropIntoNode"
                    @start-move="startRootMove"
                  />
                </div>

                <div
                  v-if="!draftAssignments.length"
                  class="pointer-events-none absolute inset-0 flex items-center justify-center text-center text-slate-400"
                >
                  <div>
                    <div class="text-lg font-semibold">{{ ui.empty }}</div>
                    <div class="mt-2 text-sm">{{ ui.emptyHint }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <aside class="flex min-h-0 w-[320px] flex-col border-l border-slate-200 bg-white p-4">
          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div class="text-sm font-semibold">{{ ui.paletteTitle }}</div>
            <div class="mt-1 text-xs leading-5 text-slate-500">{{ ui.paletteHint }}</div>
          </div>

          <div class="mt-4 min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
            <div>
              <button
                class="mb-2 flex w-full items-center justify-between text-xs font-semibold tracking-[0.18em] text-slate-400"
                @click="togglePanel('team')"
              >
                <span>{{ ui.teamSection }}</span>
                <span>{{ panelOpen.team ? '−' : '+' }}</span>
              </button>
              <div v-if="panelOpen.team" class="space-y-2">
                <div
                  v-for="item in teamPalette"
                  :key="`team-${item.refId}`"
                  class="cursor-grab rounded-xl border border-slate-200 bg-white px-3 py-3 shadow-sm"
                  draggable="true"
                  @dragstart="startPaletteDrag(item)"
                >
                  <div class="flex items-center gap-2 truncate text-sm font-semibold text-slate-800">
                    <AvatarBadge :icon="item.icon" :label="item.name" :size="28" rounded="xl" text-class="text-xs font-semibold" />
                    <span class="truncate">{{ item.name }}</span>
                  </div>
                  <div class="mt-1 text-xs text-slate-500">{{ item.meta }}</div>
                </div>
              </div>
            </div>

            <div>
              <button
                class="mb-2 flex w-full items-center justify-between text-xs font-semibold tracking-[0.18em] text-slate-400"
                @click="togglePanel('manager')"
              >
                <span>{{ ui.managerSection }}</span>
                <span>{{ panelOpen.manager ? '−' : '+' }}</span>
              </button>
              <div v-if="panelOpen.manager" class="space-y-2">
                <div
                  v-for="item in managerPalette"
                  :key="`manager-${item.refId}`"
                  class="cursor-grab rounded-xl border px-3 py-3 shadow-sm"
                  :class="item.valid ? 'border-slate-200 bg-white' : 'border-amber-200 bg-amber-50'"
                  draggable="true"
                  @dragstart="startPaletteDrag(item)"
                >
                  <div class="flex items-center gap-2 truncate text-sm font-semibold text-slate-800">
                    <AvatarBadge :icon="item.icon" :label="item.name" :size="28" rounded="xl" text-class="text-xs font-semibold" />
                    <span class="truncate">{{ item.name }}</span>
                  </div>
                  <div class="mt-1 text-xs text-slate-500">{{ item.meta }}</div>
                </div>
              </div>
            </div>

            <div>
              <button
                class="mb-2 flex w-full items-center justify-between text-xs font-semibold tracking-[0.18em] text-slate-400"
                @click="togglePanel('worker')"
              >
                <span>{{ ui.workerSection }}</span>
                <span>{{ panelOpen.worker ? '−' : '+' }}</span>
              </button>
              <div v-if="panelOpen.worker" class="space-y-2">
                <div
                  v-for="item in workerPalette"
                  :key="`worker-${item.refId}`"
                  class="cursor-grab rounded-xl border border-slate-200 bg-white px-3 py-3 shadow-sm"
                  draggable="true"
                  @dragstart="startPaletteDrag(item)"
                >
                  <div class="flex items-center gap-2 truncate text-sm font-semibold text-slate-800">
                    <AvatarBadge :icon="item.icon" :label="item.name" :size="28" rounded="xl" text-class="text-xs font-semibold" />
                    <span class="truncate">{{ item.name }}</span>
                  </div>
                  <div class="mt-1 text-xs text-slate-500">{{ item.meta }}</div>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AvatarBadge from '../components/common/AvatarBadge.vue'
import PlacementNode from '../components/canvas/PlacementNode.vue'
import {
  getPlacementBounds,
  getPlacementDesignHeight,
  getPlacementDesignWidth,
} from '../utils/placementBounds'
import { cloneDeep, resolveNode } from '../utils/tree'
import { useSimuBossStore } from '../stores/simuBoss'

const GRID = 24
const WORLD_W = 12000
const WORLD_H = 12000
const WORLD_ORIGIN_X = WORLD_W / 2
const WORLD_ORIGIN_Y = WORLD_H / 2

const ui = {
  title: '\u516c\u53f8\u5927\u697c',
  desc: '\u53f3\u4fa7\u62d6\u62fd\u8fdb\u753b\u5e03\u53ef\u751f\u6210\u6839\u8282\u70b9\uff0c\u62d6\u5230\u7ecf\u7406/\u56e2\u961f\u5361\u7247\u5185\u53ef\u6302\u5230\u8fd9\u4e2a\u5c42\u7ea7\u4e0b\u3002',
  addFloor: '+ \u65b0\u589e\u697c\u5c42',
  savedCount: '\u540d\u5458\u5de5',
  floorName: '\u90e8\u95e8\u540d\u79f0',
  discard: '\u653e\u5f03\u66f4\u6539',
  clearFloor: '\u6e05\u7a7a\u672c\u5c42',
  autoArrange: '\u4e00\u952e\u6392\u5217',
  save: '\u4fdd\u5b58\u5e03\u7f6e',
  deleteFloor: '\u5220\u9664\u697c\u5c42',
  unsaved: '\u6709\u672a\u4fdd\u5b58\u53d8\u66f4',
  saved: '\u5df2\u4e0e\u9996\u9875\u540c\u6b65',
  canvasTitle: '\u753b\u5e03',
  canvasHint: '\u7a7a\u767d\u533a\u53ef\u5e73\u79fb\uff0c\u6eda\u8f6e\u53ea\u505a\u5c0f\u5e45\u7f29\u653e\u3002',
  focusContent: '\u5b9a\u4f4d\u5230\u5185\u5bb9',
  zoom: '\u7f29\u653e',
  empty: '\u8fd8\u6ca1\u6709\u4efb\u4f55\u5e03\u7f6e',
  emptyHint: '\u628a\u53f3\u4fa7\u7684\u56e2\u961f\u3001\u7ecf\u7406\u6216\u5458\u5de5\u62d6\u8fdb\u6765\u5c31\u884c\u3002',
  paletteTitle: '\u7ec4\u4ef6',
  paletteHint: '\u7ecf\u7406/\u56e2\u961f\u4f1a\u4ee5\u5b8c\u6574\u6811\u5f62\u7ed3\u6784\u5c55\u5f00\uff0c\u4e5f\u53ef\u4ee5\u7ee7\u7eed\u5f80\u91cc\u9762\u6302\u3002',
  teamSection: '\u56e2\u961f',
  managerSection: '\u7ecf\u7406',
  workerSection: '\u5458\u5de5',
  invalidManager: '\u5b58\u5728\u6ca1\u6709\u4e0b\u5c5e\u7684\u7ecf\u7406\uff0c\u6682\u65f6\u4e0d\u80fd\u4fdd\u5b58',
  invalidTeam: '\u5b58\u5728\u76f4\u63a5\u5b50\u8282\u70b9\u4e0d\u8db3 2 \u4e2a\u7684\u56e2\u961f\uff0c\u6682\u65f6\u4e0d\u80fd\u4fdd\u5b58',
}

const store = useSimuBossStore()
const selectedFloorId = ref(store.floors[0]?.id || 'floor-1')
const viewportRef = ref(null)
const canvasContentRef = ref(null)
const dragPalette = ref(null)
const panState = ref(null)
const moveState = ref(null)
const saveError = ref('')
const toasts = ref([])
const view = ref({ x: 32, y: 24, scale: 1 })
const draftMap = ref(cloneDeep(store.floorAssignments))
const panelOpen = ref({
  team: true,
  manager: true,
  worker: true,
})

watch(
  () => store.floors.map((item) => item.id),
  (ids) => {
    ids.forEach((id) => {
      if (!draftMap.value[id]) draftMap.value[id] = cloneDeep(store.floorAssignments[id] || [])
    })
    Object.keys(draftMap.value).forEach((id) => {
      if (!ids.includes(id)) delete draftMap.value[id]
    })
  },
  { immediate: true },
)

const selectedFloor = computed(() => store.floors.find((item) => item.id === selectedFloorId.value))
const selectedFloorLabelPrefix = computed(() => {
  const index = store.floors.findIndex((item) => item.id === selectedFloorId.value)
  return index === -1 ? '\u697c\u5c42' : `${index + 1}\u5c42`
})
const savedAssignments = computed(() => store.floorAssignments[selectedFloorId.value] || [])
const draftAssignments = computed({
  get: () => draftMap.value[selectedFloorId.value] || [],
  set: (value) => {
    draftMap.value[selectedFloorId.value] = value
  },
})
const isDirty = computed(
  () => JSON.stringify(draftAssignments.value) !== JSON.stringify(savedAssignments.value),
)

function pushToast(title, message = '', type = 'info') {
  const id = crypto.randomUUID()
  toasts.value.push({ id, title, message, type })
  window.setTimeout(() => {
    toasts.value = toasts.value.filter((item) => item.id !== id)
  }, 2200)
}

function addFloorAndToast() {
  selectedFloorId.value = store.addFloor()
  pushToast('已新增楼层', '可以继续编辑名称并拖入新的组织节点。', 'success')
}

function focusContentAndToast() {
  fitViewportToContent()
  pushToast('已定位到内容', '画布视角已经重新对准当前楼层内容。')
}

function togglePanel(key) {
  panelOpen.value[key] = !panelOpen.value[key]
  const labels = {
    team: ui.teamSection,
    manager: ui.managerSection,
    worker: ui.workerSection,
  }
  pushToast(panelOpen.value[key] ? '已展开面板' : '已收起面板', labels[key] || '')
}
const contentBounds = computed(() =>
  getPlacementBounds(draftAssignments.value, {
    padding: 96,
  }),
)
const canvasWidth = computed(() => WORLD_W)
const canvasHeight = computed(() => WORLD_H)
const canvasOffsetStyle = computed(() => ({
  transform: `translate(${WORLD_ORIGIN_X}px, ${WORLD_ORIGIN_Y}px)`,
  transformOrigin: '0 0',
}))
const worldStyle = computed(() => ({
  transform: `translate(${view.value.x}px, ${view.value.y}px) scale(${view.value.scale})`,
  transformOrigin: '0 0',
}))

const teamPalette = computed(() =>
  store.teams.map((team) => ({
    kind: 'team',
    refId: team.id,
    linkedTeamId: team.id,
    linkedManagerId: null,
    name: team.name,
    icon: team.icon,
    meta: '拖入后展开完整团队',
  })),
)

const managerPalette = computed(() =>
  store.employees
    .filter((emp) => emp.role === 'manager')
    .map((emp) => ({
      kind: 'manager',
      refId: emp.id,
      linkedTeamId: getManagerBinding(emp.id),
      linkedManagerId: emp.id,
      name: emp.name,
      icon: emp.icon,
      meta: getManagerBinding(emp.id) ? '拖入后展开直属层级' : ui.invalidManager,
      valid: Boolean(getManagerBinding(emp.id)),
    })),
)

const workerPalette = computed(() =>
  store.employees
    .filter((emp) => emp.role === 'worker')
    .map((emp) => ({
      kind: 'employee',
      refId: emp.id,
      linkedTeamId: null,
      linkedManagerId: null,
      name: emp.name,
      icon: emp.icon,
      meta: '单点执行单元',
    })),
)

function getFloorLabel(floorId) {
  const index = store.floors.findIndex((item) => item.id === floorId)
  const floor = store.floors[index]
  if (!floor) return ''
  return `${index + 1}\u5c42 - ${String(floor.name || '').trim()}`
}

function getSavedCount(floorId) {
  return (store.floorAssignments[floorId] || []).length
}

function nextDraftId() {
  return `draft-${crypto.randomUUID()}`
}

function hasManagerInRawNodes(nodes, managerId) {
  for (const rawNode of nodes || []) {
    const node = resolveNode(rawNode, store.employees, store.teams)
    if (!node) continue
    if (node.role === 'manager' && node.id === managerId) return true
    if (rawNode.children?.length && hasManagerInRawNodes(rawNode.children, managerId)) return true
    if (rawNode.type === 'team_ref' && hasManagerInRawNodes(node.members || [], managerId)) return true
  }
  return false
}

function getManagerBinding(managerId) {
  for (const team of store.teams) {
    if (hasManagerInRawNodes(team.members || [], managerId)) return team.id
  }
  return null
}

function buildPlacementFromResolved(node, rawNode = null) {
  if (!node) return null

  if (node.role === 'team') {
    return {
      id: nextDraftId(),
      kind: 'team',
      refId: node.id,
      linkedTeamId: node.id,
      linkedManagerId: null,
      name: node.name,
      icon: node.icon,
      children: buildChildrenFromNodes(node.members || []),
    }
  }

  const childrenSource = rawNode?.children || []
  const kind = node.role === 'manager' ? 'manager' : 'employee'
  return {
    id: nextDraftId(),
    kind,
    refId: node.id,
    linkedTeamId: kind === 'manager' ? getManagerBinding(node.id) : null,
    linkedManagerId: kind === 'manager' ? node.id : null,
    name: node.name,
    icon: node.icon,
    children: buildChildrenFromNodes(childrenSource),
  }
}

function buildChildrenFromNodes(nodes) {
  return (nodes || [])
    .map((rawNode) => buildPlacementFromResolved(resolveNode(rawNode, store.employees, store.teams), rawNode))
    .filter(Boolean)
}

function buildPlacementFromPalette(item, point = null) {
  let children = []
  if (item.kind === 'team') {
    const team = store.teamMap[item.refId]
    children = buildChildrenFromNodes(team?.members || [])
  }

  return {
    id: nextDraftId(),
    kind: item.kind,
    refId: item.refId,
    linkedTeamId: item.linkedTeamId || null,
    linkedManagerId: item.linkedManagerId || null,
    name: item.name,
    icon: item.icon,
    x: point?.x ?? 0,
    y: point?.y ?? 0,
    children,
  }
}

function snap(value) {
  return Math.round(value / GRID) * GRID
}

function rootWidth(item) {
  return getPlacementDesignWidth(item)
}

function estimateRootHeight(item) {
  return getPlacementDesignHeight(item)
}

function getRenderedRootMetrics() {
  const rootElements = Array.from(canvasContentRef.value?.children || [])

  return draftAssignments.value.map((item, index) => {
    const el = rootElements[index]
    return {
      width: Math.max(rootWidth(item), el?.offsetWidth || 0),
      height: Math.max(estimateRootHeight(item), el?.offsetHeight || 0),
    }
  })
}

function clampRoot(x, y, item) {
  return {
    x: snap(x),
    y: snap(y),
  }
}

function pointFromEvent(clientX, clientY) {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return { x: 0, y: 0 }
  const width = dragPalette.value ? rootWidth(dragPalette.value) : 188
  const x =
    (clientX - rect.left - view.value.x) / view.value.scale - WORLD_ORIGIN_X - width / 2
  const y =
    (clientY - rect.top - view.value.y) / view.value.scale - WORLD_ORIGIN_Y - 44
  return clampRoot(x, y, dragPalette.value || { kind: 'employee' })
}

function appendChild(list, targetId, child) {
  return list.map((item) => {
    if (item.id === targetId) {
      return { ...item, children: [...(item.children || []), child] }
    }
    if (item.children?.length) {
      return { ...item, children: appendChild(item.children, targetId, child) }
    }
    return item
  })
}

function removeById(list, targetId) {
  return list
    .filter((item) => item.id !== targetId)
    .map((item) => ({
      ...item,
      children: item.children?.length ? removeById(item.children, targetId) : [],
    }))
}

function validateNodes(list) {
  for (const item of list) {
    if (item.kind === 'manager' && !(item.children || []).length) {
      return ui.invalidManager
    }
    const childError = validateNodes(item.children || [])
    if (childError) return childError
  }
  return ''
}

function startPaletteDrag(item) {
  dragPalette.value = item
}

function handleRootDrop(event) {
  if (!dragPalette.value) return
  const point = pointFromEvent(event.clientX, event.clientY)
  draftAssignments.value = [
    ...draftAssignments.value,
    buildPlacementFromPalette(dragPalette.value, point),
  ]
  dragPalette.value = null
  saveError.value = ''
}

function startRootMove(payload) {
  document.body.style.userSelect = 'none'
  moveState.value = {
    id: payload.placement.id,
    startX: payload.event.clientX,
    startY: payload.event.clientY,
    originX: payload.placement.x || 0,
    originY: payload.placement.y || 0,
    kind: payload.placement.kind,
  }
  window.addEventListener('mousemove', moveRoot)
  window.addEventListener('mouseup', stopRootMove, { once: true })
}

function moveRoot(event) {
  if (!moveState.value) return
  const dx = (event.clientX - moveState.value.startX) / view.value.scale
  const dy = (event.clientY - moveState.value.startY) / view.value.scale
  const point = clampRoot(
    moveState.value.originX + dx,
    moveState.value.originY + dy,
    { kind: moveState.value.kind },
  )
  draftAssignments.value = draftAssignments.value.map((item) =>
    item.id === moveState.value.id ? { ...item, ...point } : item,
  )
}

function stopRootMove() {
  moveState.value = null
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', moveRoot)
}

function dropIntoNode(targetId) {
  if (!dragPalette.value) return
  draftAssignments.value = appendChild(
    draftAssignments.value,
    targetId,
    buildPlacementFromPalette(dragPalette.value),
  )
  dragPalette.value = null
  saveError.value = ''
}

function removePlacement(id) {
  draftAssignments.value = removeById(draftAssignments.value, id)
}

function discardDraft() {
  draftAssignments.value = cloneDeep(savedAssignments.value)
  saveError.value = ''
  pushToast('已放弃更改', '当前楼层恢复到上次保存的布局。')
}

function clearCurrentFloor() {
  draftAssignments.value = []
  saveError.value = ''
  pushToast('已清空本层', '当前楼层的草稿布局已清空。')
}

function autoArrangeFloor() {
  if (!draftAssignments.value.length) return

  const horizontalGap = 40
  const verticalGap = 40
  const renderedMetrics = getRenderedRootMetrics()
  const sortedItems = [...draftAssignments.value].sort((a, b) => {
    const aIndex = draftAssignments.value.findIndex((item) => item.id === a.id)
    const bIndex = draftAssignments.value.findIndex((item) => item.id === b.id)
    const aWidth = renderedMetrics[aIndex]?.width || rootWidth(a)
    const aHeight = renderedMetrics[aIndex]?.height || estimateRootHeight(a)
    const bWidth = renderedMetrics[bIndex]?.width || rootWidth(b)
    const bHeight = renderedMetrics[bIndex]?.height || estimateRootHeight(b)
    const areaDiff = bWidth * bHeight - aWidth * aHeight
    if (areaDiff) return areaDiff
    const kindOrder = { team: 0, manager: 1, employee: 2 }
    const kindDiff = (kindOrder[a.kind] ?? 9) - (kindOrder[b.kind] ?? 9)
    if (kindDiff) return kindDiff
    return (a.name || '').localeCompare(b.name || '', 'zh-Hans-CN')
  })

  const metricById = Object.fromEntries(
    draftAssignments.value.map((item, index) => [
      item.id,
      renderedMetrics[index] || {
        width: rootWidth(item),
        height: estimateRootHeight(item),
      },
    ]),
  )
  const getItemWidth = (item) => metricById[item.id]?.width || rootWidth(item)
  const getItemHeight = (item) => metricById[item.id]?.height || estimateRootHeight(item)

  const maxItemWidth = Math.max(...sortedItems.map((item) => getItemWidth(item)))
  const totalArea = sortedItems.reduce(
    (sum, item) => sum + (getItemWidth(item) + horizontalGap) * (getItemHeight(item) + verticalGap),
    0,
  )

  const candidateWidths = Array.from({ length: 7 }, (_, index) =>
    snap(
      Math.max(
        maxItemWidth,
        Math.min(2200, Math.sqrt(totalArea) * (0.9 + index * 0.12)),
      ),
    ),
  )

  function buildRows(targetWidth) {
    const rows = []
    let currentRow = []
    let currentWidth = 0

    sortedItems.forEach((item) => {
      const itemWidth = getItemWidth(item)
      const nextWidth = currentRow.length ? currentWidth + horizontalGap + itemWidth : itemWidth
      if (currentRow.length && nextWidth > targetWidth) {
        rows.push(currentRow)
        currentRow = [item]
        currentWidth = itemWidth
        return
      }
      currentRow.push(item)
      currentWidth = nextWidth
    })

    if (currentRow.length) rows.push(currentRow)
    return rows
  }

  function measureRows(rows) {
    const rowMetrics = rows.map((row) => {
      const width = row.reduce((sum, item) => sum + getItemWidth(item), 0) + horizontalGap * Math.max(0, row.length - 1)
      const height = Math.max(...row.map((item) => getItemHeight(item)))
      return { row, width, height }
    })
    const width = Math.max(...rowMetrics.map((item) => item.width))
    const height = rowMetrics.reduce((sum, item) => sum + item.height, 0) + verticalGap * Math.max(0, rowMetrics.length - 1)
    return { rowMetrics, width, height }
  }

  let bestLayout = null

  candidateWidths.forEach((targetWidth) => {
    const layout = measureRows(buildRows(targetWidth))
    const aspect = layout.width / Math.max(layout.height, 1)
    const aspectPenalty = Math.abs(aspect - 1.18)
    const rowPenalty = Math.max(0, layout.rowMetrics.length - 1) * 0.08
    const widthPenalty = layout.width / 5000
    const score = aspectPenalty + rowPenalty + widthPenalty

    if (!bestLayout || score < bestLayout.score) {
      bestLayout = { ...layout, score }
    }
  })

  let cursorY = -bestLayout.height / 2
  const arranged = []

  bestLayout.rowMetrics.forEach(({ row, width, height }) => {
    let cursorX = -width / 2
    row.forEach((item) => {
      arranged.push({
        ...item,
        x: cursorX,
        y: cursorY,
      })
      cursorX += getItemWidth(item) + horizontalGap
    })
    cursorY += height + verticalGap
  })

  draftAssignments.value = arranged.map((item) => {
    const point = clampRoot(item.x, item.y, item)
    return { ...item, ...point }
  })
  saveError.value = ''
  nextTick(() => {
    fitViewportToContent()
  })
  pushToast('已完成排列', '卡片已经重新整理，并自动居中到当前视口。', 'success')
}

function saveFloor() {
  const error = validateNodes(draftAssignments.value)
  saveError.value = error
  if (error) {
    pushToast('保存失败', error, 'error')
    return
  }
  store.setFloorAssignments(selectedFloorId.value, draftAssignments.value)
  pushToast('保存成功', '首页画布已同步当前楼层布局。', 'success')
}

function removeCurrentFloor() {
  const current = selectedFloorId.value
  const currentName = selectedFloor.value?.name || '当前楼层'
  const fallback = store.floors.find((item) => item.id !== current)?.id
  store.removeFloor(current)
  delete draftMap.value[current]
  selectedFloorId.value = fallback || store.floors[0]?.id || 'floor-1'
  pushToast('已删除楼层', `${currentName} 已从大楼设计中移除。`, 'success')
}

function startPan(event) {
  if (event.target?.closest?.('[data-placement-card="true"]')) return
  panState.value = {
    startX: event.clientX,
    startY: event.clientY,
    originX: view.value.x,
    originY: view.value.y,
  }
  window.addEventListener('mousemove', movePan)
  window.addEventListener('mouseup', stopPan, { once: true })
}

function movePan(event) {
  if (!panState.value) return
  view.value = {
    ...view.value,
    x: panState.value.originX + (event.clientX - panState.value.startX),
    y: panState.value.originY + (event.clientY - panState.value.startY),
  }
  clampViewport()
}

function stopPan() {
  panState.value = null
  window.removeEventListener('mousemove', movePan)
}

function handleWheel(event) {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const oldScale = view.value.scale
  const fitScale = Math.min(rect.width / canvasWidth.value, rect.height / canvasHeight.value)
  const minScale = Math.min(1, Math.max(0.6, fitScale))
  const nextScale = Math.min(1.12, Math.max(minScale, oldScale * (event.deltaY > 0 ? 0.98 : 1.02)))
  const px = event.clientX - rect.left
  const py = event.clientY - rect.top
  const wx = (px - view.value.x) / oldScale
  const wy = (py - view.value.y) / oldScale
  view.value = {
    scale: nextScale,
    x: px - wx * nextScale,
    y: py - wy * nextScale,
  }
  clampViewport()
}

function clampViewport() {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const scaledWidth = canvasWidth.value * view.value.scale
  const scaledHeight = canvasHeight.value * view.value.scale
  const minX = scaledWidth <= rect.width ? (rect.width - scaledWidth) / 2 : rect.width - scaledWidth
  const maxX = scaledWidth <= rect.width ? minX : 0
  const minY = scaledHeight <= rect.height ? (rect.height - scaledHeight) / 2 : rect.height - scaledHeight
  const maxY = scaledHeight <= rect.height ? minY : 0
  view.value = {
    ...view.value,
    x: Math.min(maxX, Math.max(minX, view.value.x)),
    y: Math.min(maxY, Math.max(minY, view.value.y)),
  }
}

function fitViewportToContent() {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const fitScale = Math.min(rect.width / contentBounds.value.width, rect.height / contentBounds.value.height, 1)
  const nextScale = Math.max(0.42, fitScale)
  view.value = {
    scale: nextScale,
    x: rect.width / 2 - (contentBounds.value.minX + contentBounds.value.maxX) / 2 * nextScale - WORLD_ORIGIN_X * nextScale,
    y: rect.height / 2 - (contentBounds.value.minY + contentBounds.value.maxY) / 2 * nextScale - WORLD_ORIGIN_Y * nextScale,
  }
  clampViewport()
}

onBeforeUnmount(() => {
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', movePan)
  window.removeEventListener('mousemove', moveRoot)
  window.removeEventListener('resize', fitViewportToContent)
})

onMounted(() => {
  window.addEventListener('resize', fitViewportToContent)
  nextTick(() => fitViewportToContent())
})

watch(selectedFloorId, async () => {
  await nextTick()
  fitViewportToContent()
})
</script>
