function normalizeDependencyList(value) {
  return Array.isArray(value)
    ? value.map((item) => String(item || '').trim()).filter(Boolean)
    : []
}

function buildTaskRecord(task) {
  return {
    ...task,
    taskId: String(task.taskId || task.id || '').trim(),
    dependsOn: normalizeDependencyList(task.dependsOn),
    status: 'pending',
    result: '',
    error: '',
  }
}

export async function runPlanScheduler({
  assignments,
  executeAssignment,
  isExecutionError,
  onLog = () => {},
}) {
  const taskMap = new Map(
    (assignments || []).map((assignment) => {
      const record = buildTaskRecord(assignment)
      return [record.taskId, record]
    }),
  )

  const results = []

  while (true) {
    const pendingTasks = [...taskMap.values()].filter((task) => task.status === 'pending')
    if (!pendingTasks.length) break

    let progressMade = false

    for (const task of pendingTasks) {
      const dependencyStates = task.dependsOn.map((depId) => taskMap.get(depId)).filter(Boolean)
      if (dependencyStates.some((dep) => dep.status === 'failed' || dep.status === 'blocked')) {
        task.status = 'blocked'
        task.error = '依赖任务异常，当前任务未被调度'
        onLog('blocked', task)
        progressMade = true
      }
    }

    const readyTasks = [...taskMap.values()].filter(
      (task) =>
        task.status === 'pending' &&
        task.dependsOn.every((depId) => taskMap.get(depId)?.status === 'done'),
    )

    if (!readyTasks.length) {
      if (!progressMade) {
        for (const task of pendingTasks) {
          if (task.status === 'pending') {
            task.status = 'blocked'
            task.error = '没有可继续推进的任务，调度器已停止'
            onLog('stalled', task)
          }
        }
      }
      break
    }

    progressMade = true
    await Promise.all(
      readyTasks.map(async (task) => {
        task.status = 'running'
        onLog('start', task)
        const dependencyResults = task.dependsOn
          .map((depId) => taskMap.get(depId))
          .filter((dep) => dep?.status === 'done')

        const result = await executeAssignment(task, dependencyResults)
        task.result = result
        if (isExecutionError(result)) {
          task.status = 'failed'
          task.error = String(result || '')
          onLog('failed', task)
          return
        }

        task.status = 'done'
        onLog('done', task)
        results.push({
          taskId: task.taskId,
          title: task.title || task.task || '',
          assignee: task.assigneeName || task.assigneeId,
          kind: task.assigneeKind || '',
          task: task.task || '',
          dependsOn: dependencyResults.map((dep) => dep.assigneeName || dep.assigneeId),
          dependencyResults: dependencyResults.map((dep) => ({
            taskId: dep.taskId,
            title: dep.title || dep.task || '',
            assignee: dep.assigneeName || dep.assigneeId,
            result: dep.result || '',
          })),
          result,
        })
      }),
    )
  }

  return {
    tasks: [...taskMap.values()],
    taskResults: results,
    hasFailures: [...taskMap.values()].some((task) => task.status === 'failed'),
    hasBlocked: [...taskMap.values()].some((task) => task.status === 'blocked'),
  }
}
