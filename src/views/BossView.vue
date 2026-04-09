<template>
  <div class="flex h-full min-h-0 gap-4 p-4">
    <aside
      class="panel flex min-h-0 flex-col overflow-hidden transition-all duration-200"
      :class="leftSidebarCollapsed ? 'w-14' : 'w-[260px] xl:w-[280px]'"
    >
      <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div v-if="!leftSidebarCollapsed" class="text-sm font-semibold text-slate-700">{{ ui.approvals }}</div>
        <button
          class="rounded-lg border border-slate-200 px-2 py-1 text-xs font-semibold text-slate-500 transition hover:border-brand-300 hover:text-brand-600"
          @click="leftSidebarCollapsed = !leftSidebarCollapsed"
        >
          {{ leftSidebarCollapsed ? ui.expand : ui.collapse }}
        </button>
      </div>
      <div
        v-if="leftSidebarCollapsed"
        class="flex flex-1 items-center justify-center px-2 text-[11px] font-semibold tracking-[0.18em] text-slate-400 [writing-mode:vertical-rl]"
      >
        {{ ui.approvals }}
      </div>
      <template v-else>
      <div class="scrollbar-thin min-h-0 flex-[0.45] overflow-y-auto p-4">
        <div v-if="!runtime.approvals.length" class="pt-10 text-center text-xs text-slate-400">
          {{ ui.noApprovals }}
        </div>
        <button
          v-for="approval in runtime.approvals"
          :key="approval.id"
          class="mb-3 w-full rounded-xl border border-amber-200 border-l-4 border-l-amber-400 bg-white p-3 text-left shadow-sm"
          @click="selectedApproval = approval"
        >
          <div class="text-sm font-semibold text-slate-800">{{ approval.task }}</div>
          <div class="mt-1 text-xs text-slate-500">{{ ui.approver }}{{ approval.managerName }}</div>
        </button>
      </div>

      <div class="border-t border-slate-200 bg-slate-50">
        <div class="panel-header">{{ ui.deliveries }}</div>
      </div>
      <div class="scrollbar-thin min-h-0 flex-[0.55] overflow-y-auto p-4">
        <div v-if="!runtime.deliveries.length" class="pt-10 text-center text-xs text-slate-400">
          {{ ui.noDeliveries }}
        </div>
        <button
          v-for="delivery in runtime.deliveries"
          :key="delivery.id"
          class="mb-3 w-full rounded-xl border border-slate-200 border-l-4 border-l-emerald-500 bg-white p-3 text-left shadow-sm"
          @click="selectedDelivery = delivery"
        >
          <div class="text-sm font-semibold text-slate-800">{{ delivery.task }} - result.md</div>
          <div class="mt-1 text-xs text-slate-500">{{ ui.processor }}{{ delivery.sender }}</div>
        </button>
      </div>
      </template>
    </aside>

    <section class="panel flex min-w-0 flex-1 flex-col overflow-hidden">
      <div class="flex items-center border-b border-slate-200 bg-slate-100">
        <button
          v-for="floor in store.floors"
          :key="floor.id"
          class="border-r border-slate-200 px-4 py-2 text-sm font-semibold"
          :class="currentFloorId === floor.id ? 'bg-white text-brand-600' : 'text-slate-500'"
          @click="currentFloorId = floor.id"
        >
          {{ floor.name }}
        </button>
        <div class="ml-auto px-4 text-xs text-slate-500">
          {{ ui.zoom }} {{ Math.round(view.scale * 100) }}%
        </div>
      </div>

      <div class="min-h-0 flex-1 overflow-hidden bg-[#f8fafc] p-4">
        <div
          v-if="!currentPlacements.length"
          class="flex h-full min-h-[360px] items-center justify-center rounded-3xl border border-dashed border-slate-300 bg-white text-center text-slate-400"
        >
          <div>
            <div class="text-lg font-semibold">{{ ui.empty }}</div>
            <div class="mt-2 text-sm">{{ ui.emptyHint }}</div>
          </div>
        </div>

        <div v-else class="flex h-full min-h-0 flex-col">
          <div
            ref="viewportRef"
            class="relative min-h-0 flex-1 overflow-hidden rounded-3xl border border-slate-200 bg-white"
            @mousedown="startPan"
            @wheel.prevent="handleWheel"
          >
            <div class="absolute inset-0" :style="worldStyle">
              <div
                class="relative bg-[radial-gradient(circle_at_1px_1px,#cbd5e1_1.2px,transparent_0)] bg-[length:24px_24px] bg-white"
                :style="{ width: `${canvasWidth}px`, height: `${canvasHeight}px` }"
              >
                <div class="absolute inset-0" :style="canvasOffsetStyle">
                  <PlacementNode
                    v-for="placement in currentPlacements"
                    :key="placement.id"
                    :placement="placement"
                    mode="runtime"
                    absolute
                    @task-drop="dropTaskToPlacement"
                    @select="selectedEntity = $event"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        class="border-t border-black bg-slate-950 transition-all duration-200"
        :class="logsCollapsed ? 'h-[52px]' : 'h-[220px]'"
      >
        <div class="flex items-center justify-between border-b border-black px-4 py-3 text-sm font-semibold text-slate-400">
          <div>&gt;_ {{ ui.logs }}</div>
          <button
            class="rounded-lg border border-slate-700 px-2 py-1 text-[11px] font-semibold text-slate-400 transition hover:border-slate-500 hover:text-white"
            @click="logsCollapsed = !logsCollapsed"
          >
            {{ logsCollapsed ? ui.expand : ui.collapse }}
          </button>
        </div>
        <div v-if="!logsCollapsed" class="scrollbar-thin h-[168px] overflow-y-auto px-4 py-3 font-mono text-xs">
          <div
            v-for="entry in runtime.logs"
            :key="entry.id"
            class="mb-1"
            :class="logClass(entry.role)"
          >
            <span class="mr-2 text-blue-400">{{ formatLogTime(entry.time) }}</span>
            <span>{{ prefixForRole(entry.role) }} {{ entry.text }}</span>
          </div>
        </div>
      </div>
    </section>

    <aside
      class="panel flex min-h-0 flex-col overflow-hidden transition-all duration-200"
      :class="rightSidebarCollapsed ? 'w-14' : 'w-[280px] xl:w-[340px]'"
    >
      <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div v-if="!rightSidebarCollapsed" class="text-sm font-semibold text-slate-700">{{ ui.taskCenter }}</div>
        <button
          class="rounded-lg border border-slate-200 px-2 py-1 text-xs font-semibold text-slate-500 transition hover:border-brand-300 hover:text-brand-600"
          @click="rightSidebarCollapsed = !rightSidebarCollapsed"
        >
          {{ rightSidebarCollapsed ? ui.expand : ui.collapse }}
        </button>
      </div>
      <div
        v-if="rightSidebarCollapsed"
        class="flex flex-1 items-center justify-center px-2 text-[11px] font-semibold tracking-[0.18em] text-slate-400 [writing-mode:vertical-rl]"
      >
        {{ ui.taskCenter }}
      </div>
      <template v-else>
      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div class="mb-3 text-[11px] font-semibold tracking-[0.18em] text-slate-400">
          {{ ui.taskCards }}
        </div>
        <div v-if="!taskCards.length" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-xs text-slate-400">
          {{ ui.noTasks }}
        </div>
        <div
          v-for="task in taskCards"
          :key="task.id"
          class="mb-3 cursor-grab rounded-xl border border-amber-200 border-l-4 border-l-amber-400 bg-white px-3 py-3 text-sm shadow-sm"
          draggable="true"
          @dragstart="dragTask = task"
        >
          <div class="font-semibold text-slate-800">{{ task.title }}</div>
          <div class="mt-1 text-[11px] text-slate-500">{{ ui.taskDragHint }}</div>
        </div>
      </div>
      <div class="border-t border-slate-200 bg-slate-50 p-4">
        <button
          class="mb-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700"
          @click="longTaskModalOpen = true"
        >
          {{ ui.longTask }}
        </button>
        <div class="flex gap-2">
          <input
            v-model="newTaskInput"
            class="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
            :placeholder="ui.quickTaskPlaceholder"
            @keydown.enter="addQuickTask"
          />
          <button
            class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white"
            @click="addQuickTask"
          >
            {{ ui.push }}
          </button>
        </div>
      </div>
      </template>
    </aside>

    <div
      v-if="longTaskModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
    >
      <div class="w-full max-w-3xl rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div class="text-lg font-semibold text-slate-900">{{ ui.longTaskTitle }}</div>
          <button class="text-xl text-slate-400" @click="closeLongTaskModal">x</button>
        </div>
        <div class="p-5">
          <textarea
            v-model="longTaskInput"
            rows="12"
            class="w-full rounded-2xl border border-slate-200 px-4 py-4 text-sm outline-none focus:border-brand-500"
            :placeholder="ui.longTaskPlaceholder"
          />
        </div>
        <div class="flex items-center justify-end gap-3 border-t border-slate-200 px-5 py-4">
          <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="closeLongTaskModal">
            {{ ui.cancel }}
          </button>
          <button class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white" @click="addLongTask">
            {{ ui.createTask }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="selectedApproval"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
    >
      <div class="flex h-[80vh] w-full max-w-4xl flex-col rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div>
            <div class="text-lg font-semibold text-slate-900">{{ selectedApproval.task }}</div>
            <div class="mt-1 text-xs text-slate-500">
              {{ ui.approver }}{{ selectedApproval.managerName }}
            </div>
          </div>
          <button class="text-xl text-slate-400" @click="selectedApproval = null">x</button>
        </div>
        <div class="scrollbar-thin flex-1 overflow-y-auto bg-slate-50 p-5">
          <div class="rounded-2xl border border-slate-200 bg-white p-4">
            <div class="mb-3 text-sm font-semibold text-slate-700">{{ ui.decompositionTitle }}</div>
            <div v-if="selectedApproval.plan" class="space-y-4">
              <div class="grid gap-3 md:grid-cols-3">
                <div class="rounded-xl bg-slate-50 p-4">
                  <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">任务数</div>
                  <div class="mt-2 text-2xl font-semibold text-slate-900">
                    {{ selectedApproval.plan.tasks?.length || 0 }}
                  </div>
                </div>
                <div class="rounded-xl bg-slate-50 p-4">
                  <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">参与下属</div>
                  <div class="mt-2 text-2xl font-semibold text-slate-900">
                    {{ approvalAssigneeCount(selectedApproval.plan) }}
                  </div>
                </div>
                <div class="rounded-xl bg-slate-50 p-4">
                  <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">依赖关系</div>
                  <div class="mt-2 text-2xl font-semibold text-slate-900">
                    {{ approvalDependencyCount(selectedApproval.plan) }}
                  </div>
                </div>
              </div>
              <div class="rounded-xl bg-slate-50 p-4">
                <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">目标理解</div>
                <div class="mt-2 text-sm leading-6 text-slate-700">{{ selectedApproval.plan.summary }}</div>
              </div>
              <div class="rounded-xl bg-slate-50 p-4">
                <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">最终交付</div>
                <div class="mt-2 text-sm leading-6 text-slate-700">{{ selectedApproval.plan.deliverable }}</div>
              </div>
              <div class="rounded-xl border border-slate-200">
                <div class="border-b border-slate-200 px-4 py-3 text-xs font-semibold tracking-[0.18em] text-slate-400">
                  任务分配
                </div>
                <div class="divide-y divide-slate-100">
                  <div
                    v-for="(item, index) in selectedApproval.plan.tasks"
                    :key="item.id || index"
                    class="px-4 py-4"
                  >
                    <div class="flex items-start justify-between gap-4">
                      <div>
                        <div class="text-sm font-semibold text-slate-900">
                          {{ index + 1 }}. {{ item.title }}
                        </div>
                        <div class="mt-1 text-xs text-slate-500">
                          分配给 {{ item.assigneeName || item.assigneeId }}
                        </div>
                      </div>
                      <div class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                        {{ normalizeDependencyList(item.dependsOn).length ? `依赖 ${normalizeDependencyList(item.dependsOn).length} 项` : '无依赖' }}
                      </div>
                    </div>
                    <div class="mt-3 text-sm leading-6 text-slate-700">{{ item.task }}</div>
                    <div class="mt-3 text-xs text-slate-500">
                      分配理由：{{ item.reason || '未说明' }}
                    </div>
                    <div class="mt-1 text-xs text-slate-500">
                      依赖任务：{{ normalizeDependencyList(item.dependsOn).length ? normalizeDependencyList(item.dependsOn).join('、') : '无' }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="grid gap-4 md:grid-cols-2">
                <div class="rounded-xl bg-slate-50 p-4">
                  <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">风险</div>
                  <div class="mt-2 text-sm leading-6 text-slate-700">
                    {{ selectedApproval.plan.risks?.length ? selectedApproval.plan.risks.join('；') : '无' }}
                  </div>
                </div>
                <div class="rounded-xl bg-slate-50 p-4">
                  <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">待确认</div>
                  <div class="mt-2 text-sm leading-6 text-slate-700">
                    {{ selectedApproval.plan.openQuestions?.length ? selectedApproval.plan.openQuestions.join('；') : '无' }}
                  </div>
                </div>
              </div>
            </div>
            <pre
              v-else
              class="scrollbar-thin max-h-[42vh] overflow-auto whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm text-slate-700"
              >{{ selectedApproval.draft || ui.noDraft }}</pre
            >
          </div>
          <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div class="mb-2 text-sm font-semibold text-slate-700">{{ ui.feedbackLabel }}</div>
            <textarea
              v-model="selectedApproval.feedback"
              rows="4"
              class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-brand-500"
              :placeholder="ui.feedbackPlaceholder"
            />
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 border-t border-slate-200 bg-white px-5 py-4">
          <button
            class="rounded-xl border border-rose-200 px-4 py-2 text-sm font-semibold text-rose-500"
            @click="rejectApproval(selectedApproval)"
          >
            {{ ui.reject }}
          </button>
          <button
            class="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white"
            @click="approveApproval(selectedApproval)"
          >
            {{ ui.approve }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="selectedDelivery"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
    >
      <div class="w-full max-w-4xl rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div class="text-lg font-semibold text-slate-900">{{ selectedDelivery.task }}</div>
          <button class="text-xl text-slate-400" @click="selectedDelivery = null">x</button>
        </div>
        <pre
          class="scrollbar-thin max-h-[65vh] overflow-auto whitespace-pre-wrap bg-slate-50 p-5 text-sm text-slate-700"
          >{{ selectedDelivery.result }}</pre
        >
      </div>
    </div>

    <div
      v-if="selectedEntity"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
    >
      <div class="flex h-[80vh] w-full max-w-3xl flex-col rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div class="text-lg font-semibold text-slate-900">{{ displayName(selectedEntity) }}</div>
          <button class="text-xl text-slate-400" @click="selectedEntity = null">x</button>
        </div>
        <div class="scrollbar-thin flex-1 overflow-y-auto p-5">
            <div class="grid gap-3">
              <div class="grid grid-cols-[120px_1fr] border-b border-slate-200 pb-3 text-sm">
                <div class="font-semibold text-slate-500">{{ ui.statusLabel }}</div>
              <div>{{ selectedEntityStatusText }}</div>
              </div>
              <div class="grid grid-cols-[120px_1fr] border-b border-slate-200 pb-3 text-sm">
                <div class="font-semibold text-slate-500">{{ ui.positionLabel }}</div>
              <div>{{ selectedEntity.x || 0 }}, {{ selectedEntity.y || 0 }}</div>
              </div>
              <div v-if="selectedEntityApprovals.length" class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div class="mb-3 text-sm font-semibold text-slate-700">拆解与审批</div>
                <div
                  v-for="approval in selectedEntityApprovals"
                  :key="approval.id"
                  class="mb-3 rounded-xl bg-white p-3 last:mb-0"
                >
                  <div class="text-sm font-semibold text-slate-900">{{ approval.task }}</div>
                  <div class="mt-1 text-xs text-slate-500">拆解方：{{ approval.managerName }}</div>
                  <div class="mt-2 text-sm leading-6 text-slate-700 whitespace-pre-wrap">{{ approval.draft }}</div>
                </div>
              </div>
              <div v-if="selectedEntityQueue.length" class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div class="mb-3 text-sm font-semibold text-slate-700">待办队列</div>
                <div
                  v-for="item in selectedEntityQueue"
                  :key="item.id"
                  class="mb-2 rounded-lg bg-white px-3 py-2 text-sm text-slate-700 last:mb-0"
                >
                  {{ item.task }}
                </div>
              </div>
              <div v-if="selectedEntityTimeline.length" class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div class="mb-3 text-sm font-semibold text-slate-700">任务时间线</div>
                <div class="space-y-3">
                  <div
                    v-for="entry in selectedEntityTimeline"
                    :key="entry.id"
                    class="rounded-xl bg-white px-3 py-3"
                  >
                    <div class="flex items-center justify-between gap-4">
                      <div class="text-xs font-semibold uppercase tracking-[0.18em]" :class="logClass(entry.role)">
                        {{ prefixForRole(entry.role) }}
                      </div>
                      <div class="text-xs text-slate-400">{{ formatLogTime(entry.time) }}</div>
                    </div>
                    <div class="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{{ entry.text }}</div>
                  </div>
                </div>
              </div>
              <div class="rounded-xl bg-slate-950 p-4">
                <div class="mb-3 text-sm font-semibold text-amber-400">{{ ui.stream }}</div>
                <pre
                class="scrollbar-thin max-h-[32vh] overflow-auto whitespace-pre-wrap font-mono text-xs text-slate-200"
                >{{ selectedEntityStreamText }}</pre
              >
              </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import PlacementNode from '../components/canvas/PlacementNode.vue'
import { DEFAULT_SYSTEM_PROMPTS } from '../config/prompts'
import { findRootManagerNode, flattenWorkerNodes, resolveNode } from '../utils/tree'
import { useRuntimeStore } from '../stores/runtime'
import { useSimuBossStore } from '../stores/simuBoss'

const ui = {
  approvals: '\u4eba\u5de5\u5ba1\u6279\u5217\u961f',
  noApprovals: '\u5f53\u524d\u65e0\u9700\u8981\u5ba1\u6279\u7684\u4efb\u52a1',
  approver: '\u62c6\u89e3\u65b9\uff1a',
  feedbackLabel: '\u9a73\u56de\u610f\u89c1',
  feedbackPlaceholder: '\u5ba1\u6279\u9a73\u56de\u65f6\u586b\u5199\u610f\u89c1...',
  reject: '\u9a73\u56de\u91cd\u505a',
  approve: '\u5ba1\u6279\u901a\u8fc7',
  decompositionTitle: '\u4efb\u52a1\u62c6\u89e3\u8349\u6848',
  deliveries: '\u4ea4\u4ed8\u6210\u679c\u533a',
  noDeliveries: '\u5f53\u524d\u6682\u65e0\u4ea4\u4ed8\u6210\u679c',
  processor: '\u5904\u7406\u65b9\uff1a',
  zoom: '\u7f29\u653e',
  empty: '\u8fd9\u5c42\u8fd8\u6ca1\u6709\u5df2\u4fdd\u5b58\u7684\u5e03\u7f6e',
  emptyHint: '\u53bb\u697c\u5c42\u5e03\u7f6e\u9875\u9762\u62d6\u5165\u5e76\u4fdd\u5b58\u5373\u53ef\u3002',
  logs: '\u7cfb\u7edf\u8fd0\u884c\u65e5\u5fd7',
  taskCenter: '\u4efb\u52a1\u53d1\u5e03\u4e2d\u5fc3',
  createTask: '\u521b\u5efa\u4efb\u52a1',
  cancel: '\u53d6\u6d88',
  longTask: '\u65b0\u5efa\u957f\u4efb\u52a1',
  longTaskTitle: '\u65b0\u5efa\u957f\u4efb\u52a1',
  longTaskPlaceholder:
    '\u5728\u8fd9\u91cc\u8f93\u5165\u5b8c\u6574\u7684\u4efb\u52a1\u80cc\u666f\u3001\u76ee\u6807\u3001\u8981\u6c42\u548c\u9650\u5236...',
  quickTaskPlaceholder: '\u5feb\u6377\u6dfb\u52a0\u77ed\u4efb\u52a1...',
  push: '\u63a8\u9001',
  taskCards: '\u4efb\u52a1\u5361\u7247',
  taskDragHint: '\u62d6\u5230\u5bf9\u5e94\u5361\u7247\u4e0a\u5373\u53ef\u4e0b\u53d1',
  noTasks: '\u6682\u65e0\u5f85\u4e0b\u53d1\u4efb\u52a1',
  statusLabel: '\u72b6\u6001',
  positionLabel: '\u5750\u6807',
  stream: '\u5b9e\u65f6\u6d41',
  idle: '\u7a7a\u95f2',
  noDraft: '\u6682\u65e0\u62c6\u89e3\u8349\u6848',
  collapse: '\u6536\u8d77',
  expand: '\u5c55\u5f00',
}

const DEFAULT_MANAGER_PLANNER = DEFAULT_SYSTEM_PROMPTS.managerPlanner
const DEFAULT_MANAGER_SYNTHESIZER = DEFAULT_SYSTEM_PROMPTS.managerSynthesizer
const DEFAULT_WORKER_PROMPT = DEFAULT_SYSTEM_PROMPTS.worker

const store = useSimuBossStore()
const runtime = useRuntimeStore()
const currentFloorId = ref(store.floors[0]?.id || 'floor-1')
const viewportRef = ref(null)
const panState = ref(null)
const view = ref({ x: 32, y: 24, scale: 1 })
const leftSidebarCollapsed = ref(false)
const rightSidebarCollapsed = ref(false)
const logsCollapsed = ref(true)
const dragTask = ref('')
const newTaskInput = ref('')
const longTaskModalOpen = ref(false)
const longTaskInput = ref('')
const selectedApproval = ref(null)
const selectedDelivery = ref(null)
const selectedEntity = ref(null)
const processingSet = new Set()

const taskCards = ref([
  { id: crypto.randomUUID(), title: '\u65b0\u80fd\u6e90\u7ade\u54c1\u6df1\u5ea6\u5206\u6790\u62a5\u544a' },
])

const currentPlacements = computed(() => store.floorAssignments[currentFloorId.value] || [])
const selectedEntitySourceId = computed(() => getEntityInfoSourceId(selectedEntity.value))
const selectedEntityStatusText = computed(() => {
  if (!selectedEntity.value) return ui.idle
  return (
    runtime.teamStatuses[selectedEntitySourceId.value]?.text ||
    runtime.teamStatuses[selectedEntity.value.id]?.text ||
    ui.idle
  )
})
const selectedEntityQueue = computed(() => {
  if (!selectedEntity.value) return []
  return runtime.teamQueues[selectedEntitySourceId.value] || runtime.teamQueues[selectedEntity.value.id] || []
})
const selectedEntityApprovals = computed(() => {
  if (!selectedEntity.value) return []
  return runtime.approvals.filter(
    (item) =>
      item.runtimeNodeId === selectedEntitySourceId.value || item.runtimeNodeId === selectedEntity.value.id,
  )
})
const selectedEntityStreamText = computed(() => {
  if (!selectedEntity.value) return '\u65e0\u5b9e\u65f6\u8f93\u51fa'
  const sourceId = selectedEntitySourceId.value
  const streamKeys = [sourceId, `${sourceId}:dispatch`, `${sourceId}:synthesis`, selectedEntity.value.id]
  const chunks = streamKeys
    .map((key) => {
      const content = runtime.workerStates[key]?.streamedContent
      if (!content) return ''
      if (key === sourceId) return `main\n${content}`
      return `${key.replace(`${sourceId}:`, '')}\n${content}`
    })
    .filter(Boolean)
  return chunks.join('\n\n') || '\u65e0\u5b9e\u65f6\u8f93\u51fa'
})
const selectedEntityTimeline = computed(() => {
  if (!selectedEntity.value) return []
  const sourceId = selectedEntitySourceId.value
  return runtime.logs.filter(
    (entry) =>
      entry.entityId === sourceId ||
      entry.entityId === selectedEntity.value.id ||
      entry.workerKey === sourceId ||
      entry.workerKey === selectedEntity.value.id ||
      String(entry.workerKey || '').startsWith(`${sourceId}:`),
  )
})
const contentBounds = computed(() => getContentBounds(currentPlacements.value))
const canvasWidth = computed(() => Math.max(720, Math.ceil(contentBounds.value.width)))
const canvasHeight = computed(() => Math.max(520, Math.ceil(contentBounds.value.height)))
const canvasOffsetStyle = computed(() => ({
  transform: `translate(${contentBounds.value.offsetX}px, ${contentBounds.value.offsetY}px)`,
  transformOrigin: '0 0',
}))
const worldStyle = computed(() => ({
  transform: `translate(${view.value.x}px, ${view.value.y}px) scale(${view.value.scale})`,
  transformOrigin: '0 0',
}))

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value))
}

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

function getTeamHierarchyRoots(placement) {
  if (placement.kind !== 'team') return []
  return buildTreeFromRaw(store.teamMap[placement.refId]?.members || [], placement.id, 'team')
}

function getTeamLeadPlacementId(placement) {
  if (placement.kind !== 'team') return null
  const roots = getTeamHierarchyRoots(placement)
  if (roots.length === 1 && roots[0].kind === 'manager') return roots[0].id
  return roots.find((item) => item.kind === 'manager')?.id || null
}

function setPlacementStatus(placement, state, text) {
  runtime.setTeamStatus(placement.id, state, text)
  const leadId = getTeamLeadPlacementId(placement)
  if (leadId) runtime.setTeamStatus(leadId, state, text)
}

function displayName(placement) {
  if (placement.kind === 'team') return store.teamMap[placement.refId]?.name || placement.name
  return store.employeeMap[placement.refId]?.name || placement.name
}

function kindLabelForPlacement(placement) {
  return {
    team: '\u56e2\u961f',
    manager: '\u7ecf\u7406',
    employee: '\u5de5\u4eba',
  }[placement.kind] || '\u5355\u5143'
}

function flattenNestedWorkers(list, bucket = []) {
  ;(list || []).forEach((item) => {
    if (item.kind === 'employee') {
      const emp = store.employeeMap[item.refId]
      if (emp) bucket.push(emp)
    }
    if (item.children?.length) flattenNestedWorkers(item.children, bucket)
  })
  return bucket
}

function getManagerEntity(placement) {
  if (placement.kind === 'team') {
    const team = store.teamMap[placement.refId]
    return findRootManagerNode(team?.members || [], store.employees, store.teams)
  }
  if (placement.kind === 'manager') {
    return store.employeeMap[placement.refId]
  }
  return null
}

function getPlacementContext(placement) {
  if (placement.kind === 'employee') {
    const employee = store.employeeMap[placement.refId]
    return {
      workerName: employee?.name || displayName(placement),
      role: employee?.role || 'worker',
      workerPrompt: employee?.prompt || DEFAULT_WORKER_PROMPT,
      requireApproval: false,
      tools: employee?.tools || [],
    }
  }

  const manager = getManagerEntity(placement)
  const workers =
    placement.kind === 'team'
      ? flattenWorkerNodes(
          store.teamMap[placement.refId]?.members || [],
          store.employees,
          store.teams,
          [],
        )
      : flattenNestedWorkers(placement.children || [])

  return {
    workerName: manager?.name || displayName(placement),
    role: 'manager',
    plannerPrompt: manager?.plannerPrompt || manager?.prompt || DEFAULT_MANAGER_PLANNER,
    synthesizerPrompt:
      manager?.synthesizerPrompt || manager?.prompt || DEFAULT_MANAGER_SYNTHESIZER,
    requireApproval: manager ? manager.requireApproval !== false : false,
    tools: [...new Set(workers.flatMap((item) => item.tools || []))],
  }
}

function getManagedChildren(placement) {
  if (placement.kind === 'manager') return placement.children || []
  if (placement.kind !== 'team') return []

  const roots = getTeamHierarchyRoots(placement)
  if (roots.length === 1 && roots[0].kind === 'manager') {
    return roots[0].children || []
  }
  return roots
}

function createTaskCard(title) {
  return { id: crypto.randomUUID(), title }
}

function estimateRootWidth(placement) {
  return placement.kind === 'team' ? 560 : placement.kind === 'manager' ? 320 : 188
}

function estimateManagerCardHeight(children = []) {
  if (!children.length) return 132
  const childGap = 12
  const childSectionPadding = 86
  const childrenHeight =
    children.reduce((sum, child) => sum + estimatePlacementHeight(child), 0) +
    childGap * Math.max(0, children.length - 1)
  return 132 + childSectionPadding + childrenHeight
}

function estimateHierarchyBranchHeight(node) {
  if (!node) return 84
  const baseHeight = 84
  const children = node.children || []
  if (!children.length) return baseHeight

  const columns = 2
  const rowGap = 16
  const connectorHeight = 32
  let rowsHeight = 0

  for (let index = 0; index < children.length; index += columns) {
    const row = children.slice(index, index + columns)
    rowsHeight += Math.max(...row.map((child) => estimateHierarchyBranchHeight(child)))
  }

  const rowCount = Math.ceil(children.length / columns)
  return baseHeight + connectorHeight + rowsHeight + rowGap * Math.max(0, rowCount - 1)
}

function estimateTeamCardHeight(placement) {
  const roots = getTeamHierarchyRoots(placement)
  if (!roots.length) return 176
  const rootGap = 20
  const treePadding = 92
  const treeHeight =
    roots.reduce((sum, root) => sum + estimateHierarchyBranchHeight(root), 0) +
    rootGap * Math.max(0, roots.length - 1)
  return 176 + treePadding + treeHeight
}

function estimatePlacementHeight(placement) {
  if (!placement) return 88
  if (placement.kind === 'employee') return 88
  if (placement.kind === 'manager') return estimateManagerCardHeight(placement.children || [])
  if (placement.kind === 'team') return estimateTeamCardHeight(placement)
  return 88
}

function getContentBounds(placements) {
  if (!placements?.length) {
    return {
      minX: 0,
      minY: 0,
      maxX: 720,
      maxY: 520,
      width: 720,
      height: 520,
      offsetX: 64,
      offsetY: 64,
    }
  }

  const outerPadding = 96
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity

  placements.forEach((placement) => {
    const x = Number(placement.x || 0)
    const y = Number(placement.y || 0)
    const width = estimateRootWidth(placement)
    const height = estimatePlacementHeight(placement)
    minX = Math.min(minX, x)
    minY = Math.min(minY, y)
    maxX = Math.max(maxX, x + width)
    maxY = Math.max(maxY, y + height)
  })

  const width = maxX - minX + outerPadding * 2
  const height = maxY - minY + outerPadding * 2

  return {
    minX,
    minY,
    maxX,
    maxY,
    width,
    height,
    offsetX: outerPadding - minX,
    offsetY: outerPadding - minY,
  }
}

function addQuickTask() {
  const title = newTaskInput.value.trim()
  if (!title) return
  taskCards.value.unshift(createTaskCard(title))
  newTaskInput.value = ''
}

function addLongTask() {
  const title = longTaskInput.value.trim()
  if (!title) return
  taskCards.value.unshift(createTaskCard(title))
  closeLongTaskModal()
}

function closeLongTaskModal() {
  longTaskModalOpen.value = false
  longTaskInput.value = ''
}

function removeTaskCard(taskId) {
  taskCards.value = taskCards.value.filter((item) => item.id !== taskId)
}

function restoreTaskCard(taskCard) {
  if (!taskCard?.id || taskCards.value.some((item) => item.id === taskCard.id)) return
  taskCards.value.unshift(taskCard)
}

function isExecutionError(text) {
  return String(text || '').startsWith('\u6267\u884c\u5f02\u5e38')
}

function getStreamText(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  const streamKeys = [sourceId, `${sourceId}:dispatch`, `${sourceId}:synthesis`, placement.id]
  const chunks = streamKeys
    .map((key) => {
      const content = runtime.workerStates[key]?.streamedContent
      if (!content) return ''
      if (key === sourceId) return `main\n${content}`
      return `${key.replace(`${sourceId}:`, '')}\n${content}`
    })
    .filter(Boolean)
  return chunks.join('\n\n') || '\u65e0\u5b9e\u65f6\u8f93\u51fa'
}

function getEntityInfoSourceId(placement) {
  return placement?.infoSourceId || placement?.id
}

function getEntityStatusText(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  return runtime.teamStatuses[sourceId]?.text || runtime.teamStatuses[placement.id]?.text || ui.idle
}

function getEntityQueue(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  return runtime.teamQueues[sourceId] || runtime.teamQueues[placement.id] || []
}

function getEntityApprovals(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  return runtime.approvals.filter(
    (item) => item.runtimeNodeId === sourceId || item.runtimeNodeId === placement.id,
  )
}

function dropTaskToPlacement(placement) {
  if (!dragTask.value?.title) return
  assignTask(placement, dragTask.value)
  dragTask.value = ''
}

function assignTask(placement, taskCard) {
  runtime.ensureTeamQueue(placement.id)
  runtime.enqueueTask(placement.id, taskCard.title, {
    placementId: placement.id,
    sourceTask: cloneValue(taskCard),
  })
  removeTaskCard(taskCard.id)
  runtime.log('sys', `\u4efb\u52a1\u5df2\u4e0b\u53d1\u7ed9 [${displayName(placement)}] -> ${taskCard.title}`, {
    entityId: placement.id,
  })
  processQueue(placement)
}

async function processQueue(placement) {
  if (processingSet.has(placement.id)) return
  const queue = runtime.ensureTeamQueue(placement.id)
  if (!queue.length) {
    setPlacementStatus(placement, 'idle', ui.idle)
    return
  }

  processingSet.add(placement.id)
  const current = queue[0]
  const context = getPlacementContext(placement)

  if (context.role === 'manager' && context.requireApproval) {
    const success = await generateApprovalDraft(placement, current.task)
    if (!success && (runtime.teamQueues[placement.id] || []).length) {
      processQueue(placement)
    }
    return
  }

  await executeTask(placement, current.task, '', {
    queued: true,
    deliverToBoss: true,
    sourceTask: current.payload?.sourceTask,
  })
}

async function rejectApproval(approval) {
  selectedApproval.value = null
  runtime.resolveApproval(approval.id)
  setPlacementStatus(approval.nodeSnapshot, 'blocked', '\u5f85\u91cd\u65b0\u89c4\u5212')
  await generateApprovalDraft(
    approval.nodeSnapshot,
    approval.task,
    approval.feedback || '\u8bf7\u6309 Boss \u610f\u89c1\u91cd\u65b0\u62c6\u89e3',
  )
}

async function approveApproval(approval) {
  selectedApproval.value = null
  runtime.resolveApproval(approval.id)
  await executeTask(approval.nodeSnapshot, approval.task, approval.draft, {
    queued: true,
    deliverToBoss: true,
    sourceTask: approval.sourceTask,
    approvedPlan: approval.plan || null,
  })
}

async function generateApprovalDraft(placement, task, feedback = '') {
  const context = getPlacementContext(placement)
  setPlacementStatus(placement, 'working', '\u6b63\u5728\u751f\u6210\u62c6\u89e3')
  runtime.log(
    'mgr',
    `[${context.workerName}] \u6b63\u5728\u751f\u6210\u4efb\u52a1\u62c6\u89e3${feedback ? ' / \u5df2\u5e26\u5165 Boss \u610f\u89c1' : ''}`,
    { entityId: placement.id },
  )

  const children = getManagedChildren(placement)
  const childRoster = formatSubordinateRoster(children)
  const planningGuidance = getTaskPlanningGuidance(task, children)

  const rawPlan = await runtime.runWorkerTask({
    workerKey: placement.id,
    workerName: context.workerName,
    systemPrompt: context.plannerPrompt,
    entityId: placement.id,
    userPrompt: `请先审阅你的直属下属，再拆解任务，不要直接执行。
总任务：${task}
${feedback ? `Boss 反馈：${feedback}\n` : ''}直属下属清单：
${childRoster}

请只输出一个 JSON 对象，不要输出 Markdown，不要输出解释文字。字段结构如下：
{
  "summary": "对总任务的目标理解",
  "deliverable": "最终交付给 Boss 的成果形态",
  "tasks": [
    {
      "id": "t1",
      "title": "子任务标题",
      "assigneeId": "直属下属id",
      "assigneeName": "直属下属姓名",
      "task": "发给该下属的完整执行指令",
      "dependsOn": [],
      "reason": "为什么分给他"
    }
  ],
  "risks": ["风险1"],
  "openQuestions": ["待确认问题1"]
}

要求：
1. tasks 至少 1 条
2. 所有 assigneeId 必须来自直属下属清单
3. dependsOn 只能引用 tasks 里的 task id
4. 如果没有风险或待确认，输出空数组
5. 如果直属下属不足以完成任务，也要输出合法 JSON，并在 risks / openQuestions 里明确说明`,
  })

  const plan = extractJsonObjectPayload(rawPlan)
  const validationError = validateApprovalPlan(plan, children)
  if (validationError) {
    runtime.log('mgr', `[${context.workerName}] 拆解计划校验失败：${validationError}`, {
      entityId: placement.id,
    })
    setPlacementStatus(placement, 'error', '拆解计划格式错误')
    const queuedTask = runtime.shiftTask(placement.id)
    processingSet.delete(placement.id)
    restoreTaskCard(queuedTask?.payload?.sourceTask || null)
    runtime.log('sys', `任务拆解失败，已退回任务列表 -> ${task}`, { entityId: placement.id })
    return false
  }

  const draft = renderApprovalPlan(plan)
  if (!draft) {
    runtime.log('mgr', `[${context.workerName}] 审批视图渲染失败，拆解结果已退回`, {
      entityId: placement.id,
    })
    setPlacementStatus(placement, 'error', '拆解结果不可读')
    const queuedTask = runtime.shiftTask(placement.id)
    processingSet.delete(placement.id)
    restoreTaskCard(queuedTask?.payload?.sourceTask || null)
    runtime.log('sys', `任务拆解失败，已退回任务列表 -> ${task}`, { entityId: placement.id })
    return false
  }

  setPlacementStatus(placement, 'blocked', '\u7b49\u5f85\u5ba1\u9605\u62c6\u89e3')
  runtime.log('mgr', `[${context.workerName}] \u5df2\u63d0\u4ea4\u62c6\u89e3\u8349\u6848\uff0c\u7b49\u5f85 Boss \u5ba1\u9605`, {
    entityId: placement.id,
  })
  runtime.createApproval({
    runtimeNodeId: placement.id,
    task,
    managerName: context.workerName,
    nodeSnapshot: cloneValue(placement),
    sourceTask: runtime.teamQueues[placement.id]?.[0]?.payload?.sourceTask || null,
    draft,
    plan,
  })
  return true
}

function extractJsonPayload(text) {
  const cleaned = String(text || '').trim()
  if (!cleaned) return null
  const fenced = cleaned.match(/```json\s*([\s\S]*?)```/i) || cleaned.match(/```\s*([\s\S]*?)```/i)
  const candidate = fenced?.[1] || cleaned
  const start = candidate.indexOf('[')
  const end = candidate.lastIndexOf(']')
  if (start === -1 || end === -1 || end < start) return null
  try {
    return JSON.parse(candidate.slice(start, end + 1))
  } catch {
    return null
  }
}

function extractJsonObjectPayload(text) {
  const cleaned = String(text || '').trim()
  if (!cleaned) return null
  const fenced =
    cleaned.match(/```json\s*([\s\S]*?)```/i) || cleaned.match(/```\s*([\s\S]*?)```/i)
  const candidate = fenced?.[1] || cleaned
  const start = candidate.indexOf('{')
  const end = candidate.lastIndexOf('}')
  if (start === -1 || end === -1 || end < start) return null
  try {
    return JSON.parse(candidate.slice(start, end + 1))
  } catch {
    return null
  }
}

function formatSubordinateRoster(children) {
  return children.length
    ? children
        .map(
          (child) =>
            `- id: ${child.id}; name: ${displayName(child)}; kind: ${kindLabelForPlacement(child)}`,
        )
        .join('\n')
    : '- 暂无直属下属'
}

function normalizeDependencyList(value) {
  return Array.isArray(value)
    ? value.map((item) => String(item || '').trim()).filter(Boolean)
    : []
}

function isSimpleBossTask(task) {
  const normalized = String(task || '').trim().toLowerCase()
  if (!normalized) return false
  if (normalized.length <= 12) return true
  return /^(hello|hi|ping|test|说hello|打印hello|输出hello)$/.test(normalized)
}

function getTaskPlanningGuidance(task, children) {
  if (isSimpleBossTask(task)) {
    return [
      '这是一个非常简单的任务，禁止过度拆解。',
      '优先只生成 1 个子任务。',
      '优先只分配给 1 个直属下属。',
      '如果 1 个子任务就能完成，就不要再创建额外任务。',
      '通常这类任务不应该有依赖关系，除非确实必需。',
    ].join('\n')
  }

  if (children.length <= 1) {
    return '直属下属较少，请保持计划简洁，不要为了形式拆分出多余任务。'
  }

  return '请按完成任务所需的最小必要复杂度拆解，不要为了显得完整而过度拆分。'
}

function approvalAssigneeCount(plan) {
  return new Set((plan?.tasks || []).map((item) => item.assigneeId).filter(Boolean)).size
}

function approvalDependencyCount(plan) {
  return (plan?.tasks || []).reduce(
    (count, item) => count + normalizeDependencyList(item.dependsOn).length,
    0,
  )
}

function validateApprovalPlan(plan, children) {
  if (!plan || typeof plan !== 'object') return '????? JSON ??'
  if (!String(plan.summary || '').trim()) return '?? summary'
  if (!String(plan.deliverable || '').trim()) return '?? deliverable'
  if (!Array.isArray(plan.tasks) || !plan.tasks.length) return 'tasks ????'
  if (!Array.isArray(plan.risks)) return 'risks ?????'
  if (!Array.isArray(plan.openQuestions)) return 'openQuestions ?????'

  const validAssignees = new Map(children.map((child) => [String(child.id), displayName(child)]))
  const taskIds = new Set()

  for (const task of plan.tasks) {
    if (!task || typeof task !== 'object') return 'tasks ??????'
    const id = String(task.id || '').trim()
    const title = String(task.title || '').trim()
    const assigneeId = String(task.assigneeId || '').trim()
    const assigneeName = String(task.assigneeName || '').trim()
    const detail = String(task.task || '').trim()
    if (!id) return '???? id ????'
    if (taskIds.has(id)) return `??? id ??: ${id}`
    taskIds.add(id)
    if (!title) return `??? ${id} ?? title`
    if (!detail) return `??? ${id} ?? task`
    if (!validAssignees.has(assigneeId)) return `??? ${id} ? assigneeId ???????`
    if (assigneeName && assigneeName !== validAssignees.get(assigneeId)) {
      return `??? ${id} ? assigneeName ? assigneeId ???`
    }
  }

  for (const task of plan.tasks) {
    const deps = normalizeDependencyList(task.dependsOn)
    if (deps.includes(task.id)) return `??? ${task.id} ??????`
    for (const dep of deps) {
      if (!taskIds.has(dep)) return `??? ${task.id} ????????? ${dep}`
    }
  }

  const visiting = new Set()
  const visited = new Set()
  const graph = new Map(plan.tasks.map((task) => [task.id, normalizeDependencyList(task.dependsOn)]))

  function hasCycle(taskId) {
    if (visiting.has(taskId)) return true
    if (visited.has(taskId)) return false
    visiting.add(taskId)
    for (const dep of graph.get(taskId) || []) {
      if (hasCycle(dep)) return true
    }
    visiting.delete(taskId)
    visited.add(taskId)
    return false
  }

  for (const task of plan.tasks) {
    if (hasCycle(task.id)) return '????????'
  }

  return ''
}

function renderApprovalPlan(plan) {
  if (!plan) return ''
  const taskSection = plan.tasks
    .map((task, index) => {
      const deps = normalizeDependencyList(task.dependsOn)
      return [
        `${index + 1}. ${task.title}`,
        `负责人：${task.assigneeName || task.assigneeId}`,
        `指令：${task.task}`,
        `依赖：${deps.length ? deps.join('、') : '无'}`,
        `分配理由：${task.reason || '未说明'}`,
      ].join('\n')
    })
    .join('\n\n')

  return [
    '## 目标理解',
    plan.summary,
    '',
    '## 任务拆解与分配',
    taskSection,
    '',
    '## 风险',
    (plan.risks || []).length ? plan.risks.map((item) => `- ${item}`).join('\n') : '- 无',
    '',
    '## 待确认',
    (plan.openQuestions || []).length
      ? plan.openQuestions.map((item) => `- ${item}`).join('\n')
      : '- 无',
    '',
    '## 最终交付形态',
    plan.deliverable,
  ].join('\n')
}

async function createDelegationPlan(placement, task, approvedDraft, children, approvedPlan = null) {
  const context = getPlacementContext(placement)
  if (approvedPlan?.tasks?.length) {
    return approvedPlan.tasks.map((item) => ({
      taskId: String(item.id || ''),
      title: item.title || '',
      assigneeId: String(item.assigneeId),
      assigneeName: item.assigneeName || '',
      task: item.task,
      dependsOn: normalizeDependencyList(item.dependsOn),
      reason: item.reason || '',
    }))
  }

  const childRoster = formatSubordinateRoster(children)
  const rawPlan = await runtime.runWorkerTask({
    workerKey: `${placement.id}:dispatch`,
    workerName: `${context.workerName} / dispatch`,
    systemPrompt: context.plannerPrompt,
    entityId: placement.id,
    userPrompt: `你要根据已经审批通过的经理拆解，把任务分发给直属下属。
总任务：${task}
直属下属清单：
${childRoster}

已审批通过的拆解草案：
${approvedDraft || '无审批草案，请基于总任务和直属下属清单给出最合理分配。'}

请只输出 JSON 数组，每项格式为：
[{"assigneeId":"...","assigneeName":"...","task":"...","dependsOn":[],"reason":"..."}]

要求：
1. assigneeId 必须来自直属下属清单
2. task 必须是可以直接发给该下属执行的完整指令
3. dependsOn 需要反映草案中的依赖关系，没有则输出 []
4. 如果草案里已有 machine_plan，优先忠实复用`,
  })

  const parsed = extractJsonPayload(rawPlan)
  if (!Array.isArray(parsed)) {
    runtime.log('mgr', `[${context.workerName}] \u6d3e\u5de5 JSON \u89e3\u6790\u5931\u8d25\uff0c\u5c06\u4f7f\u7528\u9ed8\u8ba4\u5206\u914d`, {
      entityId: placement.id,
    })
    return children.map((child) => ({
      taskId: `fallback-${child.id}`,
      title: task,
      assigneeId: child.id,
      task: `${task}\n\u8bf7\u4ece ${displayName(child)} \u7684\u89d2\u8272\u89c6\u89d2\u63a8\u8fdb\u4f60\u8d1f\u8d23\u7684\u90e8\u5206\u3002`,
      dependsOn: [],
      reason: '',
    }))
  }

  return children.map((child) => {
    const matched = parsed.find(
      (item) =>
        item?.assigneeId === child.id ||
        item?.assigneeName === displayName(child) ||
        item?.name === displayName(child),
    )
    return {
      taskId: String(matched?.id || ''),
      title: matched?.title || task,
      assigneeId: child.id,
      assigneeName: displayName(child),
      task:
        matched?.task ||
        `${task}\n\u8bf7\u4ece ${displayName(child)} \u7684\u89d2\u8272\u89c6\u89d2\u63a8\u8fdb\u4f60\u8d1f\u8d23\u7684\u90e8\u5206\u3002`,
      dependsOn: normalizeDependencyList(matched?.dependsOn),
      reason: matched?.reason || '',
    }
  })
}

async function executeManagedTask(placement, task, approvedDraft = '', options = {}) {
  const context = getPlacementContext(placement)
  const children = getManagedChildren(placement)

  if (!children.length) {
    runtime.log('mgr', `[${context.workerName}] \u6ca1\u6709\u53ef\u6267\u884c\u7684\u4e0b\u5c5e\uff0c\u8df3\u8fc7\u7edf\u7b79`, {
      entityId: placement.id,
    })
    return ''
  }

  runtime.log('mgr', `[${context.workerName}] \u5f00\u59cb\u7ed9 ${children.length} \u4e2a\u76f4\u5c5e\u4e0b\u5c5e\u6d3e\u5de5`, {
    entityId: placement.id,
  })
  const assignments = await createDelegationPlan(
    placement,
    task,
    approvedDraft,
    children,
    options.approvedPlan || null,
  )
  const childResults = []
  const completedTaskResults = new Map()
  const assignmentPairs = assignments
    .map((assignment) => ({
      assignment,
      child: children.find((item) => item.id === assignment.assigneeId),
    }))
    .filter((item) => item.child)

  for (const { assignment, child } of assignmentPairs) {
    const dependencyTaskIds = normalizeDependencyList(assignment?.dependsOn)
    const dependencySummaries = dependencyTaskIds
      .map((dep) => completedTaskResults.get(dep))
      .filter(Boolean)
    const dependencyNames = dependencySummaries.map((item) => item.assignee)
    const taskInstruction =
      assignment?.task ||
      `${task}\n\u8bf7\u4ece ${displayName(child)} \u7684\u89d2\u8272\u89c6\u89d2\u63a8\u8fdb\u4f60\u8d1f\u8d23\u7684\u90e8\u5206\u3002`
    const enrichedTask = dependencyNames.length
      ? `${taskInstruction}\n\n前置依赖交付：\n${dependencySummaries
          .map(
            (item, index) =>
              `${index + 1}. ${item.assignee} / ${item.title}\n交付内容：${item.result}`,
          )
          .join('\n\n')}\n\n请基于以上前置交付继续当前任务。`
      : taskInstruction

    runtime.log('sch', `[${context.workerName}] -> [${displayName(child)}] ${taskInstruction}`, {
      entityId: placement.id,
    })
    const result = await executeTask(child, enrichedTask, '', {
      queued: false,
      deliverToBoss: false,
    })
    const childResult = {
      taskId: assignment?.taskId || '',
      title: assignment?.title || taskInstruction,
      assignee: displayName(child),
      kind: kindLabelForPlacement(child),
      task: taskInstruction,
      dependsOn: dependencyNames,
      result,
    }
    childResults.push(childResult)
    if (childResult.taskId) completedTaskResults.set(childResult.taskId, childResult)
  }

  runtime.log('mgr', `[${context.workerName}] \u5f00\u59cb\u7edf\u7b79\u4e0b\u5c5e\u4ea4\u4ed8`, {
    entityId: placement.id,
  })
  const finalResult = await runtime.runWorkerTask({
    workerKey: `${placement.id}:synthesis`,
    workerName: `${context.workerName} / synthesis`,
    systemPrompt: context.synthesizerPrompt,
    entityId: placement.id,
    userPrompt: `\u8bf7\u628a\u4e0b\u5c5e\u4ea4\u4ed8\u6574\u7406\u6210\u4e00\u4efd\u9762\u5411 Boss \u7684\u6700\u7ec8\u4ea4\u4ed8\u3002
\u603b\u4efb\u52a1\uff1a${task}
${approvedDraft ? `\u5df2\u901a\u8fc7\u7684\u62c6\u89e3\u8349\u6848\uff1a\n${approvedDraft}\n` : ''}\n\u4e0b\u5c5e\u4ea4\u4ed8\uff1a
${childResults
  .map(
    (item, index) =>
      `${index + 1}. ${item.assignee} (${item.kind})\n\u5b50\u4efb\u52a1\uff1a${item.task}\n\u4f9d\u8d56\uff1a${item.dependsOn.length ? item.dependsOn.join('、') : '无'}\n\u4ea4\u4ed8\uff1a${item.result}`,
  )
  .join('\n\n')}

\u8bf7\u8f93\u51fa\uff1a
1. \u6267\u884c\u6982\u89c8
2. \u5173\u952e\u7ed3\u679c
3. \u98ce\u9669/\u672a\u5b8c\u6210\u9879
4. \u5efa\u8bae Boss \u540e\u7eed\u51b3\u7b56`,
  })

  if (options.deliverToBoss !== false) {
    runtime.addDelivery({ sender: context.workerName, task, result: finalResult })
  }

  return finalResult
}

async function executeTask(placement, task, approvedDraft = '', options = {}) {
  const { queued = false, deliverToBoss = true, sourceTask = null, approvedPlan = null } = options
  const context = getPlacementContext(placement)
  setPlacementStatus(placement, 'working', '\u4efb\u52a1\u6267\u884c\u4e2d')

  let result = ''

  if (context.role === 'manager') {
    result = await executeManagedTask(placement, task, approvedDraft, {
      deliverToBoss,
      approvedPlan,
    })
  } else {
    result = await runtime.runWorkerTask({
      workerKey: placement.id,
      workerName: context.workerName,
      systemPrompt: context.workerPrompt,
      entityId: getEntityInfoSourceId(placement),
      userPrompt: approvedDraft
        ? `\u6309\u5df2\u5ba1\u9605\u901a\u8fc7\u7684\u62c6\u89e3\u5f00\u59cb\u6267\u884c\u3002\n\u4efb\u52a1\uff1a${task}\n\u62c6\u89e3\u8349\u6848\uff1a\n${approvedDraft}`
        : `\u5f53\u524d\u5de5\u4f5c\u9879\u76ee\uff1a${task}`,
    })
    if (deliverToBoss) {
      runtime.addDelivery({ sender: context.workerName, task, result })
    }
  }

  if (queued) {
    if (isExecutionError(result)) {
      restoreTaskCard(sourceTask)
      setPlacementStatus(placement, 'error', '\u6267\u884c\u5f02\u5e38')
      runtime.log('sys', `\u4efb\u52a1\u6267\u884c\u5f02\u5e38\uff0c\u5df2\u9000\u56de\u5230\u4efb\u52a1\u5217\u8868 -> ${task}`, {
        entityId: placement.id,
      })
    }
    runtime.shiftTask(placement.id)
    processingSet.delete(placement.id)
    if ((runtime.teamQueues[placement.id] || []).length) {
      processQueue(placement)
    } else if (!isExecutionError(result)) {
      setPlacementStatus(placement, 'idle', ui.idle)
    }
  } else {
    setPlacementStatus(
      placement,
      isExecutionError(result) ? 'error' : 'idle',
      isExecutionError(result) ? '\u6267\u884c\u5f02\u5e38' : ui.idle,
    )
  }

  return result
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

function logClass(role) {
  return {
    sys: 'text-slate-300',
    mgr: 'text-emerald-400',
    sch: 'text-violet-300',
    wrk: 'text-sky-300',
  }[role || 'sys']
}

function prefixForRole(role) {
  return {
    sys: '[SYS]',
    mgr: '[MGR]',
    sch: '[SCH]',
    wrk: '[WRK]',
  }[role || 'sys']
}

function formatLogTime(value) {
  if (!value) return ''
  return new Date(value).toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function fitViewportToContent() {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  const fitScale = Math.min(rect.width / canvasWidth.value, rect.height / canvasHeight.value, 1)
  const nextScale = Math.max(0.42, fitScale)
  view.value = {
    scale: nextScale,
    x: (rect.width - canvasWidth.value * nextScale) / 2,
    y: (rect.height - canvasHeight.value * nextScale) / 2,
  }
  clampViewport()
}

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', movePan)
})

onMounted(() => {
  nextTick(() => fitViewportToContent())
})

watch(
  currentPlacements,
  async () => {
    await nextTick()
    fitViewportToContent()
  },
  { deep: true },
)
</script>
