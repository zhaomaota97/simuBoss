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
        <div v-if="!store.teams.length" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-12 text-center text-sm text-slate-400">
          还没有团队，先把经理和工人组织起来吧。
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
            class="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-brand-300 hover:-translate-y-0.5"
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
      <div class="flex h-full w-full bg-white">
        <aside class="flex w-[360px] flex-col border-r border-slate-200 bg-white">
          <div class="border-b border-slate-200 p-5">
            <h2 class="text-lg font-semibold text-slate-900">团队结构设定</h2>
            <div class="mt-4 space-y-4">
              <div>
                <label class="mb-1 block text-xs font-medium text-slate-500">团队图标</label>
                <input v-model="teamForm.icon" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-slate-500">团队名称</label>
                <input v-model="teamForm.name" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
              </div>
            </div>
          </div>
          <div class="scrollbar-thin flex-1 overflow-y-auto bg-slate-50 p-5">
            <div class="mb-3 text-xs font-semibold tracking-[0.18em] text-slate-400">可用组件</div>
            <div class="space-y-3">
              <div
                v-for="team in availableTeamPalette"
                :key="`team-${team.id}`"
                class="cursor-grab rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm shadow-sm"
                draggable="true"
                @dragstart="startPaletteDrag({ kind: 'team', refId: team.id })"
              >
                <div class="flex items-center gap-2">
                  <AvatarBadge :icon="team.icon" :label="team.name" :size="28" rounded="lg" />
                  <span class="flex-1">{{ team.name }}</span>
                  <span class="rounded bg-slate-100 px-2 py-0.5 text-[10px] text-slate-500">团队</span>
                </div>
              </div>
              <div
                v-for="emp in store.employees"
                :key="`emp-${emp.id}`"
                class="cursor-grab rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm shadow-sm"
                draggable="true"
                @dragstart="startPaletteDrag({ kind: 'emp', refId: emp.id })"
              >
                <div class="flex items-center gap-2">
                  <AvatarBadge :icon="emp.icon" :label="emp.name" :size="28" rounded="lg" />
                  <span class="flex-1">{{ emp.name }}</span>
                  <span
                    class="rounded px-2 py-0.5 text-[10px]"
                    :class="emp.role === 'manager' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'"
                  >
                    {{ emp.role === 'manager' ? '经理' : '工人' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <section class="flex min-w-0 flex-1 flex-col bg-slate-50">
          <div class="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-5">
            <div class="text-sm font-semibold text-slate-600">结构画布</div>
            <div class="flex gap-3">
              <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="teamStudioOpen = false">取消更改</button>
              <button class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white" @click="saveTeam">保存团队结构</button>
            </div>
          </div>
          <div
            class="scrollbar-thin relative flex-1 overflow-auto bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] bg-[size:20px_20px] p-6"
            @dragover.prevent
            @drop="dropToRoot()"
          >
            <div v-if="!currentTeamMembers.length" class="absolute inset-0 flex items-center justify-center text-lg text-slate-400">
              拖拽左侧的经理、工人或团队到这里组成结构
            </div>
            <div v-else class="flex flex-wrap gap-4">
              <TeamTreeNode
                v-for="(member, index) in currentTeamMembers"
                :key="String(index)"
                :raw-node="member"
                :path="String(index)"
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
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import AvatarBadge from '../components/common/AvatarBadge.vue'
import TeamTreeNode from '../components/employee/TeamTreeNode.vue'
import { useSimuBossStore } from '../stores/simuBoss'
import { cloneDeep, getTeamDesc, hasCircularTeamRef } from '../utils/tree'

const store = useSimuBossStore()
const teamStudioOpen = ref(false)
const editingTeamId = ref(null)
const currentTeamMembers = ref([])
const dragging = ref(null)
const dropHint = ref('')

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
    desc: '真人24h在线干活',
    tags: ['真人执行', '24h 在线', '多班次协作', '高频跟进'],
  },
]

const availableTeamPalette = computed(() => store.teams.filter((team) => team.id !== editingTeamId.value))

function openTeamStudio(id = null) {
  editingTeamId.value = id
  dragging.value = null
  dropHint.value = ''
  teamForm.icon = 'TEAM'
  teamForm.name = ''
  currentTeamMembers.value = []
  if (id) {
    const team = store.teams.find((item) => item.id === id)
    if (team) {
      teamForm.icon = team.icon
      teamForm.name = team.name
      currentTeamMembers.value = cloneDeep(team.members || [])
    }
  }
  teamStudioOpen.value = true
}

function saveTeam() {
  store.upsertTeam(
    {
      icon: teamForm.icon || 'TEAM',
      name: teamForm.name || '无名小队',
      members: currentTeamMembers.value,
      desc: getTeamDesc(currentTeamMembers.value, store.employees, store.teams),
    },
    editingTeamId.value,
  )
  teamStudioOpen.value = false
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

function removeByPath(path) {
  const indices = path.split('-').map((item) => Number.parseInt(item, 10))
  const last = indices.pop()
  if (indices.length === 0) {
    currentTeamMembers.value.splice(last, 1)
    return
  }
  const parent = getNodeByPath(indices.join('-'))
  parent?.children?.splice(last, 1)
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
}

function startTreeDrag(payload) {
  dragging.value = payload
}

function materializeDraggingNode() {
  if (!dragging.value) return null
  if (dragging.value.kind === 'existing') return pullByPath(dragging.value.path)
  if (dragging.value.kind === 'team' && hasCircularTeamRef(editingTeamId.value, dragging.value.refId, store.teams)) {
    window.alert('不能形成循环团队引用。')
    return null
  }
  return createNodeFromDrag(dragging.value)
}

function dropToRoot() {
  const node = materializeDraggingNode()
  if (!node) return
  currentTeamMembers.value.push(node)
  dragging.value = null
  dropHint.value = ''
}

function dropBefore(path) {
  if (dragging.value?.kind === 'existing' && path.startsWith(dragging.value.path)) return
  const node = materializeDraggingNode()
  if (!node) return
  insertBeforePath(path, node)
  dragging.value = null
  dropHint.value = ''
}

function dropIntoChildren(path) {
  if (dragging.value?.kind === 'existing' && path.startsWith(dragging.value.path)) return
  const node = materializeDraggingNode()
  if (!node) return
  const parent = getNodeByPath(path)
  if (!parent.children) parent.children = []
  parent.children.push(node)
  dragging.value = null
  dropHint.value = ''
}
</script>
