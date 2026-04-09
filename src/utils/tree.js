export function cloneDeep(value) {
  return JSON.parse(JSON.stringify(value))
}

export function resolveNode(rawNode, emps, teams) {
  if (!rawNode) return null
  if (rawNode.type === 'team_ref') {
    const team = teams.find((item) => item.id === rawNode.refId)
    return team
      ? { ...team, role: 'team', type: 'team_resolved', children: [] }
      : { id: rawNode.refId, icon: '❓', name: '失效的团队引用', role: 'team', type: 'team_resolved', children: [] }
  }

  if (rawNode.type === 'emp_ref') {
    const emp = emps.find((item) => item.id === rawNode.refId)
    return emp
      ? { ...emp, type: 'emp_resolved', children: rawNode.children || [] }
      : { id: rawNode.refId, icon: '❓', name: '失效的员工引用', role: 'worker', type: 'emp_resolved', children: rawNode.children || [] }
  }

  return rawNode
}

export function countHierarchy(nodes, emps, teams) {
  let managerCount = 0
  let workerCount = 0

  ;(nodes || []).forEach((rawNode) => {
    const node = resolveNode(rawNode, emps, teams)
    if (!node) return

    if (node.role === 'manager') managerCount += 1
    if (node.role === 'worker') workerCount += 1

    if (rawNode.type === 'team_ref' && node.members) {
      const child = countHierarchy(node.members, emps, teams)
      managerCount += child.managerCount
      workerCount += child.workerCount
      return
    }

    if (rawNode.children?.length) {
      const child = countHierarchy(rawNode.children, emps, teams)
      managerCount += child.managerCount
      workerCount += child.workerCount
    }
  })

  return { managerCount, workerCount }
}

export function getTeamDesc(members, emps, teams) {
  const { managerCount, workerCount } = countHierarchy(members, emps, teams)
  if (!managerCount && !workerCount) return '未挂载实质产能的空壳组'
  const chunks = []
  if (managerCount) chunks.push(`包含 ${managerCount} 个经理`)
  if (workerCount) chunks.push(`统领 ${workerCount} 名工人`)
  return `建制链：${chunks.join('，')}`
}

export function findRootManagerNode(members, emps, teams) {
  for (const rawNode of members || []) {
    const node = resolveNode(rawNode, emps, teams)
    if (!node) continue
    if (node.role === 'manager') return node
    if (rawNode.type === 'team_ref') {
      const nested = findRootManagerNode(node.members, emps, teams)
      if (nested) return nested
    }
    if (rawNode.children?.length) {
      const nested = findRootManagerNode(rawNode.children, emps, teams)
      if (nested) return nested
    }
  }
  return null
}

export function flattenWorkerNodes(nodes, emps, teams, bucket = []) {
  ;(nodes || []).forEach((rawNode) => {
    const node = resolveNode(rawNode, emps, teams)
    if (!node) return
    if (node.role === 'worker') {
      bucket.push(node)
    }
    if (rawNode.type === 'team_ref' && node.members) {
      flattenWorkerNodes(node.members, emps, teams, bucket)
      return
    }
    if (rawNode.children?.length) {
      flattenWorkerNodes(rawNode.children, emps, teams, bucket)
    }
  })
  return bucket
}

export function hasCircularTeamRef(targetTeamId, refIdToInsert, teams) {
  if (!targetTeamId) return false
  if (targetTeamId === refIdToInsert) return true
  const targetTeam = teams.find((item) => item.id === refIdToInsert)
  if (!targetTeam?.members) return false

  for (const member of targetTeam.members) {
    if (member.type === 'team_ref' && hasCircularTeamRef(targetTeamId, member.refId, teams)) {
      return true
    }
  }

  return false
}
