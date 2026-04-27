<template>
  <div class="flex h-full min-h-0 flex-col gap-5 p-5">
    <section class="panel flex min-h-0 flex-1 flex-col overflow-hidden">
      <div class="panel-header">
        <span>人才市场</span>
        <Tabs v-model:model-value="activeTab">
          <TabsList>
            <TabsTrigger value="employee">招募员工</TabsTrigger>
            <TabsTrigger value="team">招募团队</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div
        v-if="marketNotice"
        class="border-b border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
      >
        {{ marketNotice }}
      </div>

      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <Tabs v-model:model-value="activeTab">
          <TabsContent value="employee" class="mt-0">
            <div class="grid gap-4 xl:grid-cols-2">
              <div
                v-for="candidate in marketEmployees"
                :key="candidate.name"
                class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div class="flex items-start gap-3">
                  <AvatarBadge
                    :icon="candidate.icon"
                    :label="candidate.name"
                    :size="46"
                    rounded="xl"
                  />
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-2">
                      <div class="truncate text-sm font-semibold text-slate-900">
                        {{ candidate.name }}
                      </div>
                      <span
                        class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600"
                      >
                        {{ candidate.role }}
                      </span>
                    </div>
                    <div class="mt-2 text-sm leading-6 text-slate-600">
                      {{ candidate.desc }}
                    </div>
                    <div class="mt-4 flex flex-wrap gap-2">
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
                <div class="mt-4 flex justify-end">
                  <RouterLink
                    class="rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-semibold text-emerald-700 transition hover:border-emerald-300 hover:bg-emerald-100"
                    to="/employees"
                  >
                    {{ candidate.price }}
                  </RouterLink>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="team" class="mt-0">
            <div class="grid gap-4 xl:grid-cols-2">
              <div
                v-for="team in presetTeams"
                :key="team.name"
                class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="text-sm font-semibold text-slate-900">{{ team.name }}</div>
                    <div class="mt-2 text-sm leading-6 text-slate-600">{{ team.desc }}</div>
                    <div class="mt-4 flex flex-wrap gap-2">
                      <span
                        v-for="tag in team.tags"
                        :key="tag"
                        class="rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-700"
                      >
                        {{ tag }}
                      </span>
                    </div>
                  </div>
                  <div
                    class="rounded-2xl bg-slate-950 px-3 py-2 text-[11px] font-semibold tracking-[0.18em] text-white"
                  >
                    TEAM
                  </div>
                </div>
                <div class="mt-4 flex justify-end">
                  <button
                    class="rounded-full border px-4 py-2 text-sm font-semibold transition"
                    :class="
                      rentedPresetTeamNames.has(team.name)
                        ? 'cursor-default border-slate-200 bg-slate-100 text-slate-500'
                        : 'border-amber-200 bg-amber-50 text-amber-700 hover:border-amber-300 hover:bg-amber-100'
                    "
                    :disabled="rentedPresetTeamNames.has(team.name)"
                    @click="rentPresetTeam(team)"
                  >
                    {{ rentedPresetTeamNames.has(team.name) ? '已加入团队中心' : team.price }}
                  </button>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AvatarBadge from '../components/common/AvatarBadge.vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { AVATAR_LIBRARY } from '../config/avatarLibrary'
import { useSimuBossStore } from '../stores/simuBoss'

const route = useRoute()
const router = useRouter()
const store = useSimuBossStore()
const marketNotice = ref('')

const marketEmployees = [
  {
    icon: AVATAR_LIBRARY[1]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '浏览器自动化特工',
    role: '工人',
    desc: '擅长网页操作、信息抓取和重复流程执行，适合处理需要浏览器交互的任务。',
    highlights: ['Playwright', 'Browser Use', '截图取证', '表单自动填充'],
    price: '￥5/月 租赁',
  },
  {
    icon: AVATAR_LIBRARY[2]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '全网情报猎手',
    role: '工人',
    desc: '会组合搜索、网页阅读和资料整理，适合做竞品、舆情和供应商搜集。',
    highlights: ['Search', '网页摘要', '线索归档', '批量对比'],
    price: '￥8/月 租赁',
  },
  {
    icon: AVATAR_LIBRARY[3]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '数据接口拆弹手',
    role: '工人',
    desc: '专攻 API 调试、脚本编排和日志排错，能把分散数据源快速打通。',
    highlights: ['API 调试', 'Python 脚本', '日志分析', '数据清洗'],
    price: '￥12/月 租赁',
  },
  {
    icon: AVATAR_LIBRARY[4]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '多模态创意经理',
    role: '经理',
    desc: '擅长把图像、文案、页面和演示材料串成完整方案，适合带创意型团队。',
    highlights: ['图像生成', '提示词编排', '演示整合', '资产统筹'],
    price: '￥15/月 租赁',
  },
]

const presetTeams = [
  {
    name: '数据采集团队',
    desc: '擅长全网搜索、网页抓取、表格整理和信息清洗，适合先把原始资料收上来再交给分析团队。',
    tags: ['Search', '网页采集', '表格归档', '数据清洗'],
    price: '￥29/月 租赁',
  },
  {
    name: 'PPT制作团队',
    desc: '负责把零散信息整理成演示文稿，覆盖大纲、页面文案、视觉排版和配图建议。',
    tags: ['PPT 大纲', '演示排版', '图文整合', '汇报包装'],
    price: '￥39/月 租赁',
  },
  {
    name: '财咖PPT制作团队',
    desc: '专门处理 Word 到 PPT 的链路：解析原始材料、组装标准 JSON，再调用渲染器生成最终 PPT。',
    tags: ['Word 转 PPT', 'JSON 组装', '模板渲染', '免费租赁'],
    price: '免费租赁',
    presetBundle: {
      employees: [
        {
          tempId: 'caika-manager',
          icon: 'CK',
          name: '财咖汇报经理',
          role: 'manager',
          tools: [],
          model: 'gpt-4o',
          activationType: 'word',
          deliverableType: 'ppt',
          prompt: '你负责把上传的 Word 材料拆解成 PPT 生产任务，安排团队成员完成 JSON 组装，并在最终渲染前做汇总校验。',
          plannerPrompt:
            '你负责把 Word 到 PPT 的生产链拆成清晰的子任务，合理分配给直属工人。前几个工人负责把 Word 整理成符合渲染器要求的 JSON 对象，最后一个工人负责调用渲染器生成 PPT。',
          synthesizerPrompt:
            '你负责汇总团队成员产出的页面结构与内容 JSON，确认其满足 PPT 渲染规范，再交给渲染工人生成最终 PPT 文件。',
          temperature: 0.4,
          maxTokens: 4096,
          requireApproval: true,
          fixedPlan: {
            summary: '将上传的 Word 材料处理成固定的 PPT 生产流程。',
            deliverable: '一份最终可下载的 PPT 文件。',
            tasks: [
              {
                id: 't1',
                title: '解析 Word 并规划 PPT 结构',
                assigneeRefId: 'caika-structure',
                task:
                  '请读取上传的 Word 材料，规划 PPT 页数、页型与每页核心标题。输出结构化 JSON，字段必须包含 slides（数组）、每页的 type、title、goal、requiredFields。',
                dependsOn: [],
                reason: '先确定整份 PPT 的页结构。',
              },
              {
                id: 't2',
                title: '提炼 Word 中的关键洞察',
                assigneeRefId: 'caika-analysis',
                task:
                  '请从上传的 Word 材料中提炼关键结论、亮点和适合放进管理层汇报的洞察。输出结构化 JSON，字段包含 insights、numbers、risks、recommendations。',
                dependsOn: [],
                reason: '为内容页提供事实和洞察支撑。',
              },
              {
                id: 't3',
                title: '组装最终的 content.json 对象',
                assigneeRefId: 'caika-content',
                task:
                  '请基于前序结构规划和洞察结果，输出一个完整、可直接用于 PPT 渲染的 content.json JSON 对象。不要生成文件，只输出 JSON 对象本身。',
                dependsOn: ['t1', 't2'],
                reason: '把结构与内容合并成最终渲染数据。',
              },
              {
                id: 't4',
                title: '渲染最终 PPT 文件',
                assigneeRefId: 'caika-renderer',
                task:
                  '请接收最终的 content.json JSON 对象，校验其结构后调用 PPT 渲染器生成最终 PPT 文件，并返回文件下载信息。',
                dependsOn: ['t3'],
                reason: '最后一步只负责把 JSON 变成 PPT 文件。',
              },
            ],
            risks: [],
            openQuestions: [],
          },
        },
        {
          tempId: 'caika-structure',
          icon: 'ST',
          name: '财咖结构工人',
          role: 'worker',
          tools: ['Docx_Outline', 'Slide_Planner', 'JSON_Schema'],
          model: 'gpt-4o',
          activationType: 'text',
          deliverableType: 'text',
          executionMode: 'llm',
          prompt:
            '你只负责一件事：把上传的 Word 内容拆成适合 PPT 的页结构。输出每页类型、页标题、核心要点和所需字段，不生成最终文件。',
          temperature: 0.4,
          maxTokens: 4096,
        },
        {
          tempId: 'caika-content',
          icon: 'WR',
          name: '财咖内容工人',
          role: 'worker',
          tools: ['Markdown_Editor', 'Slide_Copy', 'Content_Normalizer'],
          model: 'gpt-4o',
          activationType: 'text',
          deliverableType: 'text',
          executionMode: 'llm',
          prompt:
            '你只负责一件事：把页面大纲补成适合 content.json 的正文内容，确保每页标题、正文、要点和结论表达清晰。',
          temperature: 0.5,
          maxTokens: 4096,
        },
        {
          tempId: 'caika-analysis',
          icon: 'AN',
          name: '财咖分析工人',
          role: 'worker',
          tools: ['Insight_Summary', 'Meeting_Notes', 'Fact_Check'],
          model: 'gpt-4o',
          activationType: 'text',
          deliverableType: 'text',
          executionMode: 'llm',
          prompt:
            '你只负责一件事：从会议纪要或文本材料中提炼洞察、数据亮点和管理层关心的结论，并把这些内容补进 PPT JSON 所需字段。',
          temperature: 0.4,
          maxTokens: 4096,
        },
        {
          tempId: 'caika-renderer',
          icon: 'PT',
          name: '财咖PPT渲染工人',
          role: 'worker',
          tools: ['PPT_Renderer', 'JSON_Validator', 'Python_Runner'],
          model: 'gpt-4o',
          activationType: 'text',
          deliverableType: 'ppt',
          executionMode: 'ppt_renderer',
          prompt:
            '你只负责一件事：接收最终的 JSON 对象，检查它是否符合 PPT 渲染器要求，然后把该 JSON 对象直接传给 app.py，生成最终 PPT 文件。',
          temperature: 0.2,
          maxTokens: 4096,
        },
      ],
      team: {
        icon: 'CK',
        name: '财咖PPT制作团队',
        desc: 'Word 解析、JSON 组装与 PPT 渲染一体化团队',
        members: [
          {
            type: 'emp_ref',
            refId: 'caika-manager',
            children: [
              { type: 'emp_ref', refId: 'caika-structure', children: [] },
              { type: 'emp_ref', refId: 'caika-content', children: [] },
              { type: 'emp_ref', refId: 'caika-analysis', children: [] },
              { type: 'emp_ref', refId: 'caika-renderer', children: [] },
            ],
          },
        ],
      },
    },
  },
  {
    name: '印度团队',
    desc: '真人24h在线干活',
    tags: ['真人执行', '24h 在线', '多班次协作', '高频跟进'],
    price: '￥69/月 租赁',
  },
]

const rentedPresetTeamNames = computed(() => new Set(store.teams.map((item) => item.name)))

const activeTab = computed({
  get: () => (route.query.tab === 'team' ? 'team' : 'employee'),
  set: (tab) => {
    router.replace({
      path: '/market',
      query: { tab },
    })
  },
})

function clearMarketNoticeLater() {
  window.setTimeout(() => {
    marketNotice.value = ''
  }, 2600)
}

function rentPresetTeam(team) {
  if (team.presetBundle) {
    store.recruitPresetTeamBundle(team.presetBundle, { recruitMembers: false })
    marketNotice.value = `已成功租赁「${team.name}」，它会以只读团队样板进入团队中心；如需修改，请先克隆。`
    clearMarketNoticeLater()
    return
  }

  if (team.presetPayload) {
    store.ensurePresetTeam(team.presetPayload)
    marketNotice.value = `已成功租赁「${team.name}」，现在去团队中心就能看到它。`
    clearMarketNoticeLater()
    return
  }

  router.push('/teams')
}
</script>
