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
          @click="openApproval(approval)"
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
        <div
          v-for="delivery in runtime.deliveries"
          :key="delivery.id"
          role="button"
          tabindex="0"
          class="mb-3 w-full cursor-pointer rounded-xl border border-slate-200 border-l-4 bg-white p-3 text-left shadow-sm transition hover:border-slate-300 hover:shadow-md"
          :class="isPptDelivery(delivery) ? 'border-l-indigo-500' : 'border-l-emerald-500'"
          @click="openDelivery(delivery)"
          @keydown.enter.prevent="openDelivery(delivery)"
          @keydown.space.prevent="openDelivery(delivery)"
        >
          <div class="flex items-start gap-3">
            <div
              class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
              :class="isPptDelivery(delivery) ? 'bg-indigo-50 text-indigo-600' : 'bg-emerald-50 text-emerald-600'"
            >
              <Presentation v-if="isPptDelivery(delivery)" class="h-4 w-4" />
              <FileText v-else class="h-4 w-4" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="truncate text-sm font-semibold text-slate-800">{{ getDeliveryTitle(delivery) }}</div>
              <div class="mt-1 flex items-center gap-2 text-xs text-slate-500">
                <span>{{ ui.processor }}{{ delivery.sender }}</span>
                <span
                  class="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                  :class="isPptDelivery(delivery) ? 'bg-indigo-50 text-indigo-600' : 'bg-emerald-50 text-emerald-600'"
                >
                  {{ isPptDelivery(delivery) ? 'PPT' : 'MD' }}
                </span>
              </div>
            </div>
            <button
              type="button"
              class="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-600 disabled:cursor-wait disabled:opacity-60"
              :disabled="isDownloadingDelivery(delivery)"
              :title="isDownloadingDelivery(delivery) ? '正在准备下载' : '下载交付物'"
              @click.stop="downloadDelivery(delivery)"
            >
              <Loader2 v-if="isDownloadingDelivery(delivery)" class="h-4 w-4 animate-spin" />
              <FileDown v-else class="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
      </template>
    </aside>

    <section class="panel flex min-w-0 flex-1 flex-col overflow-visible">
      <div class="flex items-center justify-between border-b border-slate-200 bg-slate-100 px-4 py-2">
        <div class="text-sm font-semibold text-slate-700">
          {{ getFloorLabel(currentFloorId) }}
        </div>
        <div class="text-xs text-slate-500">
          {{ ui.zoom }} {{ Math.round(view.scale * 100) }}%
        </div>
      </div>
      <div class="min-h-0 flex-1 overflow-visible bg-[#f8fafc] p-4">
        <div class="flex h-full min-h-0 gap-3 overflow-visible">
          <aside ref="floorRailRef" class="relative z-30 flex w-[64px] shrink-0 flex-col justify-end">
            <div class="rounded-3xl border border-slate-200 bg-white/90 px-2 py-3 shadow-sm backdrop-blur">
              <div class="flex flex-col justify-end gap-2">
                <button
                  v-for="floor in floorButtons"
                  :key="floor.id"
                  :ref="(el) => setFloorButtonRef(floor.id, el)"
                  class="group relative z-10 flex h-11 items-center justify-center rounded-2xl border text-sm font-semibold shadow-sm transition"
                  :class="
                    currentFloorId === floor.id
                      ? 'border-brand-300 bg-brand-50 text-brand-700'
                      : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300 hover:bg-slate-50'
                  "
                  @click="selectFloor(floor.id, $event.currentTarget)"
                >
                  <span>{{ getFloorNumber(floor.id) }}</span>
                  <div
                    class="pointer-events-none absolute left-full top-1/2 z-40 ml-3 hidden -translate-y-1/2 whitespace-nowrap rounded-2xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 shadow-lg group-hover:block"
                    :class="currentFloorId === floor.id ? 'block' : ''"
                  >
                    {{ getFloorLabel(floor.id) }}
                  </div>
                </button>
              </div>
            </div>
          </aside>

          <div ref="canvasShellRef" class="relative min-w-0 flex-1 overflow-visible">
            <div
              v-if="floorCalloutStyle"
              class="pointer-events-none absolute left-0 z-30 h-8 w-6 -translate-x-[22px] -translate-y-1/2"
              :style="floorCalloutStyle"
              aria-hidden="true"
            >
              <div
                class="absolute inset-0"
                style="clip-path: polygon(0 50%, 100% 0, 100% 100%); background: rgb(226 232 240);"
              ></div>
              <div
                class="absolute inset-y-[1px] right-0 left-[2px]"
                style="clip-path: polygon(0 50%, 100% 0, 100% 100%); background: white;"
              ></div>
            </div>
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
                <svg
                  v-if="taskFlowOverlay.lines.length"
                  class="pointer-events-none absolute inset-0 z-10"
                  aria-hidden="true"
                >
                  <defs>
                    <marker
                      id="task-flow-arrow"
                      markerWidth="10"
                      markerHeight="10"
                      refX="8"
                      refY="5"
                      orient="auto"
                      markerUnits="strokeWidth"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
                    </marker>
                  </defs>
                  <g v-for="line in taskFlowOverlay.lines" :key="line.id" :class="line.colorClass">
                    <path
                      :d="line.path"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-opacity="0.82"
                      marker-end="url(#task-flow-arrow)"
                    />
                  </g>
                </svg>
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
          <div class="flex items-center justify-between gap-3">
            <div class="font-semibold text-slate-800">{{ task.title }}</div>
            <span
              class="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.16em]"
              :class="
                task.kind === 'word'
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'bg-amber-50 text-amber-700'
              "
            >
              {{ task.kind === 'word' ? 'WORD' : 'TEXT' }}
            </span>
          </div>
          <div v-if="task.kind === 'word'" class="mt-1 text-[11px] text-slate-500">
            {{ task.fileName }}
          </div>
          <div class="mt-1 text-[11px] text-slate-500">{{ ui.taskDragHint }}</div>
        </div>
      </div>
      <div class="border-t border-slate-200 bg-slate-50 p-4">
        <input
          ref="wordUploadRef"
          type="file"
          accept=".docx"
          class="hidden"
          @change="handleWordUpload"
        />
        <div class="mb-3 grid grid-cols-2 gap-2">
          <button
            class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700"
            @click="longTaskModalOpen = true"
          >
            {{ ui.longTask }}
          </button>
          <button
            class="rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm font-semibold text-indigo-700"
            @click="openWordUpload"
          >
            {{ ui.uploadWord }}
          </button>
        </div>
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

    <Dialog v-model:open="longTaskModalOpen">
      <DialogContent class="max-w-3xl p-0" hide-close>
      <div class="w-full rounded-2xl bg-white shadow-2xl">
        <div class="hidden">
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
      </DialogContent>
    </Dialog>

    <Dialog :open="Boolean(selectedApproval)" @update:open="(open) => !open && closeApprovalModal()">
      <DialogContent v-if="selectedApproval" class="flex h-[80vh] max-w-4xl flex-col p-0">
        <DialogHeader class="border-b border-slate-200 px-5 py-4 text-left">
          <DialogTitle>{{ selectedApproval.task }}</DialogTitle>
          <DialogDescription>
            {{ ui.approver }}{{ selectedApproval.managerName }}
          </DialogDescription>
        </DialogHeader>
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
              <template v-if="approvalEditMode">
                <div class="space-y-4">
                  <div class="grid gap-4 xl:grid-cols-2">
                    <div class="rounded-xl bg-slate-50 p-4">
                      <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">目标理解</div>
                      <textarea
                        v-model="selectedApproval.plan.summary"
                        rows="5"
                        class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm leading-6 text-slate-700 outline-none focus:border-brand-500"
                      />
                    </div>
                    <div class="rounded-xl bg-slate-50 p-4">
                      <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">最终交付</div>
                      <textarea
                        v-model="selectedApproval.plan.deliverable"
                        rows="5"
                        class="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm leading-6 text-slate-700 outline-none focus:border-brand-500"
                      />
                    </div>
                  </div>

                  <div class="flex items-center justify-between rounded-xl border border-dashed border-brand-300 bg-brand-50 px-4 py-3">
                    <div class="text-sm text-brand-700">在右侧详细编辑每个子任务，支持折叠查看。</div>
                    <button
                      class="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-brand-600 transition hover:bg-brand-100"
                      @click="addApprovalTask(selectedApproval)"
                    >
                      + 新增子任务
                    </button>
                  </div>

                  <div class="flex min-h-[48vh] flex-col rounded-xl border border-slate-200 bg-white">
                    <div class="border-b border-slate-200 px-4 py-3 text-xs font-semibold tracking-[0.18em] text-slate-400">
                      具体计划
                    </div>
                    <div class="scrollbar-thin min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
                      <div
                        v-for="(item, index) in selectedApproval.plan.tasks"
                        :key="item.id || index"
                        class="rounded-2xl border border-slate-200 bg-slate-50"
                      >
                        <div class="flex items-center gap-3 px-4 py-3">
                          <button
                            class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-slate-500"
                            @click="toggleApprovalTaskCollapse(selectedApproval, item, index)"
                          >
                            {{ isApprovalTaskCollapsed(selectedApproval, item, index) ? '展开' : '收起' }}
                          </button>
                          <div class="min-w-0 flex-1">
                            <div class="truncate text-sm font-semibold text-slate-900">
                              {{ index + 1 }}. {{ item.title || '未命名子任务' }}
                            </div>
                            <div class="mt-1 flex flex-wrap gap-2">
                              <span class="rounded-full bg-white px-2.5 py-1 text-[11px] text-slate-600">
                                {{ item.assigneeName || item.assigneeId || '未分配' }}
                              </span>
                              <span class="rounded-full bg-white px-2.5 py-1 text-[11px] text-slate-600">
                                {{ normalizeDependencyList(item.dependsOn).length ? `依赖 ${normalizeDependencyList(item.dependsOn).length} 项` : '无依赖' }}
                              </span>
                            </div>
                          </div>
                          <button
                            class="rounded-lg border border-rose-200 px-3 py-1.5 text-xs font-semibold text-rose-500 transition hover:bg-rose-50"
                            @click="removeApprovalTask(selectedApproval, index)"
                          >
                            删除
                          </button>
                        </div>

                        <div v-if="!isApprovalTaskCollapsed(selectedApproval, item, index)" class="border-t border-slate-200 bg-white px-4 py-4">
                          <label class="text-xs font-semibold tracking-[0.18em] text-slate-400">任务标题</label>
                          <input
                            v-model="item.title"
                            class="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-900 outline-none focus:border-brand-500"
                          />

                          <div class="mt-4 grid gap-4 lg:grid-cols-[260px_minmax(0,1fr)]">
                            <div class="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                              <div>
                                <label class="text-xs font-semibold tracking-[0.18em] text-slate-400">分配给谁</label>
                                <select
                                  v-model="item.assigneeId"
                                  class="mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-brand-500"
                                  @change="syncApprovalAssignee(selectedApproval, item)"
                                >
                                  <option
                                    v-for="child in getApprovalAssignableChildren(selectedApproval)"
                                    :key="child.id"
                                    :value="child.id"
                                  >
                                    {{ displayName(child) }} · {{ kindLabelForPlacement(child) }}
                                  </option>
                                </select>
                              </div>
                              <div class="rounded-xl border border-slate-200 bg-white p-3">
                                <div class="text-[11px] font-semibold tracking-[0.18em] text-slate-400">任务时序</div>
                                <div class="mt-2 flex flex-wrap gap-2">
                                  <span
                                    v-if="!normalizeDependencyList(item.dependsOn).length"
                                    class="rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700"
                                  >
                                    可直接开始
                                  </span>
                                  <span
                                    v-for="depLabel in getApprovalDependencyLabels(selectedApproval.plan, item)"
                                    :key="depLabel"
                                    class="rounded-full bg-amber-100 px-3 py-1 text-xs text-amber-700"
                                  >
                                    依赖 {{ depLabel }}
                                  </span>
                                </div>
                                <div class="mt-3 border-t border-slate-200 pt-3">
                                  <div class="text-[11px] font-semibold tracking-[0.18em] text-slate-400">编辑依赖</div>
                                  <div class="mt-2 flex flex-wrap gap-2">
                                    <label
                                      v-for="candidate in getApprovalDependencyCandidates(selectedApproval.plan, item)"
                                      :key="candidate.id"
                                      class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-600"
                                    >
                                      <input
                                        type="checkbox"
                                        :checked="normalizeDependencyList(item.dependsOn).includes(candidate.id)"
                                        @change="toggleApprovalDependency(item, candidate.id)"
                                      />
                                      <span>{{ candidate.id }} · {{ candidate.title }}</span>
                                    </label>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <div class="rounded-2xl border border-slate-200 bg-white p-4">
                              <label class="text-xs font-semibold tracking-[0.18em] text-slate-400">具体内容</label>
                              <textarea
                                v-model="item.task"
                                rows="12"
                                class="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm leading-6 text-slate-700 outline-none focus:border-brand-500"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="grid gap-4 md:grid-cols-2">
                  <div class="rounded-xl bg-slate-50 p-4">
                    <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">目标理解</div>
                    <div class="mt-2 text-sm leading-6 text-slate-700">
                      {{ selectedApproval.plan.summary }}
                    </div>
                  </div>
                  <div class="rounded-xl bg-slate-50 p-4">
                    <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">最终交付</div>
                    <div class="mt-2 text-sm leading-6 text-slate-700">
                      {{ selectedApproval.plan.deliverable }}
                    </div>
                  </div>
                </div>
                <div class="rounded-xl border border-slate-200 bg-white">
                  <div class="border-b border-slate-200 px-4 py-3 text-xs font-semibold tracking-[0.18em] text-slate-400">
                    任务时序与分配
                  </div>
                  <div class="divide-y divide-slate-100">
                    <div
                      v-for="(item, index) in selectedApproval.plan.tasks"
                      :key="item.id || index"
                      class="px-4 py-4"
                    >
                      <div class="flex flex-wrap items-center gap-2 text-sm font-semibold text-slate-900">
                        <span>{{ index + 1 }}. {{ item.title }}</span>
                        <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600">
                          {{ item.assigneeName || item.assigneeId }}
                        </span>
                      </div>
                      <div class="mt-3 flex flex-wrap gap-2">
                        <span
                          v-if="!normalizeDependencyList(item.dependsOn).length"
                          class="rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700"
                        >
                          可直接开始
                        </span>
                        <span
                          v-for="depLabel in getApprovalDependencyLabels(selectedApproval.plan, item)"
                          :key="depLabel"
                          class="rounded-full bg-amber-100 px-3 py-1 text-xs text-amber-700"
                        >
                          依赖 {{ depLabel }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
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
        </div>
        <div class="flex items-center justify-end gap-3 border-t border-slate-200 bg-white px-5 py-4">
          <button
            v-if="selectedApproval.plan"
            class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600"
            @click="approvalEditMode = !approvalEditMode"
          >
            {{ approvalEditMode ? '完成编辑' : '编辑计划' }}
          </button>
          <button
            v-if="!approvalEditMode"
            class="rounded-xl border border-rose-200 px-4 py-2 text-sm font-semibold text-rose-500"
            @click="openRejectModal(selectedApproval)"
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
      </DialogContent>
    </Dialog>

    <Dialog :open="rejectModalOpen && selectedApproval" @update:open="(open) => !open && closeRejectModal()">
      <DialogContent v-if="selectedApproval" class="max-w-xl p-0" hide-close>
      <div class="w-full rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div class="text-lg font-semibold text-slate-900">填写驳回意见</div>
          <button class="text-xl text-slate-400" @click="closeRejectModal">x</button>
        </div>
        <div class="p-5">
          <div class="mb-2 text-sm font-semibold text-slate-700">{{ ui.feedbackLabel }}</div>
          <textarea
            v-model="rejectFeedback"
            rows="6"
            class="w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm outline-none focus:border-brand-500"
            :placeholder="ui.feedbackPlaceholder"
          />
        </div>
        <div class="flex items-center justify-end gap-3 border-t border-slate-200 px-5 py-4">
          <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm" @click="closeRejectModal">
            取消
          </button>
          <button
            class="rounded-xl bg-rose-500 px-4 py-2 text-sm font-semibold text-white"
            @click="submitReject(selectedApproval)"
          >
            确认驳回
          </button>
        </div>
      </div>
      </DialogContent>
    </Dialog>

    <Dialog :open="Boolean(selectedDelivery)" @update:open="(open) => !open && (selectedDelivery = null)">
      <DialogContent v-if="selectedDelivery" class="flex h-[80vh] max-w-5xl flex-col p-0">
        <div class="flex h-full w-full flex-col overflow-hidden">
        <DialogHeader class="border-b border-slate-200 px-5 py-4 text-left">
          <DialogTitle>{{ selectedDelivery.task }}</DialogTitle>
          <DialogDescription>处理方：{{ selectedDelivery.sender }}</DialogDescription>
        </DialogHeader>
        <div class="hidden">
          <div>
            <div class="text-lg font-semibold text-slate-900">{{ selectedDelivery.task }}</div>
            <div class="mt-1 text-xs text-slate-500">处理方：{{ selectedDelivery.sender }}</div>
          </div>
          <button class="text-xl text-slate-400" @click="selectedDelivery = null">x</button>
        </div>
        <div class="scrollbar-thin flex-1 overflow-y-auto bg-slate-50 p-5">
          <div class="rounded-2xl border border-slate-200 bg-white p-5">
            <div class="mb-4 flex items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div class="flex items-center gap-3">
                <div
                  class="flex h-9 w-9 items-center justify-center rounded-xl"
                  :class="isPptDelivery(selectedDelivery) ? 'bg-indigo-50 text-indigo-600' : 'bg-emerald-50 text-emerald-600'"
                >
                  <Presentation v-if="isPptDelivery(selectedDelivery)" class="h-5 w-5" />
                  <FileText v-else class="h-5 w-5" />
                </div>
                <div>
                  <div class="text-sm font-semibold text-slate-700">交付预览</div>
                  <div class="mt-0.5 text-xs text-slate-400">
                    {{ isPptDelivery(selectedDelivery) ? 'PPT Deliverable' : 'Markdown Render' }}
                  </div>
                </div>
              </div>
              <button
                type="button"
                class="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-600 disabled:cursor-wait disabled:opacity-60"
                :disabled="isDownloadingDelivery(selectedDelivery)"
                @click="downloadDelivery(selectedDelivery)"
              >
                <Loader2 v-if="isDownloadingDelivery(selectedDelivery)" class="h-4 w-4 animate-spin" />
                <FileDown v-else class="h-4 w-4" />
                {{ getDownloadButtonText(selectedDelivery) }}
              </button>
            </div>
            <div
              v-if="isPptDelivery(selectedDelivery)"
              class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
            >
              <div class="text-sm font-semibold text-slate-900">
                {{ selectedDelivery.deliverable.fileName || 'result.pptx' }}
              </div>
              <div class="mt-2 text-sm text-slate-600">
                {{ selectedDelivery.deliverable.summary || '已生成可下载的 PPT 文件。' }}
              </div>
              <div v-if="isDownloadingDelivery(selectedDelivery)" class="mt-4 rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-700">
                正在准备 PPT 下载，请稍候...
              </div>
            </div>
            <div
              v-else
              class="space-y-4"
            >
              <div v-if="isDownloadingDelivery(selectedDelivery)" class="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                正在准备 Markdown 下载，请稍候...
              </div>
              <div
                class="prose prose-sm max-w-none prose-headings:mb-3 prose-headings:text-slate-900 prose-p:text-slate-700 prose-li:text-slate-700 prose-pre:hidden"
                v-html="renderMarkdown(selectedDelivery.result)"
              />
            </div>
          </div>
        </div>
      </div>
      </DialogContent>
    </Dialog>

    <Dialog :open="Boolean(selectedEntity)" @update:open="(open) => !open && (selectedEntity = null)">
      <DialogContent class="flex h-[82vh] max-w-6xl flex-col p-0">
        <DialogHeader class="border-b border-slate-200 px-5 py-4 text-left">
          <DialogTitle>{{ selectedEntity ? displayName(selectedEntity) : '' }}</DialogTitle>
          <DialogDescription>
            {{ selectedEntity?.kind === 'team' ? '团队详情与运行态信息' : '员工详情与运行态信息' }}
          </DialogDescription>
        </DialogHeader>
        <div class="grid min-h-0 flex-1 lg:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
          <div class="scrollbar-thin overflow-y-auto border-r border-slate-200 bg-slate-50 px-5 py-5">
            <div class="grid gap-3">
              <div class="grid grid-cols-[120px_1fr] border-b border-slate-200 pb-3 text-sm">
                <div class="font-semibold text-slate-500">{{ ui.statusLabel }}</div>
              <div>{{ selectedEntityStatusText }}</div>
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
            </div>
          </div>
          <div class="flex min-h-0 flex-col bg-slate-950">
            <div class="border-b border-slate-800 px-5 py-4">
              <div class="text-sm font-semibold text-amber-400">{{ ui.stream }}</div>
              <div class="mt-1 text-xs text-slate-400">实时输出会持续刷新到这一区域</div>
            </div>
            <div class="scrollbar-thin min-h-0 flex-1 overflow-auto px-5 py-5">
              <pre
                class="min-h-full whitespace-pre-wrap rounded-2xl bg-slate-900 p-4 font-mono text-xs leading-6 text-slate-200"
              >{{ selectedEntityStreamText }}</pre>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { FileDown, FileText, Loader2, Presentation } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import PlacementNode from '../components/canvas/PlacementNode.vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog'
import { DEFAULT_SYSTEM_PROMPTS } from '../config/prompts'
import { runPlanScheduler } from '../runtime/scheduler'
import { getApiBaseUrl } from '../services/api'
import { executeRuntimeTask } from '../services/backendRuntime'
import { useAssetLibraryStore } from '../stores/assetLibrary'
import { useAuthStore } from '../stores/auth'
import { useMessageStore } from '../stores/messages'
import { getPlacementBounds } from '../utils/placementBounds'
import { createId } from '../utils/id'
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
  uploadWord: '上传 Word',
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
const sessionExpiredMessage = '登录已失效，请重新登录。'
const apiBaseUrl = getApiBaseUrl()

const store = useSimuBossStore()
const authStore = useAuthStore()
const runtime = useRuntimeStore()
const assetLibrary = useAssetLibraryStore()
const router = useRouter()
const messages = useMessageStore()
const currentFloorId = ref(store.floors[0]?.id || 'floor-1')
const floorRailRef = ref(null)
const canvasShellRef = ref(null)
const floorButtonRefs = {}
const floorCalloutTop = ref(null)
const viewportRef = ref(null)
const panState = ref(null)
const view = ref({ x: 32, y: 24, scale: 1 })
const viewportSize = ref({ width: 720, height: 520 })
const leftSidebarCollapsed = ref(false)
const rightSidebarCollapsed = ref(false)
const logsCollapsed = ref(true)
const dragTask = ref('')
const newTaskInput = ref('')
const longTaskModalOpen = ref(false)
const longTaskInput = ref('')
const wordUploadRef = ref(null)
const selectedApproval = ref(null)
const selectedDelivery = ref(null)
const selectedEntity = ref(null)
const approvalEditMode = ref(false)
const approvalTaskCollapse = ref({})
const rejectModalOpen = ref(false)
const rejectFeedback = ref('')
const downloadingDeliveryIds = ref({})
const processingSet = new Set()

const taskCards = ref([
  { id: createId(), title: '\u65b0\u80fd\u6e90\u7ade\u54c1\u6df1\u5ea6\u5206\u6790\u62a5\u544a' },
])

const currentPlacements = computed(() => store.floorAssignments[currentFloorId.value] || [])
const floorButtons = computed(() => [...store.floors].reverse())
const floorCalloutStyle = computed(() =>
  floorCalloutTop.value == null ? null : { top: `${floorCalloutTop.value}px` },
)
const selectedEntitySourceId = computed(() => getEntityInfoSourceId(selectedEntity.value))
const selectedEntityStatusText = computed(() => {
  if (!selectedEntity.value) return ui.idle
  return getEntityStatusText(selectedEntity.value)
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
const activeTaskFlowOwnerId = computed(() => {
  if (selectedEntitySourceId.value && runtime.taskFlows[selectedEntitySourceId.value]) {
    return selectedEntitySourceId.value
  }
  return currentPlacements.value.map((placement) => placement.id).find((id) => runtime.taskFlows[id]) || null
})
const activeTaskFlow = computed(() =>
  activeTaskFlowOwnerId.value ? runtime.taskFlows[activeTaskFlowOwnerId.value] || null : null,
)
const taskFlowOverlay = ref({ lines: [] })
const selectedEntityStreamText = computed(() => {
  if (!selectedEntity.value) return '\u65e0\u5b9e\u65f6\u8f93\u51fa'
  return getStreamText(selectedEntity.value)
})
const selectedEntityTimeline = computed(() => {
  if (!selectedEntity.value) return []
  return getEntityTimeline(selectedEntity.value)
})
const contentBounds = computed(() => {
  if (!currentPlacements.value.length) {
    return getPlacementBounds([], {
      minWidth: viewportSize.value.width,
      minHeight: viewportSize.value.height,
    })
  }

  return getPlacementBounds(currentPlacements.value, {
    minWidth: viewportSize.value.width,
    minHeight: viewportSize.value.height,
    padding: 72,
  })
})
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

function getFloorLabel(floorId) {
  const index = store.floors.findIndex((item) => item.id === floorId)
  const floor = store.floors[index]
  if (!floor) return ''
  return `${index + 1}层 - ${String(floor.name || '').trim()}`
}

function getFloorNumber(floorId) {
  const index = store.floors.findIndex((item) => item.id === floorId)
  return index === -1 ? '?' : String(index + 1)
}

function setFloorButtonRef(floorId, el) {
  if (el) floorButtonRefs[floorId] = el
  else delete floorButtonRefs[floorId]
}

function setFloorCalloutPositionFromButton(buttonEl) {
  const shellEl = canvasShellRef.value
  if (!buttonEl || !shellEl) {
    floorCalloutTop.value = null
    return
  }

  const buttonRect = buttonEl.getBoundingClientRect()
  const shellRect = shellEl.getBoundingClientRect()
  floorCalloutTop.value = buttonRect.top - shellRect.top + buttonRect.height / 2
}

function updateFloorCalloutPosition() {
  setFloorCalloutPositionFromButton(floorButtonRefs[currentFloorId.value])
}

function scheduleFloorCalloutPositionUpdate() {
  nextTick(() => {
    requestAnimationFrame(() => {
      updateFloorCalloutPosition()
    })
  })
}

function selectFloor(floorId, buttonEl = null) {
  currentFloorId.value = floorId
  if (buttonEl) setFloorCalloutPositionFromButton(buttonEl)
  scheduleFloorCalloutPositionUpdate()
}

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value))
}

function nextLocalId(prefix) {
  return createId(prefix)
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
  if (placement.refId) runtime.setTeamStatus(placement.refId, state, text)
  const leadId = getTeamLeadPlacementId(placement)
  if (leadId) runtime.setTeamStatus(leadId, state, text)
}

function setWorkerBusyState(placement, isWorking, currentTask = '', streamedContent = null) {
  const keys = [...new Set([placement.id, placement.refId].filter(Boolean))]
  keys.forEach((key) => {
    runtime.patchWorkerState(key, {
      isWorking,
      ...(currentTask ? { currentTask } : {}),
      ...(streamedContent !== null ? { streamedContent } : {}),
    })
  })
}

function findManagedPlacementById(placement, targetId) {
  const queue = [...getManagedChildren(placement)]
  while (queue.length) {
    const current = queue.shift()
    if (!current) continue
    if (String(current.id) === String(targetId) || String(current.refId) === String(targetId)) return current
    if (current.children?.length) queue.push(...current.children)
  }
  return null
}

function displayName(placement) {
  if (placement.kind === 'team') return store.teamMap[placement.refId]?.name || placement.name
  return store.employeeMap[placement.refId]?.name || placement.name
}

function escapeSelectorValue(value) {
  return String(value ?? '').replace(/\\/g, '\\\\').replace(/"/g, '\\"')
}

function queryFlowAnchor(entityId) {
  if (!viewportRef.value || !entityId) return null
  const selectors = [
    `[data-entity-id="${escapeSelectorValue(entityId)}"]`,
    `[data-info-source-id="${escapeSelectorValue(entityId)}"]`,
    `[data-ref-id="${escapeSelectorValue(entityId)}"]`,
  ]
  for (const selector of selectors) {
    const node = viewportRef.value.querySelector(selector)
    if (node) return node
  }
  return null
}

function getAnchorCenter(entityId) {
  const viewportRect = viewportRef.value?.getBoundingClientRect()
  const nodeRect = queryFlowAnchor(entityId)?.getBoundingClientRect()
  if (!viewportRect || !nodeRect) return null
  return {
    x: nodeRect.left - viewportRect.left + nodeRect.width / 2,
    y: nodeRect.top - viewportRect.top + nodeRect.height / 2,
  }
}

function buildFlowPath(from, to) {
  const midX = (from.x + to.x) / 2
  return `M ${from.x} ${from.y} C ${midX} ${from.y}, ${midX} ${to.y}, ${to.x} ${to.y}`
}

function lineColorClassForStatus(status) {
  return (
    {
      done: 'text-emerald-500',
      running: 'text-blue-500',
      failed: 'text-rose-500',
      ready: 'text-sky-300',
      pending: 'text-slate-300',
    }[status] || 'text-slate-300'
  )
}

function rebuildTaskFlowOverlay() {
  const flow = activeTaskFlow.value
  if (!flow || !viewportRef.value) {
    taskFlowOverlay.value = { lines: [] }
    return
  }

  const nextLines = []
  flow.taskOrder.forEach((taskId) => {
    const task = flow.tasks?.[taskId]
    if (!task?.assigneeId) return
    const target = getAnchorCenter(task.assigneeId)
    if (!target) return

    const sources = task.dependsOn?.length
      ? task.dependsOn.map((depId) => flow.tasks?.[depId]?.assigneeId).filter(Boolean)
      : flow.rootId && flow.rootId !== task.assigneeId
        ? [flow.rootId]
        : []

    sources.forEach((sourceId, index) => {
      const source = getAnchorCenter(sourceId)
      if (!source) return
      nextLines.push({
        id: `${task.id}-${sourceId}-${index}`,
        path: buildFlowPath(source, target),
        colorClass: lineColorClassForStatus(task.status),
      })
    })
  })

  taskFlowOverlay.value = { lines: nextLines }
}

function scheduleTaskFlowOverlayUpdate() {
  nextTick(() => {
    requestAnimationFrame(() => {
      rebuildTaskFlowOverlay()
    })
  })
}

function extractTaskIdFromTimelineMessage(message) {
  return String(message || '').match(/\b(t\d+)\b/)?.[1] || null
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
      activationType: employee?.activationType || 'text',
      deliverableType: employee?.deliverableType || 'text',
      executionMode: employee?.executionMode || 'llm',
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
    activationType: manager?.activationType || 'text',
    deliverableType: manager?.deliverableType || 'text',
    fixedPlan: manager?.fixedPlan || null,
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
  return { id: createId(), kind: 'text', title, text: title }
}

function createWordTaskCard(file, base64) {
  return {
    id: createId(),
    kind: 'word',
    title: file.name,
    fileName: file.name,
    mimeType:
      file.type || 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    base64,
  }
}

function openWordUpload() {
  wordUploadRef.value?.click?.()
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const value = String(reader.result || '')
      resolve(value.includes(',') ? value.split(',').pop() : value)
    }
    reader.onerror = () => reject(reader.error || new Error('文件读取失败'))
    reader.readAsDataURL(file)
  })
}

async function handleWordUpload(event) {
  const file = event.target?.files?.[0]
  if (!file) return
  try {
    const base64 = await fileToBase64(file)
    taskCards.value.unshift(createWordTaskCard(file, base64))
  } catch (error) {
    messages.error('Word 文件读取失败', error instanceof Error ? error.message : '请重新选择文件。')
  } finally {
    event.target.value = ''
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

function recordDelivery({
  sender,
  task,
  result,
  sourceTaskId = '',
  sourcePlanId = '',
  deliverable = null,
}) {
  runtime.addDelivery({ sender, task, result, deliverable })
  assetLibrary.registerDeliverable({
    title: task,
    result,
    sender,
    sourceTaskId,
    sourcePlanId,
    deliverable,
  })
}

function getDeliveryTitle(delivery) {
  if (delivery?.deliverable?.type === 'ppt') {
    return `${delivery.task} - ${delivery.deliverable.fileName || 'result.pptx'}`
  }
  return `${delivery.task} - result.md`
}

function isPptDelivery(delivery) {
  return delivery?.deliverable?.type === 'ppt'
}

function getDeliveryDownloadId(delivery) {
  return delivery?.id || `${delivery?.task || 'delivery'}:${delivery?.createdAt || ''}`
}

function isDownloadingDelivery(delivery) {
  return Boolean(downloadingDeliveryIds.value[getDeliveryDownloadId(delivery)])
}

function setDownloadingDelivery(delivery, value) {
  const id = getDeliveryDownloadId(delivery)
  if (!id) return
  downloadingDeliveryIds.value = {
    ...downloadingDeliveryIds.value,
    [id]: value,
  }
  if (!value) {
    const next = { ...downloadingDeliveryIds.value }
    delete next[id]
    downloadingDeliveryIds.value = next
  }
}

function getDownloadButtonText(delivery) {
  if (isDownloadingDelivery(delivery)) return '准备中...'
  return isPptDelivery(delivery) ? '下载 PPT' : '下载 MD'
}

function openDelivery(delivery) {
  selectedDelivery.value = delivery
}

function downloadDelivery(delivery) {
  if (isPptDelivery(delivery)) {
    return downloadDeliveryFile(delivery)
  }
  return downloadMarkdownDelivery(delivery)
}

function triggerBrowserDownload(blob, filename) {
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(objectUrl)
}

function retireMessage(id, delay) {
  window.setTimeout(() => messages.remove(id), delay)
}

async function downloadMarkdownDelivery(delivery) {
  if (isDownloadingDelivery(delivery)) return
  setDownloadingDelivery(delivery, true)
  const messageId = messages.push({
    type: 'loading',
    title: '正在准备 Markdown 下载',
    message: '文件准备完成后会自动保存到浏览器下载目录。',
    persistent: true,
  })
  try {
    const blob = new Blob([String(delivery?.result || '')], {
      type: 'text/markdown;charset=utf-8',
    })
    const filename = `${getDeliveryTitle(delivery).replace(/[\\/:*?"<>|]+/g, '-')}`
    triggerBrowserDownload(blob, filename)
    messages.update(messageId, {
      type: 'success',
      title: 'Markdown 下载已开始',
      message: filename,
      persistent: false,
    })
    retireMessage(messageId, 3200)
  } catch (error) {
    messages.update(messageId, {
      type: 'error',
      title: 'Markdown 下载失败',
      message: error instanceof Error ? error.message : '请稍后重试。',
      persistent: false,
    })
    retireMessage(messageId, 5200)
  } finally {
    setDownloadingDelivery(delivery, false)
  }
}

async function downloadDeliveryFile(delivery) {
  if (isDownloadingDelivery(delivery)) return
  const downloadUrl = delivery?.deliverable?.downloadUrl
  if (!downloadUrl || !authStore.authToken) {
    messages.error('无法下载交付物', '当前交付物缺少可下载文件。')
    return
  }

  setDownloadingDelivery(delivery, true)
  const messageId = messages.push({
    type: 'loading',
    title: '正在准备 PPT 下载',
    message: 'PPT 文件较大时可能需要等待几十秒，你可以继续查看页面，完成后会自动保存。',
    persistent: true,
  })
  try {
    const response = await fetch(`${apiBaseUrl}${downloadUrl}`, {
      headers: {
        Authorization: `Bearer ${authStore.authToken}`,
      },
    })

    if (response.status === 401) {
      await authStore.logout()
      messages.update(messageId, {
        type: 'error',
        title: '登录已失效',
        message: sessionExpiredMessage,
        persistent: false,
      })
      retireMessage(messageId, 5200)
      await router.push({
        path: '/login',
        query: { redirect: router.currentRoute.value.fullPath, reason: 'expired' },
      })
      return
    }

    if (!response.ok) {
      const text = await response.text().catch(() => '')
      messages.update(messageId, {
        type: 'error',
        title: 'PPT 下载失败',
        message: text || '请稍后重试。',
        persistent: false,
      })
      retireMessage(messageId, 5200)
      return
    }

    const blob = await response.blob()
    const filename = delivery.deliverable.fileName || 'result.pptx'
    triggerBrowserDownload(blob, filename)
    messages.update(messageId, {
      type: 'success',
      title: 'PPT 下载已开始',
      message: filename,
      persistent: false,
    })
    retireMessage(messageId, 3200)
  } catch (error) {
    messages.update(messageId, {
      type: 'error',
      title: 'PPT 下载失败',
      message: error instanceof Error ? error.message : '网络异常，请稍后重试。',
      persistent: false,
    })
    retireMessage(messageId, 5200)
  } finally {
    setDownloadingDelivery(delivery, false)
  }
}

function isExecutionError(text) {
  return String(text || '').startsWith('\u6267\u884c\u5f02\u5e38')
}

function getStreamText(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  const streamKeys = getEntityStreamKeys(placement)
  const chunks = streamKeys
    .map((key) => {
      const content = runtime.workerStates[key]?.streamedContent
      const keyText = String(key)
      const sourceIdText = String(sourceId)
      if (!content) return ''
      if (keyText === sourceIdText) return `main\n${content}`
      return `${keyText.replace(`${sourceIdText}:`, '')}\n${content}`
    })
    .filter(Boolean)
  return chunks.join('\n\n') || '\u65e0\u5b9e\u65f6\u8f93\u51fa'
}

function getEntityInfoSourceId(placement) {
  return placement?.infoSourceId || placement?.id
}

function getEntityWorkerKeys(placement) {
  if (!placement) return []
  return [...new Set([placement.id, placement.refId, getEntityInfoSourceId(placement)].filter(Boolean))]
}

function getEntityStreamKeys(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  return [...new Set([...getEntityWorkerKeys(placement), `${sourceId}:dispatch`, `${sourceId}:synthesis`])]
}

function getActiveWorkerState(placement) {
  const keys = getEntityWorkerKeys(placement)
  return keys.map((key) => runtime.workerStates[key]).find((item) => item?.isWorking) || null
}

function getEntityStatusText(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  const activeWorkerState = getActiveWorkerState(placement)
  const teamStatus = runtime.teamStatuses[sourceId]?.text || runtime.teamStatuses[placement.id]?.text || ''
  if (activeWorkerState?.isWorking) {
    return activeWorkerState.currentTask || teamStatus || '执行中'
  }
  return teamStatus || ui.idle
}

function getEntityQueue(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  return runtime.teamQueues[sourceId] || runtime.teamQueues[placement.id] || []
}

function getEntityTimeline(placement) {
  const sourceId = getEntityInfoSourceId(placement)
  const workerKeys = getEntityWorkerKeys(placement).map(String)
  return runtime.logs.filter((entry) => {
    const entityId = String(entry.entityId || '')
    const workerKey = String(entry.workerKey || '')
    return (
      workerKeys.includes(entityId) ||
      workerKeys.includes(workerKey) ||
      entityId === sourceId ||
      workerKey === sourceId ||
      workerKey.startsWith(`${sourceId}:`)
    )
  })
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

function matchesActivationType(placement, taskCard) {
  const context = getPlacementContext(placement)
  return (taskCard?.kind || 'text') === (context.activationType || 'text')
}

function getTaskInputRejectionText(placement, taskCard) {
  const context = getPlacementContext(placement)
  const required = context.activationType === 'word' ? 'Word 文件' : '任务描述'
  const received = taskCard?.kind === 'word' ? 'Word 文件' : '任务描述'
  return `[${displayName(placement)}] 只能接收${required}，当前拖入的是${received}。`
}

function assignTask(placement, taskCard) {
  if (!matchesActivationType(placement, taskCard)) {
    const message = getTaskInputRejectionText(placement, taskCard)
    runtime.log('sys', message, { entityId: placement.id })
    messages.error('无法分配任务', message)
    return
  }
  runtime.ensureTeamQueue(placement.id)
  runtime.enqueueTask(placement.id, taskCard.title, {
    placementId: placement.id,
    sourceTask: cloneValue(taskCard),
  })
  setPlacementStatus(placement, 'working', '准备执行中')
  setWorkerBusyState(placement, true, taskCard.title, '')
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
    const success = await generateApprovalDraft(placement, current.task, '', current.payload?.sourceTask || null)
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
  closeApprovalModal()
  runtime.resolveApproval(approval.id)
  setPlacementStatus(approval.nodeSnapshot, 'blocked', '\u5f85\u91cd\u65b0\u89c4\u5212')
  await generateApprovalDraft(
    approval.nodeSnapshot,
    approval.task,
    approval.feedback || '\u8bf7\u6309 Boss \u610f\u89c1\u91cd\u65b0\u62c6\u89e3',
    approval.sourceTask || null,
  )
}

async function submitReject(approval) {
  approval.feedback = rejectFeedback.value.trim()
  await rejectApproval(approval)
}

async function approveApproval(approval) {
  if (!approval) return
  const approvalSnapshot = cloneValue(approval)
  if (!approvalSnapshot?.nodeSnapshot) return
  const children = getManagedChildren(approvalSnapshot.nodeSnapshot)
  const validationError = validateApprovalPlan(approvalSnapshot.plan, children)
  if (validationError) {
    messages.error('审批内容仍不合法', validationError)
    return
  }

  approvalSnapshot.draft = renderApprovalPlan(approvalSnapshot.plan)
  runtime.resolveApproval(approvalSnapshot.id)
  closeApprovalModal()
  await executeTask(approvalSnapshot.nodeSnapshot, approvalSnapshot.task, approvalSnapshot.draft, {
    queued: true,
    deliverToBoss: true,
    sourceTask: approvalSnapshot.sourceTask,
    approvedPlan: approvalSnapshot.plan || null,
  })
}

function openApproval(approval) {
  selectedApproval.value = approval
  approvalEditMode.value = false
}

function closeApprovalModal() {
  selectedApproval.value = null
  approvalEditMode.value = false
  approvalTaskCollapse.value = {}
  closeRejectModal()
}

function openRejectModal(approval) {
  selectedApproval.value = approval
  rejectFeedback.value = approval?.feedback || ''
  rejectModalOpen.value = true
}

function closeRejectModal() {
  rejectModalOpen.value = false
  rejectFeedback.value = ''
}

function getApprovalTaskCollapseKey(approval, item, index) {
  return `${approval?.id || 'approval'}:${item?.id || index}`
}

function isApprovalTaskCollapsed(approval, item, index) {
  return approvalTaskCollapse.value[getApprovalTaskCollapseKey(approval, item, index)] === true
}

function toggleApprovalTaskCollapse(approval, item, index) {
  const key = getApprovalTaskCollapseKey(approval, item, index)
  approvalTaskCollapse.value = {
    ...approvalTaskCollapse.value,
    [key]: !approvalTaskCollapse.value[key],
  }
}

function getApprovalAssignableChildren(approval) {
  return approval?.nodeSnapshot ? getManagedChildren(approval.nodeSnapshot) : []
}

function syncApprovalAssignee(approval, taskItem) {
  const matched = getApprovalAssignableChildren(approval).find((child) => child.id === taskItem.assigneeId)
  if (!matched) return
  taskItem.assigneeName = displayName(matched)
}

function nextApprovalTaskId(plan) {
  const used = new Set((plan?.tasks || []).map((item) => String(item.id || '').trim()))
  let index = 1
  while (used.has(`t${index}`)) index += 1
  return `t${index}`
}

function addApprovalTask(approval) {
  if (!approval?.plan?.tasks) return
  const children = getApprovalAssignableChildren(approval)
  const firstChild = children[0]
  approval.plan.tasks.push({
    id: nextApprovalTaskId(approval.plan),
    title: '新增子任务',
    assigneeId: firstChild?.id || '',
    assigneeName: firstChild ? displayName(firstChild) : '',
    task: '',
    dependsOn: [],
    reason: '',
  })
}

function removeApprovalTask(approval, index) {
  if (!approval?.plan?.tasks?.length) return
  const removed = approval.plan.tasks[index]
  const collapseKey = getApprovalTaskCollapseKey(approval, removed, index)
  if (collapseKey in approvalTaskCollapse.value) {
    const nextState = { ...approvalTaskCollapse.value }
    delete nextState[collapseKey]
    approvalTaskCollapse.value = nextState
  }
  approval.plan.tasks.splice(index, 1)
  if (!removed?.id) return
  approval.plan.tasks.forEach((item) => {
    item.dependsOn = normalizeDependencyList(item.dependsOn).filter((depId) => depId !== removed.id)
  })
}

function getApprovalDependencyCandidates(plan, task) {
  return (plan?.tasks || []).filter((item) => item.id && item.id !== task?.id)
}

function toggleApprovalDependency(task, depId) {
  const current = new Set(normalizeDependencyList(task?.dependsOn))
  if (current.has(depId)) current.delete(depId)
  else current.add(depId)
  task.dependsOn = [...current]
}

function replaceTaskTemplatePlaceholders(value, replacements) {
  if (typeof value === 'string') {
    return value.replace(/\{\{\s*(taskTitle|task|fileName)\s*\}\}/g, (_, key) => replacements[key] || '')
  }
  if (Array.isArray(value)) return value.map((item) => replaceTaskTemplatePlaceholders(item, replacements))
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, replaceTaskTemplatePlaceholders(item, replacements)]),
    )
  }
  return value
}

function buildFixedPlanForPlacement(placement, task, sourceTask, fixedPlan) {
  if (!fixedPlan?.tasks?.length) return null
  const replacements = {
    taskTitle: task,
    task,
    fileName: sourceTask?.fileName || task,
  }
  const children = getManagedChildren(placement)
  const tasks = fixedPlan.tasks
    .map((item, index) => {
      const resolved = replaceTaskTemplatePlaceholders(cloneValue(item), replacements)
      const matched =
        children.find((child) => String(child.id) === String(resolved.assigneeId)) ||
        children.find((child) => String(child.refId) === String(resolved.assigneeRefId))
      if (!matched) return null
      return {
        id: resolved.id || `t${index + 1}`,
        title: resolved.title || `子任务 ${index + 1}`,
        assigneeId: matched.id,
        assigneeName: displayName(matched),
        task: resolved.task || '',
        dependsOn: normalizeDependencyList(resolved.dependsOn),
        reason: resolved.reason || '',
      }
    })
    .filter(Boolean)

  return {
    summary:
      replaceTaskTemplatePlaceholders(fixedPlan.summary || `执行任务：${task}`, replacements) || `执行任务：${task}`,
    deliverable:
      replaceTaskTemplatePlaceholders(fixedPlan.deliverable || `完成“${task}”的交付结果`, replacements) ||
      `完成“${task}”的交付结果`,
    tasks,
    risks: Array.isArray(fixedPlan.risks) ? fixedPlan.risks : [],
    openQuestions: Array.isArray(fixedPlan.openQuestions) ? fixedPlan.openQuestions : [],
  }
}

async function generateApprovalDraft(placement, task, feedback = '', sourceTask = null) {
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
  let plan = null
  if (context.fixedPlan?.tasks?.length) {
    plan = buildFixedPlanForPlacement(placement, task, sourceTask, context.fixedPlan)
  }

  const rawPlan = plan
    ? null
    : await runtime.runWorkerTask({
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

  plan = plan || extractJsonObjectPayload(rawPlan)
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
    sourceTask: sourceTask || runtime.teamQueues[placement.id]?.[0]?.payload?.sourceTask || null,
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

function escapeHtml(text) {
  return String(text || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
}

function renderMarkdown(markdown) {
  const lines = String(markdown || '').replace(/\r/g, '').split('\n')
  const html = []
  let inList = false

  function closeList() {
    if (inList) {
      html.push('</ul>')
      inList = false
    }
  }

  function inline(text) {
    return escapeHtml(text)
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
  }

  for (const line of lines) {
    if (!line.trim()) {
      closeList()
      continue
    }
    if (line.startsWith('## ')) {
      closeList()
      html.push(`<h2>${inline(line.slice(3))}</h2>`)
      continue
    }
    if (line.startsWith('- ')) {
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${inline(line.slice(2))}</li>`)
      continue
    }
    closeList()
    html.push(`<p>${inline(line)}</p>`)
  }

  closeList()
  return html.join('')
}

function getApprovalDependencyLabels(plan, task) {
  const taskMap = new Map((plan?.tasks || []).map((item) => [String(item.id || ''), item]))
  return normalizeDependencyList(task?.dependsOn).map((depId) => {
    const matched = taskMap.get(depId)
    return matched?.title ? `${depId} · ${matched.title}` : depId
  })
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

function buildBackendExecutionPlan(placement, task, approvedPlan, sourceTask = null) {
  if (approvedPlan?.tasks?.length) return approvedPlan
  const context = getPlacementContext(placement)
  if (context.role === 'manager' && context.fixedPlan?.tasks?.length) {
    const fixedExecutionPlan = buildFixedPlanForPlacement(
      placement,
      task,
      sourceTask,
      context.fixedPlan,
    )
    if (fixedExecutionPlan?.tasks?.length) return fixedExecutionPlan
  }
  return {
    summary: `执行任务：${task}`,
    deliverable: `完成“${task}”的交付结果`,
    tasks: [
      {
        id: 't1',
        title: task,
        assigneeId: String(placement.id),
        assigneeName: context.workerName,
        task,
        dependsOn: [],
        reason: '直接执行当前任务',
      },
    ],
    risks: [],
    openQuestions: [],
  }
}

function getWorkerConfigForPlacement(placement) {
  if (placement.kind === 'employee') {
    const employee = store.employeeMap[placement.refId]
    return employee
      ? {
          name: employee.name,
          prompt: employee.prompt || DEFAULT_WORKER_PROMPT,
          activationType: employee.activationType || 'text',
          deliverableType: employee.deliverableType || 'text',
          executionMode: employee.executionMode || 'llm',
          tools: employee.tools || [],
        }
      : null
  }

  const manager = getManagerEntity(placement)
  return manager
    ? {
        name: manager.name,
        prompt: manager.prompt || manager.plannerPrompt || DEFAULT_MANAGER_PLANNER,
        activationType: manager.activationType || 'text',
        deliverableType: manager.deliverableType || 'text',
        executionMode: manager.executionMode || 'llm',
        tools: manager.tools || [],
      }
    : null
}

function buildAssigneeConfigMap(placement, executionPlan) {
  const configMap = {}
  if (placement.kind === 'employee') {
    const config = getWorkerConfigForPlacement(placement)
    if (config) configMap[String(placement.id)] = config
    return configMap
  }

  const childMap = new Map(getManagedChildren(placement).map((child) => [String(child.id), child]))
  ;(executionPlan?.tasks || []).forEach((taskItem) => {
    const matched = childMap.get(String(taskItem.assigneeId))
    if (!matched) return
    const config = getWorkerConfigForPlacement(matched)
    if (!config) return
    configMap[String(taskItem.assigneeId)] = config
  })
  return configMap
}

function appendBackendTimeline(placement, timeline = []) {
  timeline.forEach((entry) => {
    const role = entry.stage === 'received' ? 'sys' : entry.stage.includes('worker') ? 'wrk' : 'mgr'
    const taskId = extractTaskIdFromTimelineMessage(entry.message)
    const flowTask = taskId ? runtime.taskFlows[String(placement.id)]?.tasks?.[taskId] : null
    const assigneePlacement = flowTask?.assigneeId ? findManagedPlacementById(placement, flowTask.assigneeId) : null
    runtime.log(role, `[${entry.actor}] ${entry.message}`, {
      entityId: placement.id,
      workerKey: assigneePlacement?.id || flowTask?.assigneeId || '',
      taskId: taskId || '',
    })
  })
}

function taskLabelForStream(stage, payload = {}) {
  if (stage === 'synthesizer') return '汇总最终交付'
  return payload.title || payload.taskId || '执行任务中'
}

function handleRuntimeStreamEvent(placement, eventName, payload = {}) {
  if (eventName === 'plan' && payload.plan) {
    runtime.upsertTaskFlow(String(placement.id), payload.plan, {
      rootId: String(placement.id),
      rootName: displayName(placement),
    })
    scheduleTaskFlowOverlayUpdate()
    return
  }

  if (eventName === 'timeline' && payload.entry) {
    appendBackendTimeline(placement, [payload.entry])
    const taskId = extractTaskIdFromTimelineMessage(payload.entry.message)
    if (taskId && payload.entry.stage === 'worker') {
      runtime.markTaskFlowTaskRunning(String(placement.id), taskId)
      const flowTask = runtime.taskFlows[String(placement.id)]?.tasks?.[taskId]
      const assigneePlacement = flowTask?.assigneeId
        ? findManagedPlacementById(placement, flowTask.assigneeId)
        : null
      if (assigneePlacement) {
        setWorkerBusyState(
          assigneePlacement,
          true,
          flowTask.title || taskId,
          runtime.workerStates[assigneePlacement.id]?.streamedContent || '',
        )
      }
      scheduleTaskFlowOverlayUpdate()
    }
    if (taskId && payload.entry.stage === 'worker_done') {
      runtime.markTaskFlowTaskDone(String(placement.id), taskId)
      const flowTask = runtime.taskFlows[String(placement.id)]?.tasks?.[taskId]
      const assigneePlacement = flowTask?.assigneeId
        ? findManagedPlacementById(placement, flowTask.assigneeId)
        : null
      if (assigneePlacement) {
        setWorkerBusyState(
          assigneePlacement,
          false,
          flowTask.title || taskId,
          runtime.workerStates[assigneePlacement.id]?.streamedContent || '',
        )
      }
      scheduleTaskFlowOverlayUpdate()
    }
    return
  }

  if (eventName === 'chunk') {
    const stage = payload.stage || 'worker'
    if (stage === 'synthesizer') {
      runtime.patchWorkerState(`${placement.id}:synthesis`, {
        streamedContent: payload.fullText || '',
        isWorking: true,
        currentTask: taskLabelForStream(stage, payload),
      })
    } else {
      const assigneePlacement = payload.assigneeId
        ? findManagedPlacementById(placement, payload.assigneeId)
        : null
      setWorkerBusyState(
        assigneePlacement || placement,
        true,
        taskLabelForStream(stage, payload),
        payload.fullText || '',
      )
    }
    return
  }

  if (eventName === 'worker_result' && payload.assignee_name) {
    const assigneePlacement = payload.assignee_id
      ? findManagedPlacementById(placement, payload.assignee_id)
      : null
    if (assigneePlacement) {
      setWorkerBusyState(assigneePlacement, false, payload.title || '', payload.result || '')
    }
    runtime.log('wrk', `[${payload.assignee_name}] 已产出结果 -> ${payload.title}`, {
      entityId: placement.id,
      workerKey: assigneePlacement?.id || payload.assignee_id || '',
      taskId: payload.task_id || '',
    })
  }
}

async function executeTask(placement, task, approvedDraft = '', options = {}) {
  const { queued = false, deliverToBoss = true, sourceTask = null, approvedPlan = null } = options
  const context = getPlacementContext(placement)
  setPlacementStatus(placement, 'working', '\u4efb\u52a1\u6267\u884c\u4e2d')
  setWorkerBusyState(placement, true, task, '')
  runtime.patchWorkerState(`${placement.id}:synthesis`, {
    streamedContent: '',
    isWorking: false,
  })

  let result = ''

  try {
    if (!authStore.authToken) {
      throw new Error('未检测到后端登录态，请先重新登录')
    }

    const executionPlan = buildBackendExecutionPlan(placement, task, approvedPlan, sourceTask)
    const assigneeConfigs = buildAssigneeConfigMap(placement, executionPlan)
    const runtimeResult = await executeRuntimeTask({
      token: authStore.authToken,
      task,
      managerId: String(placement.id),
      managerName: context.workerName,
      approvedPlan: executionPlan,
      context: {
        role: context.role,
        approvedDraft,
        taskInput:
          sourceTask || {
            id: createId('task'),
            kind: 'text',
            title: task,
            text: task,
          },
        managerConfig: {
          activationType: context.activationType || 'text',
          deliverableType: context.deliverableType || 'text',
          fixedPlan: context.fixedPlan || null,
        },
        assigneeConfigs,
      },
      onEvent: ({ event, payload }) => handleRuntimeStreamEvent(placement, event, payload),
    })
    result = runtimeResult.finalResult || ''

    if (deliverToBoss) {
      recordDelivery({
        sender: context.workerName,
        task,
        result,
        sourcePlanId: runtimeResult.plan?.id || '',
        deliverable: runtimeResult.finalDeliverable || null,
      })
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error || '')
    if (error?.status === 401 || error?.code === 'UNAUTHORIZED') {
      await authStore.logout()
      messages.error('登录已失效', sessionExpiredMessage)
      await router.push({
        path: '/login',
        query: { redirect: router.currentRoute.value.fullPath, reason: 'expired' },
      })
      result = `执行异常: ${sessionExpiredMessage}`
    } else {
      runtime.log('sys', `任务执行异常详情 -> ${errorMessage}`, {
        entityId: placement.id,
      })
      result = `执行异常: ${errorMessage}`
    }
  }

  setWorkerBusyState(placement, false)
  runtime.patchWorkerState(`${placement.id}:synthesis`, {
    isWorking: false,
  })

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

function updateViewportSize() {
  const rect = viewportRef.value?.getBoundingClientRect()
  if (!rect) return
  viewportSize.value = {
    width: Math.max(320, Math.round(rect.width)),
    height: Math.max(240, Math.round(rect.height)),
  }
}

function fitViewportToContent() {
  updateViewportSize()
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
  window.removeEventListener('resize', fitViewportToContent)
  window.removeEventListener('resize', updateFloorCalloutPosition)
})

onMounted(() => {
  updateViewportSize()
  window.addEventListener('resize', fitViewportToContent)
  window.addEventListener('resize', updateFloorCalloutPosition)
  nextTick(() => {
    fitViewportToContent()
    updateFloorCalloutPosition()
  })
})

watch(
  [currentPlacements, leftSidebarCollapsed, rightSidebarCollapsed, logsCollapsed],
  async () => {
    await nextTick()
    fitViewportToContent()
    updateFloorCalloutPosition()
  },
  { deep: true },
)

watch(currentFloorId, () => {
  scheduleFloorCalloutPositionUpdate()
})

watch(
  () => store.floors.map((floor) => floor.id).join('|'),
  () => {
    scheduleFloorCalloutPositionUpdate()
  },
)
</script>
