<template>
  <div class="flex h-full min-h-0 gap-5 p-5">
    <section class="panel flex min-h-0 min-w-0 flex-[1.35] flex-col">
      <div class="panel-header">
        <span>员工中心</span>
      </div>

      <div class="min-h-0 flex-1 p-4">
        <div class="grid h-full min-h-0 gap-5 xl:grid-cols-2">
          <section class="flex min-h-0 flex-col rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <div class="text-sm font-semibold text-slate-900">经理席位</div>
                <div class="mt-1 text-xs text-slate-500">负责拆解任务、推进协作与最终汇总。</div>
              </div>
              <button
                class="rounded-lg bg-slate-700 px-3 py-2 text-xs font-semibold text-white"
                @click="openEmployeeModal(null, 'manager')"
              >
                + 招募经理
              </button>
            </div>

            <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto pr-1">
              <div
                v-if="!managers.length"
                class="rounded-xl border border-dashed border-slate-200 bg-white px-4 py-8 text-center text-sm text-slate-400"
              >
                还没有经理，先招募一位负责人吧。
              </div>

              <div v-else class="grid gap-3 sm:grid-cols-2">
                <div
                  v-for="emp in managers"
                  :key="emp.id"
                  class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300"
                >
                  <div class="flex items-start gap-3">
                    <AvatarBadge :icon="emp.icon" :label="emp.name" :size="44" rounded="xl" />
                    <div class="min-w-0 flex-1">
                      <div class="flex items-center gap-2">
                        <div class="truncate text-sm font-semibold text-slate-900">{{ emp.name }}</div>
                        <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">
                          经理
                        </span>
                        <span
                          v-if="emp.locked"
                          class="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700"
                        >
                          市场样板
                        </span>
                      </div>
                      <div class="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
                        {{ getManagerSummary(emp) }}
                      </div>
                    </div>
                  </div>

                  <div class="mt-4 flex items-center gap-2 text-[11px]">
                    <button
                      v-if="!emp.locked"
                      class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50"
                      @click="openEmployeeModal(emp.id)"
                    >
                      配置
                    </button>
                    <button
                      v-else
                      class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50"
                      @click="cloneAndEditEmployee(emp.id)"
                    >
                      克隆后编辑
                    </button>
                    <button
                      class="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100"
                      @click="store.cloneEmployee(emp.id)"
                    >
                      克隆
                    </button>
                    <button
                      class="rounded-md px-2 py-1 text-rose-500 hover:bg-rose-50"
                      @click="store.deleteEmployee(emp.id)"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="flex min-h-0 flex-col rounded-2xl border border-blue-200 bg-blue-50/40 p-4">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <div class="text-sm font-semibold text-slate-900">工人席位</div>
                <div class="mt-1 text-xs text-slate-500">负责接收明确子任务并直接执行。</div>
              </div>
              <button
                class="rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white"
                @click="openEmployeeModal(null, 'worker')"
              >
                + 招募工人
              </button>
            </div>

            <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto pr-1">
              <div
                v-if="!workers.length"
                class="rounded-xl border border-dashed border-blue-200 bg-white px-4 py-8 text-center text-sm text-slate-400"
              >
                还没有工人，先招募几位执行角色吧。
              </div>

              <div v-else class="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
                <div
                  v-for="emp in workers"
                  :key="emp.id"
                  class="rounded-2xl border border-blue-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300"
                >
                  <div class="flex items-start gap-3">
                    <AvatarBadge :icon="emp.icon" :label="emp.name" :size="44" rounded="xl" />
                    <div class="min-w-0 flex-1">
                      <div class="flex items-center gap-2">
                        <div class="truncate text-sm font-semibold text-slate-900">{{ emp.name }}</div>
                        <span class="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700">
                          工人
                        </span>
                        <span
                          v-if="emp.locked"
                          class="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700"
                        >
                          市场样板
                        </span>
                      </div>
                      <div class="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
                        {{ getWorkerSummary(emp) }}
                      </div>
                    </div>
                  </div>

                  <div class="mt-4 flex items-center gap-2 text-[11px]">
                    <button
                      v-if="!emp.locked"
                      class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50"
                      @click="openEmployeeModal(emp.id)"
                    >
                      配置
                    </button>
                    <button
                      v-else
                      class="rounded-md px-2 py-1 text-brand-600 hover:bg-brand-50"
                      @click="cloneAndEditEmployee(emp.id)"
                    >
                      克隆后编辑
                    </button>
                    <button
                      class="rounded-md px-2 py-1 text-slate-500 hover:bg-slate-100"
                      @click="store.cloneEmployee(emp.id)"
                    >
                      克隆
                    </button>
                    <button
                      class="rounded-md px-2 py-1 text-rose-500 hover:bg-rose-50"
                      @click="store.deleteEmployee(emp.id)"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>

    <aside class="panel flex min-h-0 w-[360px] flex-col">
      <div class="panel-header">
        <span>招募推荐</span>
      </div>
      <div class="scrollbar-thin flex-1 overflow-y-auto p-4">
        <div class="mb-4 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm leading-6 text-slate-500">
          这里作为招募推荐位使用。感兴趣的话，点任意卡片直接进入“人才市场”查看。
        </div>
        <div class="space-y-3">
          <RouterLink
            v-for="candidate in marketEmployees"
            :key="candidate.name"
            class="block rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300"
            to="/market"
          >
            <div class="flex items-start gap-3">
              <AvatarBadge :icon="candidate.icon" :label="candidate.name" :size="42" rounded="xl" />
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <div class="truncate text-sm font-semibold text-slate-900">{{ candidate.name }}</div>
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">
                    {{ candidate.role }}
                  </span>
                </div>
                <div class="mt-2 text-xs leading-5 text-slate-500">{{ candidate.desc }}</div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <span
                    v-for="tool in candidate.highlights"
                    :key="tool"
                    class="rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-700"
                  >
                    {{ tool }}
                  </span>
                </div>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>
    </aside>

    <Dialog v-model:open="employeeModalOpen">
      <DialogContent class="max-h-[88vh] max-w-2xl p-0">
        <DialogHeader class="border-b border-slate-200 px-6 py-5">
          <DialogTitle>{{ avatarUi.modalTitle(editingEmployeeId) }}</DialogTitle>
          <DialogDescription>为员工配置头像、职责和模型参数。</DialogDescription>
        </DialogHeader>

        <div class="scrollbar-thin max-h-[calc(88vh-136px)] overflow-y-auto px-6 py-5">
          <div class="grid gap-4">
            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-start pt-2 text-sm font-medium text-slate-700">头像</label>
              <div class="space-y-3">
                <div class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-3">
                  <AvatarBadge :icon="employeeForm.icon" :label="employeeForm.name" :size="56" rounded="2xl" />
                  <div class="text-sm text-slate-500">从头像库里挑一个，更像真实员工。</div>
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
                  placeholder="也可以手动输入 emoji、缩写或头像值"
                />
              </div>
            </div>

            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-center text-sm font-medium text-slate-700">名称</label>
              <input
                v-model="employeeForm.name"
                class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              />
            </div>

            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-start pt-2 text-sm font-medium text-slate-700">角色</label>
              <div class="flex gap-4 text-sm">
                <label class="flex items-center gap-2">
                  <input v-model="employeeForm.role" type="radio" value="manager" />
                  经理
                </label>
                <label class="flex items-center gap-2">
                  <input v-model="employeeForm.role" type="radio" value="worker" />
                  工人
                </label>
              </div>
            </div>

            <div class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-center text-sm font-medium text-slate-700">模型</label>
              <select
                v-model="employeeForm.model"
                class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              >
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4o-mini">GPT-4o mini</option>
                <option value="deepseek-v3">DeepSeek V3</option>
                <option value="claude-3-5-sonnet-20240620">Claude 3.5 Sonnet</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="grid grid-cols-[120px_1fr] gap-3">
                <label class="self-center text-sm font-medium text-slate-700">启动方式</label>
                <select
                  v-model="employeeForm.activationType"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                >
                  <option value="text">任务描述</option>
                  <option value="word">Word 文件</option>
                </select>
              </div>
              <div class="grid grid-cols-[120px_1fr] gap-3">
                <label class="self-center text-sm font-medium text-slate-700">交付物</label>
                <select
                  v-model="employeeForm.deliverableType"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                >
                  <option value="text">文本结果</option>
                  <option value="ppt">PPT 文件</option>
                </select>
              </div>
            </div>

            <div v-if="employeeForm.role === 'worker'" class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-start pt-2 text-sm font-medium text-slate-700">System Prompt</label>
              <textarea
                v-model="employeeForm.prompt"
                rows="5"
                class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              />
            </div>

            <template v-else>
              <div class="grid grid-cols-[120px_1fr] gap-3">
                <label class="self-start pt-2 text-sm font-medium text-slate-700">拆解 Prompt</label>
                <textarea
                  v-model="employeeForm.plannerPrompt"
                  rows="5"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                />
              </div>
              <div class="grid grid-cols-[120px_1fr] gap-3">
                <label class="self-start pt-2 text-sm font-medium text-slate-700">汇总 Prompt</label>
                <textarea
                  v-model="employeeForm.synthesizerPrompt"
                  rows="5"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                />
              </div>
              <div class="grid grid-cols-[120px_1fr] gap-3">
                <label class="self-start pt-2 text-sm font-medium text-slate-700">固定拆解 JSON</label>
                <textarea
                  v-model="employeeForm.fixedPlanText"
                  rows="10"
                  class="rounded-lg border border-slate-200 px-3 py-2 font-mono text-sm outline-none focus:border-brand-500"
                  placeholder='{"summary":"","deliverable":"","tasks":[{"id":"t1","title":"","assigneeRefId":"","task":"","dependsOn":[],"reason":""}],"risks":[],"openQuestions":[]}'
                />
              </div>
            </template>

            <div class="grid grid-cols-2 gap-4">
              <div class="grid grid-cols-[120px_1fr] gap-3">
                <label class="self-center text-sm font-medium text-slate-700">Temperature</label>
                <input
                  v-model.number="employeeForm.temperature"
                  type="number"
                  step="0.1"
                  min="0"
                  max="2"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                />
              </div>
              <div class="grid grid-cols-[120px_1fr] gap-3">
                <label class="self-center text-sm font-medium text-slate-700">Max Tokens</label>
                <input
                  v-model.number="employeeForm.maxTokens"
                  type="number"
                  step="500"
                  min="1000"
                  class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                />
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

            <div v-if="employeeForm.role === 'worker'" class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-center text-sm font-medium text-slate-700">执行方式</label>
              <select
                v-model="employeeForm.executionMode"
                class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              >
                <option value="llm">普通执行</option>
                <option value="ppt_renderer">PPT 渲染</option>
              </select>
            </div>

            <div v-else class="grid grid-cols-[120px_1fr] gap-3">
              <label class="self-start pt-2 text-sm font-medium text-slate-700">审批</label>
              <label class="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-3 text-sm text-slate-700">
                <input v-model="employeeForm.requireApproval" type="checkbox" />
                拆解任务需要 Boss 审批
              </label>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
          <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="employeeModalOpen = false">
            取消
          </button>
          <button class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white" @click="saveEmployee">
            保存
          </button>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import AvatarBadge from '../components/common/AvatarBadge.vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog'
import { AVATAR_LIBRARY } from '../config/avatarLibrary'
import { useSimuBossStore } from '../stores/simuBoss'

const store = useSimuBossStore()
const employeeModalOpen = ref(false)
const editingEmployeeId = ref(null)
const avatarOptions = AVATAR_LIBRARY

const marketEmployees = [
  {
    icon: AVATAR_LIBRARY[1]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '浏览器自动化特工',
    role: '工人',
    desc: '擅长网页操作、信息抓取和重复流程执行，适合处理需要浏览器交互的任务。',
    highlights: ['Playwright', 'Browser Use', '截图取证', '表单自动填充'],
  },
  {
    icon: AVATAR_LIBRARY[2]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '全网情报猎手',
    role: '工人',
    desc: '会组合搜索、网页阅读和资料整理，适合做竞品、舆情和供应商搜集。',
    highlights: ['Search', '网页摘要', '线索归档', '批量对比'],
  },
  {
    icon: AVATAR_LIBRARY[3]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '数据接口拆弹手',
    role: '工人',
    desc: '专攻 API 调试、脚本编排和日志排错，能把分散数据源快速打通。',
    highlights: ['API 调试', 'Python 脚本', '日志分析', '数据清洗'],
  },
  {
    icon: AVATAR_LIBRARY[4]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '多模态创意经理',
    role: '经理',
    desc: '擅长把图像、文案、页面和演示材料串成完整方案，适合带创意型团队。',
    highlights: ['图像生成', '提示词编排', '演示整合', '资产统筹'],
  },
]

const employeeForm = reactive({
  icon: AVATAR_LIBRARY[0]?.value || 'DE',
  name: '',
  role: 'worker',
  model: 'gpt-4o',
  activationType: 'text',
  deliverableType: 'text',
  prompt: '',
  plannerPrompt: '',
  synthesizerPrompt: '',
  fixedPlanText: '',
  temperature: 0.7,
  maxTokens: 4096,
  toolsText: '',
  executionMode: 'llm',
  requireApproval: true,
})

const managers = computed(() =>
  store.employees.filter((item) => item.role === 'manager' && !item.hidden),
)
const workers = computed(() =>
  store.employees.filter((item) => item.role !== 'manager' && !item.hidden),
)

const avatarUi = {
  modalTitle: (editingId) =>
    editingId
      ? employeeForm.role === 'manager'
        ? '编辑经理'
        : '编辑工人'
      : employeeForm.role === 'manager'
        ? '招募经理'
        : '招募工人',
}

function getManagerSummary(emp) {
  const planner = emp.plannerPrompt?.trim()
  const synth = emp.synthesizerPrompt?.trim()
  if (planner) return planner.slice(0, 36)
  if (synth) return synth.slice(0, 36)
  return '负责拆解任务、推进协作并整合最终交付。'
}

function getWorkerSummary(emp) {
  const tools = (emp.tools || []).filter(Boolean)
  if (tools.length) return `擅长 ${tools.slice(0, 3).join(' / ')}`
  if (emp.prompt?.trim()) return emp.prompt.trim().slice(0, 36)
  return '接收明确子任务，直接执行并交付结果。'
}

function resetEmployeeForm(role = 'worker') {
  Object.assign(employeeForm, {
    icon: AVATAR_LIBRARY[0]?.value || 'DE',
    name: '',
    role,
    model: 'gpt-4o',
    activationType: 'text',
    deliverableType: 'text',
    prompt: '',
    plannerPrompt: '',
    synthesizerPrompt: '',
    fixedPlanText: '',
    temperature: 0.7,
    maxTokens: 4096,
    toolsText: '',
    executionMode: 'llm',
    requireApproval: true,
  })
}

function openEmployeeModal(id = null, role = 'worker') {
  editingEmployeeId.value = id
  resetEmployeeForm(role)
  if (id) {
    const emp = store.employees.find((item) => item.id === id)
    if (emp) {
      Object.assign(employeeForm, {
        icon: emp.icon,
        name: emp.name,
        role: emp.role,
        model: emp.model || 'gpt-4o',
        activationType: emp.activationType || 'text',
        deliverableType: emp.deliverableType || 'text',
        prompt: emp.prompt || '',
        plannerPrompt: emp.plannerPrompt || emp.prompt || '',
        synthesizerPrompt: emp.synthesizerPrompt || emp.prompt || '',
        fixedPlanText: emp.fixedPlan ? JSON.stringify(emp.fixedPlan, null, 2) : '',
        temperature: emp.temperature ?? 0.7,
        maxTokens: emp.maxTokens || 4096,
        toolsText: (emp.tools || []).join(', '),
        executionMode: emp.executionMode || 'llm',
        requireApproval: emp.requireApproval !== false,
      })
    }
  }
  employeeModalOpen.value = true
}

function cloneAndEditEmployee(id) {
  const clonedId = store.cloneEmployee(id)
  if (!clonedId) return
  const cloned = store.employees.find((item) => item.id === clonedId)
  openEmployeeModal(clonedId, cloned?.role || 'worker')
}

function saveEmployee() {
  let fixedPlan = null
  if (employeeForm.role === 'manager' && employeeForm.fixedPlanText.trim()) {
    try {
      fixedPlan = JSON.parse(employeeForm.fixedPlanText)
    } catch {
      window.alert('固定拆解 JSON 格式不正确，请先修正后再保存。')
      return
    }
  }

  store.upsertEmployee(
    {
      icon: employeeForm.icon || AVATAR_LIBRARY[0]?.value || 'DE',
      name: employeeForm.name || '临时工位',
      role: employeeForm.role,
      model: employeeForm.model,
      activationType: employeeForm.activationType,
      deliverableType: employeeForm.deliverableType,
      prompt: employeeForm.prompt,
      plannerPrompt: employeeForm.role === 'manager' ? employeeForm.plannerPrompt : '',
      synthesizerPrompt: employeeForm.role === 'manager' ? employeeForm.synthesizerPrompt : '',
      fixedPlan,
      temperature: employeeForm.temperature,
      maxTokens: employeeForm.maxTokens,
      requireApproval: employeeForm.requireApproval,
      tools: employeeForm.toolsText.split(',').map((item) => item.trim()).filter(Boolean),
      executionMode: employeeForm.role === 'worker' ? employeeForm.executionMode : 'llm',
    },
    editingEmployeeId.value,
  )
  employeeModalOpen.value = false
}
</script>
