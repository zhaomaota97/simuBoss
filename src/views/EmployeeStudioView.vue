<template>
  <div class="flex h-full min-h-0 gap-5 p-5">
    <section class="panel flex min-h-0 flex-1 flex-col">
      <div class="panel-header">
        <span>🏢 团队架构列表</span>
        <button class="rounded-lg bg-brand-500 px-3 py-2 text-xs font-semibold text-white" @click="openTeamStudio()">
          + 编排新团队
        </button>
      </div>
      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div v-if="!store.teams.length" class="py-10 text-center text-sm text-slate-400">空空如也，请新建团队</div>
        <div v-for="team in store.teams" :key="team.id" class="mb-4 rounded-xl border border-slate-200 p-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-center gap-3">
              <AvatarBadge :icon="team.icon" :label="team.name" :size="44" rounded="xl" />
              <div>
                <div class="text-sm font-semibold text-slate-800">{{ team.name }}</div>
                <div class="mt-1 text-xs text-slate-500">{{ getTeamDesc(team.members, store.employees, store.teams) }}</div>
              </div>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <button class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50" @click="openTeamStudio(team.id)">编辑架构</button>
              <button class="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100" @click="store.cloneTeam(team.id)">克隆</button>
              <button class="rounded-md px-2 py-1 text-rose-500 hover:bg-rose-50" @click="store.deleteTeam(team.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="panel flex min-h-0 flex-1 flex-col">
      <div class="panel-header">
        <span>🤖 员工资源池</span>
        <button class="rounded-lg bg-brand-500 px-3 py-2 text-xs font-semibold text-white" @click="openEmployeeModal()">
          + 添加新员工
        </button>
      </div>
      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div v-if="!store.employees.length" class="py-10 text-center text-sm text-slate-400">空空如也，请录用新员工</div>
        <div v-for="emp in store.employees" :key="emp.id" class="mb-4 rounded-xl border border-slate-200 p-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-center gap-3">
              <AvatarBadge :icon="emp.icon" :label="emp.name" :size="44" rounded="xl" />
              <div>
                <div class="flex items-center gap-2 text-sm font-semibold text-slate-800">
                  <span>{{ emp.name }}</span>
                  <span
                    class="rounded px-2 py-0.5 text-[10px] font-medium"
                    :class="emp.role === 'manager' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'"
                  >
                    {{ emp.role === 'manager' ? '经理' : '工人' }}
                  </span>
                </div>
                <div class="mt-1 text-xs text-slate-500">
                  {{ emp.role === 'manager' ? '负责任务拆解与团队调度' : `掌握工具: ${(emp.tools || []).join(', ') || '无'}` }}
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <button class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50" @click="openEmployeeModal(emp.id)">配置</button>
              <button class="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100" @click="store.cloneEmployee(emp.id)">克隆</button>
              <button class="rounded-md px-2 py-1 text-rose-500 hover:bg-rose-50" @click="store.deleteEmployee(emp.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="employeeModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4">
      <div class="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl">
        <div class="mb-5 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">{{ avatarUi.modalTitle(editingEmployeeId) }}</h2>
          <button class="text-xl text-slate-400" @click="employeeModalOpen = false">x</button>
        </div>
        <div class="grid gap-4">
          <div class="grid grid-cols-[120px_1fr] gap-3">
            <label class="self-start pt-2 text-sm font-medium text-slate-700">{{ avatarUi.label }}</label>
            <div class="space-y-3">
              <div class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-3">
                <AvatarBadge :icon="employeeForm.icon" :label="employeeForm.name" :size="56" rounded="2xl" />
                <div class="text-sm text-slate-500">{{ avatarUi.helper }}</div>
              </div>
              <div class="grid grid-cols-6 gap-2">
                <button
                  v-for="avatar in avatarOptions"
                  :key="avatar.value"
                  type="button"
                  class="rounded-xl border p-1.5 transition"
                  :class="employeeForm.icon === avatar.value ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:border-slate-300'"
                  @click="employeeForm.icon = avatar.value"
                >
                  <AvatarBadge :icon="avatar.value" :label="avatar.label" :size="40" rounded="xl" />
                </button>
              </div>
              <input
                v-model="employeeForm.icon"
                class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                :placeholder="avatarUi.placeholder"
              />
            </div>
          </div>
          <div class="grid grid-cols-[120px_1fr] gap-3">
            <label class="self-center text-sm font-medium text-slate-700">名称</label>
            <input v-model="employeeForm.name" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
          </div>
          <div class="grid grid-cols-[120px_1fr] gap-3">
            <label class="self-start pt-2 text-sm font-medium text-slate-700">角色</label>
            <div class="flex gap-4 text-sm">
              <label class="flex items-center gap-2"><input v-model="employeeForm.role" type="radio" value="manager" /> 经理</label>
              <label class="flex items-center gap-2"><input v-model="employeeForm.role" type="radio" value="worker" /> 工人</label>
            </div>
          </div>
          <div class="grid grid-cols-[120px_1fr] gap-3">
            <label class="self-center text-sm font-medium text-slate-700">模型</label>
            <select v-model="employeeForm.model" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500">
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o mini</option>
              <option value="deepseek-v3">DeepSeek V3</option>
              <option value="claude-3-5-sonnet-20240620">Claude 3.5 Sonnet</option>
            </select>
          </div>
          <div v-if="employeeForm.role === 'worker'" class="grid grid-cols-[120px_1fr] gap-3">
            <label class="self-start pt-2 text-sm font-medium text-slate-700">System Prompt</label>
            <textarea v-model="employeeForm.prompt" rows="5" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
          </div>
          <template v-else>
            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-start pt-2 text-sm font-medium text-slate-700">拆解 Prompt</label>
              <textarea v-model="employeeForm.plannerPrompt" rows="5" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
            </div>
            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-start pt-2 text-sm font-medium text-slate-700">汇总 Prompt</label>
              <textarea v-model="employeeForm.synthesizerPrompt" rows="5" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
            </div>
          </template>
          <div class="grid grid-cols-2 gap-4">
            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-center text-sm font-medium text-slate-700">Temperature</label>
              <input v-model.number="employeeForm.temperature" type="number" step="0.1" min="0" max="2" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
            </div>
            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-center text-sm font-medium text-slate-700">Max Tokens</label>
              <input v-model.number="employeeForm.maxTokens" type="number" step="500" min="1000" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500" />
            </div>
          </div>
          <div v-if="employeeForm.role === 'worker'" class="grid grid-cols-[120px_1fr] gap-3">
            <label class="self-start pt-2 text-sm font-medium text-slate-700">工具</label>
            <input
              v-model="employeeForm.toolsText"
              placeholder="例如: terminal, Search_Web, db_read"
              class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
            />
          </div>
          <div v-else class="grid grid-cols-[120px_1fr] gap-3">
            <label class="self-start pt-2 text-sm font-medium text-slate-700">审批</label>
            <label class="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-3 text-sm text-slate-700">
              <input v-model="employeeForm.requireApproval" type="checkbox" />
              拆解任务需要 Boss 审批
            </label>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="employeeModalOpen = false">取消</button>
          <button class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white" @click="saveEmployee">保存</button>
        </div>
      </div>
    </div>

    <div v-if="teamStudioOpen" class="fixed inset-0 z-50 bg-slate-950/70">
      <div class="flex h-full w-full bg-white">
        <aside class="flex w-[360px] flex-col border-r border-slate-200 bg-white">
          <div class="border-b border-slate-200 p-5">
            <h2 class="text-lg font-semibold text-slate-900">团队架构设定</h2>
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
                  <span>{{ team.icon }}</span>
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
                  <span>{{ emp.icon }}</span>
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
            <div class="text-sm font-semibold text-slate-600">架构画布</div>
            <div class="flex gap-3">
              <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="teamStudioOpen = false">取消更改</button>
              <button class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white" @click="saveTeam">保存团队架构</button>
            </div>
          </div>
          <div
            class="scrollbar-thin relative flex-1 overflow-auto bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] bg-[size:20px_20px] p-6"
            @dragover.prevent
            @drop="dropToRoot()"
          >
            <div v-if="!currentTeamMembers.length" class="absolute inset-0 flex items-center justify-center text-lg text-slate-400">
              拖拽左侧的经理、工人或团队到这里组成架构
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
import { AVATAR_LIBRARY } from '../config/avatarLibrary'
import TeamTreeNode from '../components/employee/TeamTreeNode.vue'
import { useSimuBossStore } from '../stores/simuBoss'
import { cloneDeep, getTeamDesc, hasCircularTeamRef } from '../utils/tree'

const store = useSimuBossStore()
const employeeModalOpen = ref(false)
const editingEmployeeId = ref(null)
const teamStudioOpen = ref(false)
const editingTeamId = ref(null)
const currentTeamMembers = ref([])
const dragging = ref(null)
const dropHint = ref('')
const avatarUi = {
  modalTitle: (editingId) => (editingId ? '\u7f16\u8f91\u5458\u5de5\u4fe1\u606f' : '\u6dfb\u52a0\u65b0\u5458\u5de5'),
  label: '\u5934\u50cf',
  helper: '\u4ece\u5934\u50cf\u5e93\u91cc\u6311\u4e00\u4e2a\uff0c\u66f4\u50cf\u771f\u5b9e\u5458\u5de5',
  placeholder: '\u4e5f\u53ef\u4ee5\u624b\u52a8\u8f93\u5165 emoji\u3001\u7f29\u5199\u6216\u5934\u50cf\u503c',
}

const employeeForm = reactive({
  icon: '👷',
  name: '',
  role: 'worker',
  model: 'gpt-4o',
  prompt: '',
  plannerPrompt: '',
  synthesizerPrompt: '',
  temperature: 0.7,
  maxTokens: 4096,
  toolsText: '',
  requireApproval: true,
})

const teamForm = reactive({
  icon: '💼',
  name: '',
})

const availableTeamPalette = computed(() => store.teams.filter((team) => team.id !== editingTeamId.value))
const avatarOptions = AVATAR_LIBRARY

function resetEmployeeForm() {
  Object.assign(employeeForm, {
    icon: '👷',
    name: '',
    role: 'worker',
    model: 'gpt-4o',
    prompt: '',
    plannerPrompt: '',
    synthesizerPrompt: '',
    temperature: 0.7,
    maxTokens: 4096,
    toolsText: '',
    requireApproval: true,
  })
}

function openEmployeeModal(id = null) {
  editingEmployeeId.value = id
  resetEmployeeForm()
  if (id) {
    const emp = store.employees.find((item) => item.id === id)
    if (emp) {
      Object.assign(employeeForm, {
        icon: emp.icon,
        name: emp.name,
        role: emp.role,
        model: emp.model || 'gpt-4o',
        prompt: emp.prompt || '',
        plannerPrompt: emp.plannerPrompt || emp.prompt || '',
        synthesizerPrompt: emp.synthesizerPrompt || emp.prompt || '',
        temperature: emp.temperature ?? 0.7,
        maxTokens: emp.maxTokens || 4096,
        toolsText: (emp.tools || []).join(', '),
        requireApproval: emp.requireApproval !== false,
      })
    }
  }
  employeeModalOpen.value = true
}

function saveEmployee() {
  store.upsertEmployee(
    {
      icon: employeeForm.icon || '👷',
      name: employeeForm.name || '临时工',
      role: employeeForm.role,
      model: employeeForm.model,
      prompt: employeeForm.prompt,
      plannerPrompt: employeeForm.role === 'manager' ? employeeForm.plannerPrompt : '',
      synthesizerPrompt:
        employeeForm.role === 'manager' ? employeeForm.synthesizerPrompt : '',
      temperature: employeeForm.temperature,
      maxTokens: employeeForm.maxTokens,
      requireApproval: employeeForm.requireApproval,
      tools: employeeForm.toolsText.split(',').map((item) => item.trim()).filter(Boolean),
    },
    editingEmployeeId.value,
  )
  employeeModalOpen.value = false
}

function openTeamStudio(id = null) {
  editingTeamId.value = id
  dragging.value = null
  dropHint.value = ''
  teamForm.icon = '💼'
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
      icon: teamForm.icon || '💼',
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
