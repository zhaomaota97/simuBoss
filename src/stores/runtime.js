import { computed, ref } from 'vue'
import { watch } from 'vue'
import { defineStore } from 'pinia'
import { streamChatCompletion } from '../services/llm'
import { createDebouncedWorkspaceSaver } from '../services/api'

export const useRuntimeStore = defineStore('runtime', () => {
  const approvals = ref([])
  const deliveries = ref([])
  const logs = ref([
    { id: crypto.randomUUID(), role: 'sys', text: '系统启动完成，已同步本地数据。' },
  ])
  const teamQueues = ref({})
  const teamStatuses = ref({})
  const workerStates = ref({})
  const taskFlows = ref({})
  const workerLocks = new Map()
  const persistenceReady = ref(false)

  function serialize() {
    return {
      approvals: approvals.value,
      deliveries: deliveries.value,
      logs: logs.value,
      teamQueues: teamQueues.value,
      teamStatuses: teamStatuses.value,
      workerStates: workerStates.value,
      taskFlows: taskFlows.value,
    }
  }

  function hydrate(data = {}) {
    persistenceReady.value = false
    approvals.value = Array.isArray(data.approvals) ? data.approvals : []
    deliveries.value = Array.isArray(data.deliveries) ? data.deliveries : []
    logs.value = Array.isArray(data.logs) && data.logs.length
      ? data.logs
      : [{ id: crypto.randomUUID(), role: 'sys', text: '系统启动完成，已同步数据库数据。' }]
    teamQueues.value = data.teamQueues && typeof data.teamQueues === 'object' ? data.teamQueues : {}
    teamStatuses.value = data.teamStatuses && typeof data.teamStatuses === 'object' ? data.teamStatuses : {}
    workerStates.value = data.workerStates && typeof data.workerStates === 'object' ? data.workerStates : {}
    taskFlows.value = data.taskFlows && typeof data.taskFlows === 'object' ? data.taskFlows : {}
    window.setTimeout(() => {
      persistenceReady.value = true
    }, 0)
  }

  const scheduleSave = createDebouncedWorkspaceSaver('runtime', serialize)

  watch(
    [approvals, deliveries, logs, teamQueues, teamStatuses, workerStates, taskFlows],
    () => {
      if (persistenceReady.value) scheduleSave()
    },
    { deep: true },
  )

  const approvalCount = computed(() => approvals.value.length)

  function log(role, text, meta = {}) {
    logs.value.push({ id: crypto.randomUUID(), role, text, time: new Date(), ...meta })
  }

  function ensureTeamQueue(teamId) {
    if (!teamQueues.value[teamId]) {
      teamQueues.value = {
        ...teamQueues.value,
        [teamId]: [],
      }
    }
    if (!teamStatuses.value[teamId]) {
      teamStatuses.value = {
        ...teamStatuses.value,
        [teamId]: { state: 'idle', text: '空闲等待任务' },
      }
    }
    return teamQueues.value[teamId]
  }

  function setTeamStatus(teamId, state, text) {
    teamStatuses.value = {
      ...teamStatuses.value,
      [teamId]: { state, text },
    }
  }

  function enqueueTask(teamId, task, payload = {}) {
    const queue = ensureTeamQueue(teamId)
    teamQueues.value = {
      ...teamQueues.value,
      [teamId]: [
        ...queue,
        {
          id: crypto.randomUUID(),
          task,
          payload,
        },
      ],
    }
  }

  function shiftTask(teamId) {
    const queue = ensureTeamQueue(teamId)
    const [head, ...rest] = queue
    teamQueues.value = {
      ...teamQueues.value,
      [teamId]: rest,
    }
    return head
  }

  function createApproval(entry) {
    approvals.value.unshift({
      id: crypto.randomUUID(),
      createdAt: Date.now(),
      feedback: '',
      ...entry,
    })
  }

  function resolveApproval(id) {
    approvals.value = approvals.value.filter((item) => item.id !== id)
  }

  function addDelivery(entry) {
    deliveries.value.unshift({
      id: crypto.randomUUID(),
      createdAt: Date.now(),
      ...entry,
    })
  }

  function ensureWorkerState(workerKey) {
    if (!workerStates.value[workerKey]) {
      workerStates.value = {
        ...workerStates.value,
        [workerKey]: {
          isWorking: false,
          currentTask: '无任务',
          streamedContent: '',
          queue: [],
        },
      }
    }
    return workerStates.value[workerKey]
  }

  function patchWorkerState(workerKey, patch) {
    const current = ensureWorkerState(workerKey)
    workerStates.value = {
      ...workerStates.value,
      [workerKey]: {
        ...current,
        ...patch,
      },
    }
    return workerStates.value[workerKey]
  }

  function upsertTaskFlow(ownerKey, plan, meta = {}) {
    if (!ownerKey || !plan?.tasks?.length) return null
    const previous = taskFlows.value[ownerKey]
    const previousTasks = previous?.tasks || {}
    const nextTasks = Object.fromEntries(
      plan.tasks.map((task) => {
        const existing = previousTasks[task.id] || {}
        return [
          task.id,
          {
            ...task,
            status: existing.status || (task.dependsOn?.length ? 'pending' : 'ready'),
            result: existing.result || '',
            error: existing.error || '',
          },
        ]
      }),
    )

    taskFlows.value = {
      ...taskFlows.value,
      [ownerKey]: {
        ownerKey,
        rootId: meta.rootId || previous?.rootId || ownerKey,
        rootName: meta.rootName || previous?.rootName || '',
        summary: plan.summary || previous?.summary || '',
        deliverable: plan.deliverable || previous?.deliverable || '',
        tasks: nextTasks,
        taskOrder: plan.tasks.map((task) => task.id),
        updatedAt: Date.now(),
      },
    }
    return taskFlows.value[ownerKey]
  }

  function patchTaskFlowTask(ownerKey, taskId, patch) {
    const flow = taskFlows.value[ownerKey]
    if (!flow?.tasks?.[taskId]) return null
    const nextTask = {
      ...flow.tasks[taskId],
      ...patch,
    }
    taskFlows.value = {
      ...taskFlows.value,
      [ownerKey]: {
        ...flow,
        tasks: {
          ...flow.tasks,
          [taskId]: nextTask,
        },
        updatedAt: Date.now(),
      },
    }
    return nextTask
  }

  function markTaskFlowTaskRunning(ownerKey, taskId) {
    return patchTaskFlowTask(ownerKey, taskId, { status: 'running', error: '' })
  }

  function markTaskFlowTaskDone(ownerKey, taskId, result = '') {
    const task = patchTaskFlowTask(ownerKey, taskId, { status: 'done', result, error: '' })
    if (!task) return null
    const flow = taskFlows.value[ownerKey]
    const completed = new Set(
      Object.values(flow.tasks)
        .filter((item) => item.status === 'done')
        .map((item) => item.id),
    )

    const patchedTasks = Object.fromEntries(
      Object.entries(flow.tasks).map(([id, item]) => {
        if (item.status === 'pending' && (item.dependsOn || []).every((depId) => completed.has(depId))) {
          return [id, { ...item, status: 'ready' }]
        }
        return [id, item]
      }),
    )

    taskFlows.value = {
      ...taskFlows.value,
      [ownerKey]: {
        ...flow,
        tasks: patchedTasks,
        updatedAt: Date.now(),
      },
    }
    return taskFlows.value[ownerKey]
  }

  function markTaskFlowTaskFailed(ownerKey, taskId, error = '') {
    return patchTaskFlowTask(ownerKey, taskId, { status: 'failed', error })
  }

  function clearTaskFlow(ownerKey) {
    if (!ownerKey || !taskFlows.value[ownerKey]) return
    const next = { ...taskFlows.value }
    delete next[ownerKey]
    taskFlows.value = next
  }

  async function runWorkerTask({ workerKey, workerName, systemPrompt, userPrompt }) {
    const state = ensureWorkerState(workerKey)
    patchWorkerState(workerKey, {
      queue: [...(state.queue || []), userPrompt],
    })
    const prior = workerLocks.get(workerKey) || Promise.resolve()

    const currentRun = prior.then(async () => {
      patchWorkerState(workerKey, {
        isWorking: true,
        currentTask: userPrompt,
        streamedContent: '',
      })
      log('wrk', `[${workerName}] 开始专注处理 "${userPrompt}"`)

      try {
        const result = await streamChatCompletion({
          systemPrompt,
          userPrompt,
          onChunk: (_, fullText) => {
            patchWorkerState(workerKey, {
              streamedContent: fullText,
            })
          },
        })
        return result
      } catch (error) {
        const message = String(error?.message || error)
        patchWorkerState(workerKey, {
          streamedContent: message,
        })
        return `执行异常: ${message}`
      } finally {
        const latest = workerStates.value[workerKey] || state
        patchWorkerState(workerKey, {
          queue: (latest.queue || []).slice(1),
          isWorking: false,
          currentTask: '无任务',
        })
      }
    })

    workerLocks.set(workerKey, currentRun.catch(() => null))
    return currentRun
  }

  function clearRuntime() {
    approvals.value = []
    deliveries.value = []
    logs.value = [{ id: crypto.randomUUID(), role: 'sys', text: '系统运行态已重置。' }]
    teamQueues.value = {}
    teamStatuses.value = {}
    workerStates.value = {}
    taskFlows.value = {}
    if (persistenceReady.value) scheduleSave()
  }

  return {
    approvals,
    deliveries,
    logs,
    teamQueues,
    teamStatuses,
    workerStates,
    taskFlows,
    serialize,
    hydrate,
    approvalCount,
    log,
    ensureTeamQueue,
    setTeamStatus,
    enqueueTask,
    shiftTask,
    createApproval,
    resolveApproval,
    addDelivery,
    ensureWorkerState,
    patchWorkerState,
    upsertTaskFlow,
    patchTaskFlowTask,
    markTaskFlowTaskRunning,
    markTaskFlowTaskDone,
    markTaskFlowTaskFailed,
    clearTaskFlow,
    runWorkerTask,
    clearRuntime,
  }
})
