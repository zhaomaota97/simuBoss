import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { streamChatCompletion } from '../services/llm'

export const useRuntimeStore = defineStore('runtime', () => {
  const approvals = ref([])
  const deliveries = ref([])
  const logs = ref([{ id: crypto.randomUUID(), role: 'sys', text: '系统启动完成，已同步本地数据。' }])
  const teamQueues = ref({})
  const teamStatuses = ref({})
  const workerStates = ref({})
  const workerLocks = new Map()

  const approvalCount = computed(() => approvals.value.length)

  function log(role, text, meta = {}) {
    logs.value.push({ id: crypto.randomUUID(), role, text, time: new Date(), ...meta })
  }

  function ensureTeamQueue(teamId) {
    if (!teamQueues.value[teamId]) teamQueues.value[teamId] = []
    if (!teamStatuses.value[teamId]) teamStatuses.value[teamId] = { state: 'idle', text: '空闲等待任务' }
    return teamQueues.value[teamId]
  }

  function setTeamStatus(teamId, state, text) {
    teamStatuses.value[teamId] = { state, text }
  }

  function enqueueTask(teamId, task, payload = {}) {
    const queue = ensureTeamQueue(teamId)
    queue.push({
      id: crypto.randomUUID(),
      task,
      payload,
    })
  }

  function shiftTask(teamId) {
    const queue = ensureTeamQueue(teamId)
    return queue.shift()
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
      workerStates.value[workerKey] = {
        isWorking: false,
        currentTask: '无任务',
        streamedContent: '',
        queue: [],
      }
    }
    return workerStates.value[workerKey]
  }

  async function runWorkerTask({ workerKey, workerName, systemPrompt, userPrompt, entityId = "" }) {
    const state = ensureWorkerState(workerKey)
    state.queue.push(userPrompt)
    const prior = workerLocks.get(workerKey) || Promise.resolve()

    const currentRun = prior.then(async () => {
      state.isWorking = true
      state.currentTask = userPrompt
      state.streamedContent = ''
      log('wrk', `[${workerName}] 开始专注处理 "${userPrompt}"`)

      try {
        const result = await streamChatCompletion({
          systemPrompt,
          userPrompt,
          onChunk: (_, fullText) => {
            state.streamedContent = fullText
          },
        })
        return result
      } catch (error) {
        state.streamedContent = String(error?.message || error)
        return `执行异常: ${state.streamedContent}`
      } finally {
        state.queue.shift()
        state.isWorking = false
        state.currentTask = '无任务'
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
  }

  return {
    approvals,
    deliveries,
    logs,
    teamQueues,
    teamStatuses,
    workerStates,
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
    runWorkerTask,
    clearRuntime,
  }
})
