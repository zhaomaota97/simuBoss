<template>
  <div class="flex h-full min-h-0 gap-5 p-5">
    <section class="panel flex min-h-0 min-w-0 flex-[1.35] flex-col">
      <div class="panel-header">
        <span>团队中心</span>
        <button class="rounded-lg bg-brand-500 px-3 py-2 text-xs font-semibold text-white" @click="openTeamStudio()">
          + 编排新团队
        </button>
      </div>
      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div
          v-if="!store.teams.length"
          class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-12 text-center text-sm text-slate-400"
        >
          还没有团队，先把经理和员工组织起来吧。
        </div>
        <div v-for="team in store.teams" :key="team.id" class="mb-4 rounded-2xl border border-slate-200 bg-white p-4 last:mb-0">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-center gap-3">
              <AvatarBadge :icon="team.icon" :label="team.name" :size="44" rounded="xl" />
              <div>
                <div class="text-sm font-semibold text-slate-800">{{ team.name }}</div>
                <div class="mt-1 text-xs text-slate-500">{{ getTeamDesc(team.members, store.employees, store.teams) }}</div>
              </div>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <button class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50" @click="openTeamStudio(team.id)">编辑结构</button>
              <button class="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100" @click="store.cloneTeam(team.id)">克隆</button>
              <button class="rounded-md px-2 py-1 text-rose-500 hover:bg-rose-50" @click="store.deleteTeam(team.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <aside class="panel flex min-h-0 w-[360px] flex-col">
      <div class="panel-header">
        <span>招募推荐</span>
      </div>
      <div class="scrollbar-thin flex-1 overflow-y-auto p-4">
        <div class="mb-4 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-500">
          这里先作为团队招募推荐位使用。点任意卡片会直接跳到“招募员工”页面里的团队市场。
        </div>
        <div class="space-y-3">
          <RouterLink
            v-for="team in presetTeams"
            :key="team.name"
            class="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300"
            to="/market?tab=team"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <div class="text-sm font-semibold text-slate-900">{{ team.name }}</div>
                <div class="mt-2 text-xs leading-5 text-slate-500">{{ team.desc }}</div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <span
                    v-for="tag in team.tags"
                    :key="tag"
                    class="rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-700"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
              <div class="rounded-2xl bg-slate-950 px-3 py-2 text-[11px] font-semibold tracking-[0.18em] text-white">
                TEAM
              </div>
            </div>
          </RouterLink>
        </div>
      </div>
    </aside>

    <div v-if="teamStudioOpen" class="fixed inset-0 z-50 bg-slate-950/70">
      <div class="flex h-full w-full bg-slate-100 text-slate-900">
        <aside class="w-[280px] border-r border-slate-200 bg-white p-4">
          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div class="text-lg font-semibold">团队中心</div>
            <p class="mt-2 text-xs leading-5 text-slate-500">
              一个团队只能有一个根节点。可以把经理、员工或团队引用拖进中间画布，并继续往经理节点里挂下属。
            </p>
          </div>

          <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div class="mb-3 text-xs font-semibold tracking-[0.18em] text-slate-400">团队信息</div>
            <div class="space-y-3">
              <label class="block">
                <div class="mb-1 text-xs font-medium text-slate-500">团队图标</div>
                <input
                  v-model="teamForm.icon"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                />
              </label>
              <label class="block">
                <div class="mb-1 text-xs font-medium text-slate-500">团队名称</div>
                <input
                  v-model="teamForm.name"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                />
              </label>
            </div>
          </div>

          <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div class="mb-3 text-xs font-semibold tracking-[0.18em] text-slate-400">当前结构</div>
            <div v-if="studioRootResolved" class="flex items-center gap-3 rounded-xl bg-slate-50 px-3 py-3">
              <AvatarBadge :icon="studioRootResolved.icon" :label="studioRootResolved.name" :size="40" rounded="xl" />
              <div class="min-w-0">
                <div class="truncate text-sm font-semibold text-slate-800">{{ studioRootResolved.name }}</div>
                <div class="mt-1 text-xs text-slate-500">
                  {{ studioRootResolved.role === 'manager' ? '经理根节点' : studioRootResolved.role === 'team' ? '团队引用根节点' : '员工根节点' }}
                </div>
              </div>
            </div>
            <div v-else class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-3 py-6 text-center text-sm text-slate-400">
              还没有根节点，把右侧组件拖进中间画布即可开始编辑。
            </div>
            <div class="mt-3 text-xs leading-5 text-slate-500">
              {{ currentTeamMembers.length ? getTeamDesc(currentTeamMembers, store.employees, store.teams) : '空团队结构' }}
            </div>
          </div>

          <div v-if="teamStudioMessage" class="mt-4 rounded-2xl border px-4 py-3 text-sm" :class="teamStudioMessageClass">
            {{ teamStudioMessage }}
          </div>
        </aside>

        <main class="flex min-w-0 flex-1 flex-col">
          <div class="border-b border-slate-200 bg-white px-6 py-4">
            <div class="flex flex-wrap items-center gap-3">
              <div>
                <div class="text-sm font-semibold text-slate-800">团队画布</div>
                <div class="mt-1 text-xs text-slate-500">中键拖拽空白区域可平移，滚轮可缩放，布局会自动居中当前团队结构。</div>
              </div>
              <button
                class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium"
                @click="focusTeamContent"
              >
                定位到内容
              </button>
              <div class="text-xs text-slate-500">缩放 {{ Math.round(teamView.scale * 100) }}%</div>
              <div class="ml-auto flex gap-3">
                <button class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium" @click="closeTeamStudio">
                  取消更改
                </button>
                <button class="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white" @click="saveTeam">
                  保存团队结构
                </button>
              </div>
            </div>
          </div>

          <div class="flex min-h-0 flex-1">
            <section class="flex min-w-0 flex-1 flex-col overflow-hidden p-4">
              <div
                ref="teamViewportRef"
                class="relative min-h-0 flex-1 overflow-hidden rounded-3xl border border-slate-200 bg-white"
                @mousedown="startTeamPan"
                @dragover.prevent
                @drop="dropToRoot"
                @wheel.prevent="handleTeamWheel"
              >
                <div class="absolute inset-0" :style="teamWorldStyle">
                  <div
                    class="relative bg-[radial-gradient(circle_at_1px_1px,#cbd5e1_1.2px,transparent_0)] bg-[length:24px_24px] bg-white"
                    :style="{ width: `${WORLD_W}px`, height: `${WORLD_H}px` }"
                  >
                    <div class="absolute inset-0" :style="teamCanvasOffsetStyle">
                      <div
                        v-if="currentTeamMembers.length"
                        ref="teamRootRef"
                        class="absolute left-0 top-0"
                        :style="{ transform: 'translate(-50%, -50%)' }"
                      >
                        <TeamTreeNode
                          :raw-node="currentTeamMembers[0]"
                          path="0"
                          :emps="store.employees"
                          :teams="store.teams"
                          :drop-hint="dropHint"
                          @remove="removeByPath"
                          @drag-start="startTreeDrag"
                          @drop-before="dropBefore"
                          @drop-children="dropIntoChildren"
                        />
                      </div>
                    </div>

                    <div
                      v-if="!currentTeamMembers.length"
                      class="pointer-events-none absolute inset-0 flex items-center justify-center text-center text-slate-400"
                    >
                      <div>
                        <div class="text-lg font-semibold">还没有团队根节点</div>
                        <div class="mt-2 text-sm">把右侧的经理、员工或团队拖进来，团队画布只会保留一个根节点。</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <aside class="flex min-h-0 w-[320px] flex-col border-l border-slate-200 bg-white p-4">
              <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div class="text-sm font-semibold">招募推荐</div>
                <div class="mt-1 text-xs leading-5 text-slate-500">推荐团队会跳到团队市场，可用组件可以直接拖进中间画布。</div>
              </div>

              <div class="mt-4 min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
                <div class="space-y-3">
                  <RouterLink
                    v-for="team in presetTeams"
                    :key="`studio-${team.name}`"
                    class="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300"
                    to="/market?tab=team"
                  >
                    <div class="text-sm font-semibold text-slate-900">{{ team.name }}</div>
                    <div class="mt-2 text-xs leading-5 text-slate-500">{{ team.desc }}</div>
                  </RouterLink>
                </div>

                <div>
                  <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">团队组件</div>
                  <div class="space-y-2">
                    <div
                      v-for="team in availableTeamPalette"
                      :key="`team-${team.id}`"
                      class="cursor-grab rounded-xl border border-slate-200 bg-white px-3 py-3 shadow-sm"
                      draggable="true"
                      @dragstart="startPaletteDrag({ kind: 'team', refId: team.id })"
                    >
                      <div class="flex items-center gap-2">
                        <AvatarBadge :icon="team.icon" :label="team.name" :size="28" rounded="lg" />
                        <span class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800">{{ team.name }}</span>
                        <span class="rounded bg-slate-100 px-2 py-0.5 text-[10px] text-slate-500">团队</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">经理席位</div>
                  <div class="space-y-2">
                    <div
                      v-for="emp in managerPalette"
                      :key="`manager-${emp.id}`"
                      class="cursor-grab rounded-xl border border-amber-200 bg-white px-3 py-3 shadow-sm"
                      draggable="true"
                      @dragstart="startPaletteDrag({ kind: 'emp', refId: emp.id })"
                    >
                      <div class="flex items-center gap-2">
                        <AvatarBadge :icon="emp.icon" :label="emp.name" :size="28" rounded="lg" />
                        <span class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800">{{ emp.name }}</span>
                        <span class="rounded bg-amber-100 px-2 py-0.5 text-[10px] text-amber-700">经理</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">员工席位</div>
                  <div class="space-y-2">
                    <div
                      v-for="emp in workerPalette"
                      :key="`worker-${emp.id}`"
                      class="cursor-grab rounded-xl border border-blue-200 bg-white px-3 py-3 shadow-sm"
                      draggable="true"
                      @dragstart="startPaletteDrag({ kind: 'emp', refId: emp.id })"
                    >
                      <div class="flex items-center gap-2">
                        <AvatarBadge :icon="emp.icon" :label="emp.name" :size="28" rounded="lg" />
                        <span class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800">{{ emp.name }}</span>
                        <span class="rounded bg-blue-100 px-2 py-0.5 text-[10px] text-blue-700">员工</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import AvatarBadge from '../components/common/AvatarBadge.vue'
import TeamTreeNode from '../components/employee/TeamTreeNode.vue'
import { useSimuBossStore } from '../stores/simuBoss'
import { cloneDeep, getTeamDesc, hasCircularTeamRef, resolveNode } from '../utils/tree'

const WORLD_W = 12000
const WORLD_H = 12000
const WORLD_ORIGIN_X = WORLD_W / 2
const WORLD_ORIGIN_Y = WORLD_H / 2

const store = useSimuBossStore()
const teamStudioOpen = ref(false)
const editingTeamId = ref(null)
const currentTeamMembers = ref([])
const dragging = ref(null)
const dropHint = ref('')
const teamStudioMessage = ref('')
const teamStudioMessageType = ref('info')
const teamViewportRef = ref(null)
const teamRootRef = ref(null)
const teamPanState = ref(null)
const teamView = ref({ x: 32, y: 24, scale: 1 })
const teamContentSize = ref({ width: 320, height: 176 })

const teamForm = reactive({
  icon: 'TEAM',
  name: '',
})

const presetTeams = [
  {
    name: '数据采集团队',
    desc: '擅长全网搜索、网页抓取、表格整理和信息清洗，适合先把原始资料收上来再交给分析团队。',
    tags: ['Search', '网页采集', '表格归档', '数据清洗'],
  },
  {
    name: 'PPT 制作团队',
    desc: '负责把零散信息整理成演示文稿，覆盖大纲、页面文案、视觉排版和配图建议。',
    tags: ['PPT 大纲', '演示排版', '图文整合', '汇报包装'],
  },
  {
    name: '印度团队',
    desc: '真人 24h 在线干活',
    tags: ['真人执行', '24h 在线', '多班次协作', '高频跟进'],
  },
]

const availableTeamPalette = computed(() => store.teams.filter((team) => team.id !== editingTeamId.value))
const managerPalette = computed(() => store.employees.filter((item) => item.role === 'manager'))
const workerPalette = computed(() => store.employees.filter((item) => item.role !== 'manager'))
const studioRootResolved = computed(() =>
  currentTeamMembers.value.length ? resolveNode(currentTeamMembers.value[0], store.employees, store.teams) : null,
)
const teamStudioMessageClass = computed(() =>
  teamStudioMessageType.value === 'error'
    ? 'border-rose-200 bg-rose-50 text-rose-700'
    : teamStudioMessageType.value === 'success'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
      : 'border-slate-200 bg-slate-50 text-slate-600',
)
const teamCanvasOffsetStyle = computed(() => ({
  transform: `translate(${WORLD_ORIGIN_X}px, ${WORLD_ORIGIN_Y}px)`,
  transformOrigin: '0 0',
}))
const teamWorldStyle = computed(() => ({
  transform: `translate(${teamView.value.x}px, ${teamView.value.y}px) scale(${teamView.value.scale})`,
  transformOrigin: '0 0',
}))

function setTeamStudioMessage(message, type = 'info') {
  teamStudioMessage.value = message
  teamStudioMessageType.value = type
}

function clearTeamStudioMessage() {
  teamStudioMessage.value = ''
}

function openTeamStudio(id = null) {
  editingTeamId.value = id
  dragging.value = null
  dropHint.value = ''
  clearTeamStudioMessage()
  teamForm.icon = 'TEAM'
  teamForm.name = ''
  currentTeamMembers.value = []

  if (id) {
    const team = store.teams.find((item) => item.id === id)
    if (team) {
      teamForm.icon = team.icon
      teamForm.name = team.name
      currentTeamMembers.value = cloneDeep(team.members || []).slice(0, 1)
    }
  }

  teamStudioOpen.value = true
}

function closeTeamStudio() {
  teamStudioOpen.value = false
  dragging.value = null
  dropHint.value = ''
  clearTeamStudioMessage()
}

function saveTeam() {
  if (currentTeamMembers.value.length > 1) {
    setTeamStudioMessage('团队结构只能保留一个根节点，请先整理后再保存。', 'error')
    return
  }

  store.upsertTeam(
    {
      icon: teamForm.icon || 'TEAM',
      name: teamForm.name || '无名小队',
      members: currentTeamMembers.value,
      desc: getTeamDesc(currentTeamMembers.value, store.employees, store.teams),
    },
    editingTeamId.value,
  )

  setTeamStudioMessage('团队结构已保存。', 'success')
  window.setTimeout(() => {
    closeTeamStudio()
  }, 180)
}

function createNodeFromDrag(payload) {
  if (!payload) return null
  if (payload.kind === 'emp') return { type: 'emp_ref', refId: payload.refId, children: [] }
  if (payload.kind === 'team') return { type: 'team_ref', refId: payload.refId }
  return null
}

function getNodeByPath(path) {
  if (!path) return null
  const indices = path.split('-').map((item) => Number.parseInt(item, 10))
  let current = currentTeamMembers.value[indices[0]]
  for (let i = 1; i < indices.length; i += 1) current = current?.children?.[indices[i]]
  return current
}

function isRootPath(path) {
  return !String(path).includes('-')
}

function removeByPath(path) {
  const indices = path.split('-').map((item) => Number.parseInt(item, 10))
  const last = indices.pop()
  if (indices.length === 0) {
    currentTeamMembers.value.splice(last, 1)
    measureAndFitTeamCanvas()
    return
  }
  const parent = getNodeByPath(indices.join('-'))
  parent?.children?.splice(last, 1)
  measureAndFitTeamCanvas()
}

function pullByPath(path) {
  const indices = path.split('-').map((item) => Number.parseInt(item, 10))
  const last = indices.pop()
  if (indices.length === 0) return currentTeamMembers.value.splice(last, 1)[0]
  const parent = getNodeByPath(indices.join('-'))
  return parent?.children?.splice(last, 1)?.[0]
}

function insertBeforePath(path, node) {
  const indices = path.split('-').map((item) => Number.parseInt(item, 10))
  const last = indices.pop()
  if (indices.length === 0) {
    currentTeamMembers.value.splice(last, 0, node)
    return
  }
  const parent = getNodeByPath(indices.join('-'))
  if (!parent.children) parent.children = []
  parent.children.splice(last, 0, node)
}

function startPaletteDrag(payload) {
  dragging.value = payload
  clearTeamStudioMessage()
}

function startTreeDrag(payload) {
  dragging.value = payload
  clearTeamStudioMessage()
}

function resetDragState() {
  dragging.value = null
  dropHint.value = ''
}

function materializeDraggingNode() {
  if (!dragging.value) return null
  if (dragging.value.kind === 'existing') return pullByPath(dragging.value.path)
  if (dragging.value.kind === 'team' && hasCircularTeamRef(editingTeamId.value, dragging.value.refId, store.teams)) {
    setTeamStudioMessage('不能形成循环团队引用。', 'error')
    return null
  }
  return createNodeFromDrag(dragging.value)
}

function dropToRoot() {
  if (dragging.value?.kind === 'existing' && dragging.value.path === '0') {
    resetDragState()
    return
  }

  if (currentTeamMembers.value.length) {
    setTeamStudioMessage('团队画布只能保留一个根节点，请把新成员拖到现有经理节点内部。', 'error')
    resetDragState()
    return
  }

  const node = materializeDraggingNode()
  if (!node) {
    resetDragState()
    return
  }

  currentTeamMembers.value = [node]
  resetDragState()
  setTeamStudioMessage('已放入团队根节点。', 'success')
  measureAndFitTeamCanvas()
}

function dropBefore(path) {
  if (dragging.value?.kind === 'existing' && path.startsWith(dragging.value.path)) return

  if (isRootPath(path)) {
    setTeamStudioMessage('团队只能有一个根节点，不能在根层级再插入新的节点。', 'error')
    resetDragState()
    return
  }

  const node = materializeDraggingNode()
  if (!node) {
    resetDragState()
    return
  }

  insertBeforePath(path, node)
  resetDragState()
  clearTeamStudioMessage()
  measureAndFitTeamCanvas()
}

function dropIntoChildren(path) {
  if (dragging.value?.kind === 'existing' && path.startsWith(dragging.value.path)) return

  const node = materializeDraggingNode()
  if (!node) {
    resetDragState()
    return
  }

  const parent = getNodeByPath(path)
  if (!parent.children) parent.children = []
  parent.children.push(node)
  resetDragState()
  clearTeamStudioMessage()
  measureAndFitTeamCanvas()
}

async function measureTeamCanvas() {
  await nextTick()
  if (!teamRootRef.value) {
    teamContentSize.value = { width: 320, height: 176 }
    return
  }

  teamContentSize.value = {
    width: Math.max(320, teamRootRef.value.offsetWidth || 320),
    height: Math.max(176, teamRootRef.value.offsetHeight || 176),
  }
}

function clampTeamViewport() {
  const rect = teamViewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const scaledWidth = WORLD_W * teamView.value.scale
  const scaledHeight = WORLD_H * teamView.value.scale
  const minX = scaledWidth <= rect.width ? (rect.width - scaledWidth) / 2 : rect.width - scaledWidth
  const maxX = scaledWidth <= rect.width ? minX : 0
  const minY = scaledHeight <= rect.height ? (rect.height - scaledHeight) / 2 : rect.height - scaledHeight
  const maxY = scaledHeight <= rect.height ? minY : 0
  teamView.value = {
    ...teamView.value,
    x: Math.min(maxX, Math.max(minX, teamView.value.x)),
    y: Math.min(maxY, Math.max(minY, teamView.value.y)),
  }
}

function fitViewportToTeamContent() {
  const rect = teamViewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const paddedWidth = teamContentSize.value.width + 192
  const paddedHeight = teamContentSize.value.height + 192
  const fitScale = Math.min(rect.width / paddedWidth, rect.height / paddedHeight, 1)
  const nextScale = Math.max(0.42, fitScale)

  teamView.value = {
    scale: nextScale,
    x: rect.width / 2 - WORLD_ORIGIN_X * nextScale,
    y: rect.height / 2 - WORLD_ORIGIN_Y * nextScale,
  }

  clampTeamViewport()
}

async function measureAndFitTeamCanvas() {
  await measureTeamCanvas()
  fitViewportToTeamContent()
}

function focusTeamContent() {
  measureAndFitTeamCanvas()
}

function startTeamPan(event) {
  if (event.target?.closest?.('button, input, textarea, a')) return
  if (event.target?.closest?.('[draggable="true"]')) return

  teamPanState.value = {
    startX: event.clientX,
    startY: event.clientY,
    originX: teamView.value.x,
    originY: teamView.value.y,
  }
  window.addEventListener('mousemove', moveTeamPan)
  window.addEventListener('mouseup', stopTeamPan, { once: true })
}

function moveTeamPan(event) {
  if (!teamPanState.value) return
  teamView.value = {
    ...teamView.value,
    x: teamPanState.value.originX + (event.clientX - teamPanState.value.startX),
    y: teamPanState.value.originY + (event.clientY - teamPanState.value.startY),
  }
  clampTeamViewport()
}

function stopTeamPan() {
  teamPanState.value = null
  window.removeEventListener('mousemove', moveTeamPan)
}

function handleTeamWheel(event) {
  const rect = teamViewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const oldScale = teamView.value.scale
  const fitScale = Math.min(rect.width / WORLD_W, rect.height / WORLD_H)
  const minScale = Math.min(1, Math.max(0.35, fitScale))
  const nextScale = Math.min(1.16, Math.max(minScale, oldScale * (event.deltaY > 0 ? 0.98 : 1.02)))
  const px = event.clientX - rect.left
  const py = event.clientY - rect.top
  const wx = (px - teamView.value.x) / oldScale
  const wy = (py - teamView.value.y) / oldScale

  teamView.value = {
    scale: nextScale,
    x: px - wx * nextScale,
    y: py - wy * nextScale,
  }

  clampTeamViewport()
}

onMounted(() => {
  window.addEventListener('resize', measureAndFitTeamCanvas)
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', moveTeamPan)
  window.removeEventListener('resize', measureAndFitTeamCanvas)
})

watch(teamStudioOpen, async (open) => {
  if (!open) return
  await measureAndFitTeamCanvas()
})

watch(
  currentTeamMembers,
  async () => {
    if (!teamStudioOpen.value) return
    await measureAndFitTeamCanvas()
  },
  { deep: true },
)
</script>
