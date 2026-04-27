<template>
  <div class="flex h-full min-h-0 bg-slate-100 text-slate-900">
    <section class="w-[320px] border-r border-slate-200 bg-white p-4">
      <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div class="text-lg font-semibold">团队中心</div>
        <p class="mt-2 text-xs leading-5 text-slate-500">
          这里直接在中间画布查看或编辑团队结构。保存时会自动校验 leader 规则。
        </p>
        <button
          class="mt-4 w-full rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white"
          @click="createTeam"
        >
          + 编排新团队
        </button>
      </div>

      <div class="mt-4 space-y-3">
        <div
          v-for="team in visibleTeams"
          :key="team.id"
          class="rounded-2xl border px-4 py-3 shadow-sm transition cursor-pointer"
          :class="
            selectedTeamId === team.id
              ? 'border-brand-500 bg-brand-50 text-brand-700'
              : 'border-slate-200 bg-white hover:bg-slate-50'
          "
          @click="openTeam(team.id, 'view')"
        >
          <div class="flex items-start gap-3">
            <AvatarBadge :icon="team.icon" :label="team.name" :size="42" rounded="xl" />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <div class="text-sm font-semibold text-slate-800">{{ team.name }}</div>
                <span
                  v-if="team.locked"
                  class="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700"
                >
                  市场样板
                </span>
              </div>
              <div class="mt-1 text-xs text-slate-500">
                {{ getTeamDesc(team.members, store.employees, store.teams) }}
              </div>
            </div>
          </div>
          <div class="mt-3 flex items-center gap-2 text-xs">
            <button class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50" @click.stop="openTeam(team.id, 'edit')">
              编辑结构
            </button>
            <button class="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100" @click.stop="store.cloneTeam(team.id)">
              克隆
            </button>
            <button class="rounded-md px-2 py-1 text-rose-500 hover:bg-rose-50" @click.stop="deleteTeam(team.id)">
              删除
            </button>
          </div>
        </div>
      </div>
    </section>

    <main class="flex min-w-0 flex-1 flex-col">
      <div class="border-b border-slate-200 bg-white px-6 py-4">
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex min-w-[320px] items-center overflow-hidden rounded-xl border border-slate-200 bg-white">
            <div class="border-r border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-500">
              团队
            </div>
            <input
              v-model="teamForm.name"
              :disabled="currentMode !== 'edit'"
              class="min-w-0 flex-1 px-3 py-2 text-sm font-medium outline-none disabled:bg-slate-50"
              placeholder="团队名称"
            />
          </div>

          <button
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium"
            @click="discardDraft"
            :disabled="currentMode !== 'edit'"
          >
            放弃更改
          </button>
          <button
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium"
            @click="clearCurrentTeam"
            :disabled="currentMode !== 'edit' || !draftAssignments.length"
          >
            清空团队
          </button>
          <button
            class="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-emerald-300"
            @click="saveTeam"
            :disabled="currentMode !== 'edit'"
          >
            保存团队结构
          </button>
          <div class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
            {{ currentMode === 'edit' ? '编辑模式' : '查看模式' }}
          </div>
          <div class="ml-auto flex items-center gap-2">
            <button
              class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600"
              @click="focusContent"
            >
              定位到内容
            </button>
            <div class="text-xs text-slate-500">缩放 {{ Math.round(view.scale * 100) }}%</div>
          </div>
        </div>
        <div v-if="saveError" class="mt-3 text-xs text-rose-600">{{ saveError }}</div>
      </div>

      <div class="flex min-h-0 flex-1">
        <section class="flex min-w-0 flex-1 flex-col overflow-hidden p-4">
          <div class="mb-3 flex items-center justify-between">
            <div>
              <div class="text-sm font-semibold text-slate-800">画布</div>
              <div class="mt-1 text-xs text-slate-500">
                {{ currentMode === 'edit' ? '空白区域可平移，滚轮只做小幅缩放。' : '查看模式下仅浏览团队结构。' }}
              </div>
            </div>
          </div>

          <div
            ref="viewportRef"
            class="relative min-h-0 flex-1 overflow-hidden rounded-3xl border border-slate-200 bg-white"
            @mousedown="startPan"
            @dragover.prevent="currentMode === 'edit'"
            @drop="currentMode === 'edit' && handleRootDrop($event)"
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
                    :mode="currentMode === 'edit' ? 'edit' : 'runtime'"
                    absolute
                    @remove="currentMode === 'edit' && removePlacement($event)"
                    @drop-into="currentMode === 'edit' && dropIntoNode($event)"
                    @start-move="currentMode === 'edit' && startRootMove($event)"
                  />
                </div>

                <div
                  v-if="!draftAssignments.length"
                  class="pointer-events-none absolute inset-0 flex items-center justify-center text-center text-slate-400"
                >
                  <div>
                    <div class="text-lg font-semibold">还没有团队结构</div>
                    <div class="mt-2 text-sm">
                      {{ currentMode === 'edit' ? '把右侧的经理、员工或团队拖进来就行。' : '请选择一个团队查看，或点击左侧新建。' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <aside class="flex min-h-0 w-[320px] flex-col border-l border-slate-200 bg-white p-4">
          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div class="text-sm font-semibold">{{ currentMode === 'edit' ? '组件' : '团队信息' }}</div>
            <div class="mt-1 text-xs leading-5 text-slate-500">
              {{
                currentMode === 'edit'
                  ? '和公司大楼一样，从右侧拖拽团队、经理或员工到画布。'
                  : '查看模式下只展示当前团队概况。'
              }}
            </div>
          </div>

          <div class="mt-4 min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
            <div class="rounded-2xl border border-slate-200 bg-white p-4">
              <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">团队信息</div>
              <label class="block">
                <div class="mb-1 text-xs font-medium text-slate-500">团队图标</div>
                <input
                  v-model="teamForm.icon"
                  :disabled="currentMode !== 'edit'"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none disabled:bg-slate-50"
                />
              </label>
              <div class="mt-3 rounded-xl bg-slate-50 px-3 py-3 text-xs leading-5 text-slate-500">
                {{ selectedTeam ? getTeamDesc(selectedTeam.members, store.employees, store.teams) : '新团队尚未保存' }}
              </div>
            </div>

            <template v-if="currentMode === 'edit'">
              <div>
                <button
                  class="mb-2 flex w-full items-center justify-between text-xs font-semibold tracking-[0.18em] text-slate-400"
                  @click="togglePanel('team')"
                >
                  <span>团队</span>
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
                  <span>经理</span>
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
                  <span>员工</span>
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
            </template>

            <div
              v-if="saveError && currentMode === 'edit'"
              class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
            >
              {{ saveError }}
            </div>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import AvatarBadge from '../components/common/AvatarBadge.vue'
import PlacementNode from '../components/canvas/PlacementNode.vue'
import {
  getPlacementBounds,
  getPlacementDesignHeight,
  getPlacementDesignWidth,
} from '../utils/placementBounds'
import { resolveNode } from '../utils/tree'
import { useSimuBossStore } from '../stores/simuBoss'

const GRID = 24
const WORLD_W = 12000
const WORLD_H = 12000
const WORLD_ORIGIN_X = WORLD_W / 2
const WORLD_ORIGIN_Y = WORLD_H / 2

const store = useSimuBossStore()
const selectedTeamId = ref(store.teams[0]?.id ?? null)
const currentMode = ref(store.teams.length ? 'view' : 'edit')
const viewportRef = ref(null)
const canvasContentRef = ref(null)
const dragPalette = ref(null)
const panState = ref(null)
const moveState = ref(null)
const saveError = ref('')
const view = ref({ x: 32, y: 24, scale: 1 })
const draftAssignments = ref([])
const panelOpen = ref({
  team: true,
  manager: true,
  worker: true,
})

const teamForm = reactive({
  icon: 'TEAM',
  name: '',
})

const visibleTeams = computed(() => store.teams.filter((item) => !item.hidden))
const selectedTeam = computed(() => store.teams.find((item) => item.id === selectedTeamId.value) || null)
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
  visibleTeams.value
    .filter((team) => team.id !== selectedTeamId.value)
    .map((team) => ({
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
    .filter((emp) => emp.role === 'manager' && !emp.hidden)
    .map((emp) => ({
      kind: 'manager',
      refId: emp.id,
      linkedTeamId: null,
      linkedManagerId: emp.id,
      name: emp.name,
      icon: emp.icon,
      meta: '可作为团队 leader，或继续挂下属',
      valid: true,
    })),
)

const workerPalette = computed(() =>
  store.employees
    .filter((emp) => emp.role === 'worker' && !emp.hidden)
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

function countTeamMembers(nodes) {
  return (nodes || []).reduce((total, node) => {
    const resolved = resolveNode(node, store.employees, store.teams)
    if (!resolved) return total
    if (resolved.role === 'team') {
      return total + countTeamMembers(resolved.members || [])
    }
    return total + 1 + countTeamMembers(node.children || [])
  }, 0)
}

function countManagers(nodes) {
  return (nodes || []).reduce((total, node) => {
    const resolved = resolveNode(node, store.employees, store.teams)
    if (!resolved) return total
    if (resolved.role === 'team') {
      return total + countManagers(resolved.members || [])
    }
    const selfCount = resolved.role === 'manager' ? 1 : 0
    return total + selfCount + countManagers(node.children || [])
  }, 0)
}

function getTeamDesc(members, employees, teams) {
  const managerCount = (members || []).reduce((total, node) => {
    const resolved = resolveNode(node, employees, teams)
    if (!resolved) return total
    if (resolved.role === 'team') {
      return total + countManagers(resolved.members || [])
    }
    const selfCount = resolved.role === 'manager' ? 1 : 0
    return total + selfCount + countManagers(node.children || [])
  }, 0)
  const totalCount = countTeamMembers(members || [])
  return `建制链：包含 ${managerCount} 个经理、统领 ${Math.max(totalCount - managerCount, 0)} 名员工`
}

function togglePanel(key) {
  panelOpen.value[key] = !panelOpen.value[key]
}

function nextDraftId() {
  return `team-draft-${crypto.randomUUID()}`
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
    linkedTeamId: null,
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

function placementToRawNode(placement) {
  if (!placement) return null
  return {
    type: placement.kind === 'team' ? 'team_ref' : 'emp_ref',
    refId: placement.refId,
    children: (placement.children || []).map((child) => placementToRawNode(child)).filter(Boolean),
  }
}

function loadTeamIntoCanvas(team, mode = 'view') {
  currentMode.value = mode
  saveError.value = ''
  dragPalette.value = null

  if (!team) {
    teamForm.icon = 'TEAM'
    teamForm.name = ''
    draftAssignments.value = []
    nextTick(() => fitViewportToContent())
    return
  }

  teamForm.icon = team.icon
  teamForm.name = team.name
  draftAssignments.value = buildChildrenFromNodes(team.members || []).map((item, index) => ({
    ...item,
    x: index * 48,
    y: 0,
  }))
  nextTick(() => fitViewportToContent())
}

function openTeam(id, mode = 'view') {
  const original = store.teams.find((item) => item.id === id)
  if (!original) return

  if (mode === 'edit' && original.locked) {
    const clonedId = store.cloneTeam(id)
    if (!clonedId) return
    const cloned = store.teams.find((item) => item.id === clonedId)
    selectedTeamId.value = clonedId
    loadTeamIntoCanvas(cloned, 'edit')
    return
  }

  selectedTeamId.value = id
  loadTeamIntoCanvas(original, mode)
}

function createTeam() {
  selectedTeamId.value = null
  loadTeamIntoCanvas(null, 'edit')
}

function discardDraft() {
  loadTeamIntoCanvas(selectedTeam.value, selectedTeam.value ? 'view' : 'edit')
}

function clearCurrentTeam() {
  if (currentMode.value !== 'edit') return
  draftAssignments.value = []
  saveError.value = ''
}

function validateTeamDraft() {
  if (draftAssignments.value.length !== 1) {
    return '一个团队只能有一个根节点，也就是团队 leader。'
  }
  const root = draftAssignments.value[0]
  if (root.kind !== 'manager') {
    return '团队根节点必须是经理。'
  }
  if (!(root.children || []).length) {
    return '团队 leader 下面至少需要有一名成员。'
  }
  return ''
}

function saveTeam() {
  const validationError = validateTeamDraft()
  if (validationError) {
    saveError.value = validationError
    return
  }

  const savedId = store.upsertTeam(
    {
      icon: teamForm.icon || 'TEAM',
      name: teamForm.name || '无名小队',
      members: [placementToRawNode(draftAssignments.value[0])],
    },
    selectedTeamId.value,
  )

  selectedTeamId.value = savedId
  openTeam(savedId, 'view')
}

function deleteTeam(id) {
  const deletingSelected = selectedTeamId.value === id
  store.deleteTeam(id)
  if (!deletingSelected) return
  const fallback = visibleTeams.value[0] || null
  if (fallback) {
    openTeam(fallback.id, 'view')
  } else {
    createTeam()
  }
}

function startPaletteDrag(item) {
  if (currentMode.value !== 'edit') return
  dragPalette.value = item
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

function removePlacement(id) {
  if (currentMode.value !== 'edit') return
  draftAssignments.value = removeById(draftAssignments.value, id)
}

function dropIntoNode(targetId) {
  if (currentMode.value !== 'edit' || !dragPalette.value) return
  draftAssignments.value = appendChild(
    draftAssignments.value,
    targetId,
    buildPlacementFromPalette(dragPalette.value),
  )
  dragPalette.value = null
  saveError.value = ''
}

function snap(value) {
  return Math.round(value / GRID) * GRID
}

function pointFromEvent(clientX, clientY) {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return { x: 0, y: 0 }
  const width = dragPalette.value ? getPlacementDesignWidth(dragPalette.value) : 188
  const x =
    (clientX - rect.left - view.value.x) / view.value.scale - WORLD_ORIGIN_X - width / 2
  const y =
    (clientY - rect.top - view.value.y) / view.value.scale - WORLD_ORIGIN_Y - 44
  return { x: snap(x), y: snap(y) }
}

function handleRootDrop(event) {
  if (currentMode.value !== 'edit' || !dragPalette.value) return
  const point = pointFromEvent(event.clientX, event.clientY)
  draftAssignments.value = [
    ...draftAssignments.value,
    buildPlacementFromPalette(dragPalette.value, point),
  ]
  dragPalette.value = null
  saveError.value = ''
}

function startRootMove(payload) {
  if (currentMode.value !== 'edit') return
  document.body.style.userSelect = 'none'
  moveState.value = {
    id: payload.placement.id,
    startX: payload.event.clientX,
    startY: payload.event.clientY,
    originX: payload.placement.x || 0,
    originY: payload.placement.y || 0,
  }
  window.addEventListener('mousemove', moveRoot)
  window.addEventListener('mouseup', stopRootMove, { once: true })
}

function moveRoot(event) {
  if (!moveState.value) return
  const dx = (event.clientX - moveState.value.startX) / view.value.scale
  const dy = (event.clientY - moveState.value.startY) / view.value.scale
  const point = { x: snap(moveState.value.originX + dx), y: snap(moveState.value.originY + dy) }
  draftAssignments.value = draftAssignments.value.map((item) =>
    item.id === moveState.value.id ? { ...item, ...point } : item,
  )
}

function stopRootMove() {
  moveState.value = null
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', moveRoot)
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

const contentBounds = computed(() =>
  getPlacementBounds(draftAssignments.value, {
    padding: 96,
  }),
)

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
  const bounds = contentBounds.value
  const paddedWidth = Math.max(420, bounds.width)
  const paddedHeight = Math.max(260, bounds.height)
  const fitScale = Math.min(rect.width / paddedWidth, rect.height / paddedHeight, 1)
  const nextScale = Math.max(0.42, fitScale)
  view.value = {
    scale: nextScale,
    x: rect.width / 2 - ((bounds.minX + bounds.maxX) / 2 + WORLD_ORIGIN_X) * nextScale,
    y: rect.height / 2 - ((bounds.minY + bounds.maxY) / 2 + WORLD_ORIGIN_Y) * nextScale,
  }
  clampViewport()
}

function focusContent() {
  fitViewportToContent()
}

function handleWheel(event) {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const oldScale = view.value.scale
  const fitScale = Math.min(rect.width / canvasWidth.value, rect.height / canvasHeight.value)
  const minScale = Math.min(1, Math.max(0.35, fitScale))
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

onMounted(() => {
  window.addEventListener('resize', fitViewportToContent)
  if (visibleTeams.value.length) {
    openTeam(visibleTeams.value[0].id, 'view')
  } else {
    createTeam()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', movePan)
  window.removeEventListener('resize', fitViewportToContent)
})

watch(
  draftAssignments,
  async () => {
    await nextTick()
    fitViewportToContent()
  },
  { deep: true },
)
</script>
