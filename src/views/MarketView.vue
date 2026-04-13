<template>
  <div class="flex h-full min-h-0 flex-col gap-5 p-5">
    <section class="panel flex min-h-0 flex-1 flex-col overflow-hidden">
      <div class="panel-header">
        <span>招募员工</span>
        <div class="flex items-center gap-2 text-xs">
          <button
            class="rounded-full px-3 py-1.5 font-semibold transition"
            :class="activeTab === 'employee' ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-600'"
            @click="setTab('employee')"
          >
            人才市场
          </button>
          <button
            class="rounded-full px-3 py-1.5 font-semibold transition"
            :class="activeTab === 'team' ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-600'"
            @click="setTab('team')"
          >
            团队市场
          </button>
        </div>
      </div>

      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div v-if="activeTab === 'employee'" class="grid gap-4 xl:grid-cols-2">
          <div
            v-for="candidate in marketEmployees"
            :key="candidate.name"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div class="flex items-start gap-3">
              <AvatarBadge :icon="candidate.icon" :label="candidate.name" :size="46" rounded="xl" />
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <div class="truncate text-sm font-semibold text-slate-900">{{ candidate.name }}</div>
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">
                    {{ candidate.role }}
                  </span>
                </div>
                <div class="mt-2 text-sm leading-6 text-slate-600">{{ candidate.desc }}</div>
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
              <RouterLink class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white" to="/employees">
                去员工中心使用
              </RouterLink>
            </div>
          </div>
        </div>

        <div v-else class="grid gap-4 xl:grid-cols-2">
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
              <div class="rounded-2xl bg-slate-950 px-3 py-2 text-[11px] font-semibold tracking-[0.18em] text-white">
                TEAM
              </div>
            </div>
            <div class="mt-4 flex justify-end">
              <RouterLink class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white" to="/teams">
                去团队中心使用
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AvatarBadge from '../components/common/AvatarBadge.vue'
import { AVATAR_LIBRARY } from '../config/avatarLibrary'

const route = useRoute()
const router = useRouter()

const marketEmployees = [
  {
    icon: AVATAR_LIBRARY[1]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '浏览器自动化特工',
    role: '工人',
    desc: '擅长端到端操作网页、抓取页面信息、完成后台流程录入，适合高重复流程任务。',
    highlights: ['Playwright', 'Browser Use', '截图取证', '表单自动填充'],
  },
  {
    icon: AVATAR_LIBRARY[2]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '全网情报猎手',
    role: '工人',
    desc: '会主动组合搜索、网页阅读和资料整理能力，适合做竞品、舆情、供应商搜集。',
    highlights: ['Search', '网页摘要', '线索归档', '批量对比'],
  },
  {
    icon: AVATAR_LIBRARY[3]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '数据接口拆弹手',
    role: '工人',
    desc: '专攻 API 调试、脚本编排与日志排错，能把分散数据源快速打通成稳定流程。',
    highlights: ['API 调试', 'Python 脚本', '日志分析', '数据清洗'],
  },
  {
    icon: AVATAR_LIBRARY[4]?.value || AVATAR_LIBRARY[0]?.value || 'DE',
    name: '多模态创意经理',
    role: '经理',
    desc: '擅长把图片、文案、页面和演示材料串成一个完整方案，适合带创意生产型团队。',
    highlights: ['图像生成', '提示词编排', '演示整合', '资产统筹'],
  },
]

const presetTeams = [
  {
    name: '数据采集团队',
    desc: '擅长全网搜索、网页抓取、表格整理和信息清洗，适合先把原始资料收上来再交给分析团队。',
    tags: ['Search', '网页采集', '表格归档', '数据清洗'],
  },
  {
    name: 'ppt制作团队',
    desc: '负责把零散信息整理成演示文稿，覆盖大纲、页面文案、视觉排版和配图建议。',
    tags: ['PPT 大纲', '演示排版', '图文整合', '汇报包装'],
  },
  {
    name: '印度团队',
    desc: '真人24h在线干活',
    tags: ['真人执行', '24h 在线', '多班次协作', '高频跟进'],
  },
]

const activeTab = computed(() => (route.query.tab === 'team' ? 'team' : 'employee'))

function setTab(tab) {
  router.replace({
    path: '/market',
    query: { tab },
  })
}
</script>
