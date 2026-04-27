import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'
import { SEED_ROLE_PROMPTS } from '../config/prompts'
import { cloneDeep, getTeamDesc } from '../utils/tree'

const STORAGE_VERSION = 'boss-sim-seed-v2'

const TEXT = {
  cloneSuffix: ' (\u526f\u672c)',
  defaultFloorName: '\u4e3b\u529e\u516c\u533a',
  floor2Name: '\u7814\u53d1\u4e2d\u5fc3',
  floor3Name: '\u7b56\u7565\u4e0e\u4ea4\u4ed8',
  newFloorName: '\u65b0\u90e8\u95e8',
}

function normalizeFloorName(name, fallback = TEXT.newFloorName) {
  const cleaned = String(name || '')
    .replace(/^\s*\d+\s*层\s*[-－]\s*/, '')
    .trim()

  return cleaned || fallback
}

function normalizeActivationType(value) {
  return value === 'word' ? 'word' : 'text'
}

function normalizeDeliverableType(value) {
  return value === 'ppt' ? 'ppt' : 'text'
}

function normalizeExecutionMode(value) {
  return value === 'ppt_renderer' ? 'ppt_renderer' : 'llm'
}

function normalizeFixedPlan(value) {
  if (!value || typeof value !== 'object') return null
  const tasks = Array.isArray(value.tasks) ? value.tasks : []
  return {
    summary: String(value.summary || '').trim(),
    deliverable: String(value.deliverable || '').trim(),
    tasks: tasks.map((task, index) => ({
      id: String(task.id || `t${index + 1}`).trim() || `t${index + 1}`,
      title: String(task.title || '').trim(),
      assigneeId: String(task.assigneeId || '').trim(),
      assigneeRefId: String(task.assigneeRefId || '').trim(),
      assigneeName: String(task.assigneeName || '').trim(),
      task: String(task.task || '').trim(),
      dependsOn: Array.isArray(task.dependsOn)
        ? task.dependsOn.map((item) => String(item || '').trim()).filter(Boolean)
        : [],
      reason: String(task.reason || '').trim(),
    })),
    risks: Array.isArray(value.risks)
      ? value.risks.map((item) => String(item || '').trim()).filter(Boolean)
      : [],
    openQuestions: Array.isArray(value.openQuestions)
      ? value.openQuestions.map((item) => String(item || '').trim()).filter(Boolean)
      : [],
  }
}

function sanitizeEmployeePayload(payload = {}) {
  return {
    ...payload,
    locked: Boolean(payload.locked),
    hidden: Boolean(payload.hidden),
    source: payload.source || 'local',
    activationType: normalizeActivationType(payload.activationType),
    deliverableType: normalizeDeliverableType(payload.deliverableType),
    executionMode: normalizeExecutionMode(payload.executionMode),
    fixedPlan: normalizeFixedPlan(payload.fixedPlan),
  }
}

function sanitizeTeamPayload(payload = {}) {
  return {
    ...payload,
    locked: Boolean(payload.locked),
    source: payload.source || 'local',
    bundledEmployeeIds: Array.isArray(payload.bundledEmployeeIds)
      ? [...payload.bundledEmployeeIds]
      : [],
  }
}

const DEFAULT_EMPS = [
  {
    id: 101,
    icon: 'RS',
    name: '\u60c5\u62a5\u7814\u7a76\u5458',
    role: 'worker',
    tools: ['Search_Engines', 'HTTP_Scraper', 'Knowledge_Base'],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.workers.research,
    temperature: 0.3,
    maxTokens: 4096,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 102,
    icon: 'WR',
    name: '\u65b9\u6848\u5199\u4f5c\u5de5\u4eba',
    role: 'worker',
    tools: ['Write_File', 'Read_Context', 'Markdown_Editor'],
    model: 'claude-3-5-sonnet-20240620',
    prompt: SEED_ROLE_PROMPTS.workers.writing,
    temperature: 0.7,
    maxTokens: 8192,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 103,
    icon: 'DE',
    name: '\u4ea4\u4e92\u8bbe\u8ba1\u5de5\u4eba',
    role: 'worker',
    tools: ['Figma_Export', 'Wireframe', 'Design_System'],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.workers.design,
    temperature: 0.5,
    maxTokens: 4096,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 104,
    icon: 'FE',
    name: '\u524d\u7aef\u5f00\u53d1\u5de5\u4eba',
    role: 'worker',
    tools: ['Vue', 'Tailwind', 'Vite'],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.workers.frontend,
    temperature: 0.2,
    maxTokens: 8192,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 105,
    icon: 'BE',
    name: '\u540e\u7aef\u5de5\u7a0b\u5de5\u4eba',
    role: 'worker',
    tools: ['Node', 'Express', 'Database'],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.workers.backend,
    temperature: 0.2,
    maxTokens: 8192,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 106,
    icon: 'QA',
    name: '\u8d28\u68c0\u6d4b\u8bd5\u5de5\u4eba',
    role: 'worker',
    tools: ['Playwright', 'Checklist', 'Bug_Report'],
    model: 'gpt-4o-mini',
    prompt: SEED_ROLE_PROMPTS.workers.qa,
    temperature: 0.2,
    maxTokens: 4096,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 107,
    icon: 'AN',
    name: '\u5546\u4e1a\u5206\u6790\u5de5\u4eba',
    role: 'worker',
    tools: ['Spreadsheet', 'SQL_Read', 'Dashboard'],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.workers.analysis,
    temperature: 0.3,
    maxTokens: 4096,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 108,
    icon: 'OP',
    name: '\u8fd0\u8425\u6267\u884c\u5de5\u4eba',
    role: 'worker',
    tools: ['SOP', 'Calendar', 'Campaign_Board'],
    model: 'gpt-4o-mini',
    prompt: SEED_ROLE_PROMPTS.workers.operations,
    temperature: 0.4,
    maxTokens: 4096,
    activationType: 'text',
    deliverableType: 'text',
    executionMode: 'llm',
  },
  {
    id: 201,
    icon: 'PM',
    name: '\u4ea7\u54c1\u7ecf\u7406',
    role: 'manager',
    tools: [],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.managers.product.prompt,
    plannerPrompt: SEED_ROLE_PROMPTS.managers.product.planner,
    synthesizerPrompt: SEED_ROLE_PROMPTS.managers.product.synthesizer,
    temperature: 0.6,
    maxTokens: 4096,
    requireApproval: true,
    activationType: 'text',
    deliverableType: 'text',
  },
  {
    id: 202,
    icon: 'TL',
    name: '\u6280\u672f\u7ecf\u7406',
    role: 'manager',
    tools: [],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.managers.technical.prompt,
    plannerPrompt: SEED_ROLE_PROMPTS.managers.technical.planner,
    synthesizerPrompt: SEED_ROLE_PROMPTS.managers.technical.synthesizer,
    temperature: 0.5,
    maxTokens: 4096,
    requireApproval: true,
    activationType: 'text',
    deliverableType: 'text',
  },
  {
    id: 203,
    icon: 'ST',
    name: '\u7b56\u7565\u603b\u76d1',
    role: 'manager',
    tools: [],
    model: 'gpt-4o',
    prompt: SEED_ROLE_PROMPTS.managers.strategy.prompt,
    plannerPrompt: SEED_ROLE_PROMPTS.managers.strategy.planner,
    synthesizerPrompt: SEED_ROLE_PROMPTS.managers.strategy.synthesizer,
    temperature: 0.7,
    maxTokens: 4096,
    requireApproval: true,
    activationType: 'text',
    deliverableType: 'text',
  },
]

const DEFAULT_TEAMS = [
  {
    id: 301,
    icon: 'PR',
    name: '\u4ea7\u54c1\u7814\u53d1\u5c0f\u961f',
    desc: '\u4ea7\u54c1 + \u524d\u7aef + \u540e\u7aef + \u8d28\u68c0',
    members: [
      {
        type: 'emp_ref',
        refId: 201,
        children: [
          { type: 'emp_ref', refId: 103, children: [] },
          { type: 'emp_ref', refId: 104, children: [] },
          { type: 'emp_ref', refId: 105, children: [] },
          { type: 'emp_ref', refId: 106, children: [] },
        ],
      },
    ],
  },
  {
    id: 302,
    icon: 'IN',
    name: '\u60c5\u62a5\u5185\u5bb9\u5c0f\u961f',
    desc: '\u7814\u7a76 + \u5199\u4f5c + \u5206\u6790',
    members: [
      {
        type: 'emp_ref',
        refId: 203,
        children: [
          { type: 'emp_ref', refId: 101, children: [] },
          { type: 'emp_ref', refId: 102, children: [] },
          { type: 'emp_ref', refId: 107, children: [] },
        ],
      },
    ],
  },
  {
    id: 303,
    icon: 'GT',
    name: '\u589e\u957f\u8fd0\u8425\u5c0f\u961f',
    desc: '\u7b56\u7565 + \u8fd0\u8425 + \u5206\u6790 + \u8bbe\u8ba1',
    members: [
      {
        type: 'emp_ref',
        refId: 203,
        children: [
          { type: 'emp_ref', refId: 108, children: [] },
          { type: 'emp_ref', refId: 107, children: [] },
          { type: 'emp_ref', refId: 103, children: [] },
        ],
      },
    ],
  },
  {
    id: 304,
    icon: 'EN',
    name: '\u5de5\u7a0b\u4ea4\u4ed8\u5c0f\u961f',
    desc: '\u6280\u672f + \u524d\u7aef + \u540e\u7aef + \u8d28\u68c0',
    members: [
      {
        type: 'emp_ref',
        refId: 202,
        children: [
          { type: 'emp_ref', refId: 104, children: [] },
          { type: 'emp_ref', refId: 105, children: [] },
          { type: 'emp_ref', refId: 106, children: [] },
        ],
      },
    ],
  },
]

const DEFAULT_FLOORS = [
  { id: 'floor-1', name: TEXT.defaultFloorName, scale: 1 },
  { id: 'floor-2', name: TEXT.floor2Name, scale: 1 },
  { id: 'floor-3', name: TEXT.floor3Name, scale: 1 },
]

const DEFAULT_CANVAS = {
  'floor-1': [],
  'floor-2': [],
  'floor-3': [],
}

const DEFAULT_FLOOR_ASSIGNMENTS = {
  'floor-1': [],
  'floor-2': [],
  'floor-3': [],
}

export const useSimuBossStore = defineStore('simuBoss', () => {
  const seedVersion = useStorage('sb_seed_version', '')
  const employees = useStorage('sb_emps', cloneDeep(DEFAULT_EMPS))
  const teams = useStorage('sb_teams', cloneDeep(DEFAULT_TEAMS))
  const floors = useStorage('sb_floors', cloneDeep(DEFAULT_FLOORS))
  const canvasLayouts = useStorage('sb_canvas_layouts', cloneDeep(DEFAULT_CANVAS))
  const floorAssignments = useStorage(
    'sb_floor_assignments',
    cloneDeep(DEFAULT_FLOOR_ASSIGNMENTS),
  )
  const nextIdSeed = ref(Date.now())

  function resetSeedData() {
    employees.value = cloneDeep(DEFAULT_EMPS)
    teams.value = cloneDeep(DEFAULT_TEAMS)
    floors.value = cloneDeep(DEFAULT_FLOORS)
    canvasLayouts.value = cloneDeep(DEFAULT_CANVAS)
    floorAssignments.value = cloneDeep(DEFAULT_FLOOR_ASSIGNMENTS)
    seedVersion.value = STORAGE_VERSION
  }

  if (seedVersion.value !== STORAGE_VERSION) {
    resetSeedData()
  }

  function ensureFloorScopedState() {
    const validIds = new Set(floors.value.map((floor) => floor.id))

    floors.value.forEach((floor) => {
      floor.name = normalizeFloorName(floor.name)
      if (!canvasLayouts.value[floor.id]) canvasLayouts.value[floor.id] = []
      if (!floorAssignments.value[floor.id]) floorAssignments.value[floor.id] = []
    })

    Object.keys(canvasLayouts.value).forEach((key) => {
      if (!validIds.has(key)) delete canvasLayouts.value[key]
    })

    Object.keys(floorAssignments.value).forEach((key) => {
      if (!validIds.has(key)) delete floorAssignments.value[key]
    })
  }

  watch(
    floors,
    () => {
      ensureFloorScopedState()
    },
    { deep: true, immediate: true },
  )

  const employeeMap = computed(() =>
    Object.fromEntries(employees.value.map((item) => [item.id, item])),
  )

  const teamMap = computed(() =>
    Object.fromEntries(teams.value.map((item) => [item.id, item])),
  )

  function nextId() {
    nextIdSeed.value += 1
    return nextIdSeed.value
  }

  function upsertEmployee(payload, editingId = null) {
    const isManager = payload.role === 'manager'
    const value = sanitizeEmployeePayload({
      ...payload,
      id: editingId ?? nextId(),
      prompt:
        isManager
          ? payload.plannerPrompt || payload.prompt || ''
          : payload.prompt || '',
      plannerPrompt: isManager ? payload.plannerPrompt || payload.prompt || '' : '',
      synthesizerPrompt:
        isManager ? payload.synthesizerPrompt || payload.prompt || '' : '',
      tools: payload.role === 'worker' ? payload.tools || [] : [],
      requireApproval: isManager ? payload.requireApproval !== false : undefined,
      activationType: normalizeActivationType(payload.activationType),
      deliverableType: normalizeDeliverableType(payload.deliverableType),
      executionMode: payload.role === 'worker' ? normalizeExecutionMode(payload.executionMode) : 'llm',
      fixedPlan: isManager ? normalizeFixedPlan(payload.fixedPlan) : null,
    })

    if (editingId) {
      const index = employees.value.findIndex((item) => item.id === editingId)
      if (index >= 0) employees.value[index] = value
      return editingId
    }

    employees.value.push(value)
    return value.id
  }

  function deleteEmployee(id) {
    employees.value = employees.value.filter((item) => item.id !== id)
    Object.keys(floorAssignments.value).forEach((floorId) => {
      floorAssignments.value[floorId] = (floorAssignments.value[floorId] || []).filter(
        (item) =>
          !(
            (item.kind === 'employee' || item.kind === 'manager') && item.refId === id
          ) && item.linkedManagerId !== id,
      )
    })
  }

  function cloneEmployee(id) {
    const source = employees.value.find((item) => item.id === id)
    if (!source) return null
    const value = cloneDeep(source)
    value.id = nextId()
    value.name = `${value.name}${TEXT.cloneSuffix}`
    value.locked = false
    value.hidden = false
    value.source = 'local'
    employees.value.push(value)
    return value.id
  }

  function upsertTeam(payload, editingId = null) {
    const value = sanitizeTeamPayload({
      ...payload,
      id: editingId ?? nextId(),
      desc: getTeamDesc(payload.members || [], employees.value, teams.value),
    })

    if (editingId) {
      const index = teams.value.findIndex((item) => item.id === editingId)
      if (index >= 0) teams.value[index] = value
      return editingId
    }

    teams.value.push(value)
    return value.id
  }

  function deleteTeam(id) {
    const team = teams.value.find((item) => item.id === id)
    teams.value = teams.value.filter((item) => item.id !== id)
    if (team?.bundledEmployeeIds?.length) {
      const bundledIds = new Set(team.bundledEmployeeIds)
      employees.value = employees.value.filter((item) => !bundledIds.has(item.id))
    }
    Object.keys(canvasLayouts.value).forEach((floorId) => {
      canvasLayouts.value[floorId] = (canvasLayouts.value[floorId] || []).filter(
        (node) => !(node.kind === 'team' && node.refId === id),
      )
    })
    Object.keys(floorAssignments.value).forEach((floorId) => {
      floorAssignments.value[floorId] = (floorAssignments.value[floorId] || []).filter(
        (item) => !(item.kind === 'team' && item.refId === id) && item.linkedTeamId !== id,
      )
    })
  }

  function cloneTeam(id) {
    const source = teams.value.find((item) => item.id === id)
    if (!source) return null
    const value = cloneDeep(source)

    if (value.bundledEmployeeIds?.length) {
      const employeeIdMap = new Map()
      value.bundledEmployeeIds.forEach((employeeId) => {
        const employee = employees.value.find((item) => item.id === employeeId)
        if (!employee) return
        const clonedEmployeeId = nextId()
        employeeIdMap.set(employeeId, clonedEmployeeId)
        employees.value.push({
          ...cloneDeep(employee),
          id: clonedEmployeeId,
          name: `${employee.name}${TEXT.cloneSuffix}`,
          locked: false,
          hidden: false,
          source: 'local',
        })
      })

      function remapNodes(nodes) {
        return (nodes || []).map((node) => ({
          ...cloneDeep(node),
          refId:
            node.type === 'emp_ref' && employeeIdMap.has(node.refId)
              ? employeeIdMap.get(node.refId)
              : node.refId,
          children: remapNodes(node.children || []),
        }))
      }

      value.members = remapNodes(value.members || [])
      value.bundledEmployeeIds = [...employeeIdMap.values()]
    }

    value.id = nextId()
    value.name = `${value.name}${TEXT.cloneSuffix}`
    value.locked = false
    value.source = 'local'
    value.desc = getTeamDesc(value.members || [], employees.value, teams.value)
    teams.value.push(value)
    return value.id
  }

  function ensurePresetTeam(payload) {
    const existing = teams.value.find((item) => item.name === payload.name)
    if (existing) return existing.id

    const value = sanitizeTeamPayload({
      ...payload,
      id: nextId(),
      members: cloneDeep(payload.members || []),
    })
    value.desc = getTeamDesc(value.members || [], employees.value, teams.value) || payload.desc || ''
    teams.value.push(value)
    return value.id
  }

  function recruitPresetTeamBundle(bundle, options = {}) {
    const teamName = String(bundle?.team?.name || '').trim()
    if (!teamName) return null

    const existing = teams.value.find((item) => item.name === teamName)
    if (existing) return existing.id

    const recruitMembers = options.recruitMembers !== false
    const employeeIdMap = new Map()
    const bundledEmployeeIds = []

    for (const presetEmployee of bundle.employees || []) {
      const newId = nextId()
      employeeIdMap.set(String(presetEmployee.tempId), newId)
      bundledEmployeeIds.push(newId)
      employees.value.push(
        sanitizeEmployeePayload({
          ...cloneDeep(presetEmployee),
          id: newId,
          locked: !recruitMembers,
          hidden: !recruitMembers,
          source: 'market',
        }),
      )
    }

    employees.value = employees.value.map((employee) => {
      if (!bundledEmployeeIds.includes(employee.id) || !employee.fixedPlan?.tasks?.length) return employee
      return sanitizeEmployeePayload({
        ...employee,
        fixedPlan: {
          ...employee.fixedPlan,
          tasks: employee.fixedPlan.tasks.map((task) => ({
            ...task,
            assigneeRefId: employeeIdMap.has(String(task.assigneeRefId))
              ? employeeIdMap.get(String(task.assigneeRefId))
              : task.assigneeRefId,
            assigneeId: employeeIdMap.has(String(task.assigneeId))
              ? employeeIdMap.get(String(task.assigneeId))
              : task.assigneeId,
          })),
        },
      })
    })

    function remapNodes(nodes) {
      return (nodes || []).map((node) => ({
        ...cloneDeep(node),
        refId:
          node.type === 'emp_ref' && employeeIdMap.has(String(node.refId))
            ? employeeIdMap.get(String(node.refId))
            : node.refId,
        children: remapNodes(node.children || []),
      }))
    }

    const teamPayload = sanitizeTeamPayload({
      ...cloneDeep(bundle.team),
      members: remapNodes(bundle.team.members || []),
      locked: !recruitMembers,
      source: 'market',
      bundledEmployeeIds,
    })

    return upsertTeam(teamPayload)
  }

  function addFloor(name = null) {
    let maxIndex = 0
    floors.value.forEach((floor) => {
      const numeric = Number.parseInt(String(floor.id).split('-')[1], 10)
      if (numeric > maxIndex) maxIndex = numeric
    })

    const id = `floor-${maxIndex + 1}`
    floors.value.push({
      id,
      name: normalizeFloorName(name, TEXT.newFloorName),
      scale: 1,
    })
    ensureFloorScopedState()
    return id
  }

  function updateFloorName(id, name) {
    const floor = floors.value.find((item) => item.id === id)
    if (floor) floor.name = normalizeFloorName(name)
  }

  function getFloorDisplayName(id) {
    const index = floors.value.findIndex((item) => item.id === id)
    const floor = floors.value[index]
    if (!floor) return ''
    return `${index + 1}\u5c42 - ${normalizeFloorName(floor.name)}`
  }

  function removeFloor(id) {
    if (floors.value.length <= 1) return
    floors.value = floors.value.filter((item) => item.id !== id)
    delete canvasLayouts.value[id]
    delete floorAssignments.value[id]
    ensureFloorScopedState()
  }

  function setFloorScale(id, scale) {
    const floor = floors.value.find((item) => item.id === id)
    if (floor) floor.scale = scale
  }

  function addCanvasNode(floorId, node) {
    if (!canvasLayouts.value[floorId]) canvasLayouts.value[floorId] = []
    const id = `canvas-${nextId()}`
    canvasLayouts.value[floorId].push({
      id,
      x: node.x ?? 120,
      y: node.y ?? 120,
      width: node.width ?? 300,
      kind: node.kind,
      refId: node.refId,
      name: node.name,
    })
    return id
  }

  function updateCanvasNode(floorId, nodeId, patch) {
    const list = canvasLayouts.value[floorId] || []
    const node = list.find((item) => item.id === nodeId)
    if (node) Object.assign(node, patch)
  }

  function removeCanvasNode(floorId, nodeId) {
    canvasLayouts.value[floorId] = (canvasLayouts.value[floorId] || []).filter(
      (item) => item.id !== nodeId,
    )
  }

  function createPlacement(floorId, payload) {
    if (!floorAssignments.value[floorId]) floorAssignments.value[floorId] = []
    const id = `placement-${nextId()}`
    const placement = {
      id,
      kind: payload.kind || 'employee',
      refId: payload.refId ?? null,
      x: payload.x ?? 0,
      y: payload.y ?? 0,
      linkedTeamId: payload.linkedTeamId ?? null,
      linkedManagerId: payload.linkedManagerId ?? null,
      name: payload.name ?? '',
      icon: payload.icon ?? '',
      role: payload.role ?? 'worker',
    }
    floorAssignments.value[floorId].push(placement)
    return id
  }

  function updateFloorPlacement(floorId, placementId, patch) {
    const placement = (floorAssignments.value[floorId] || []).find(
      (item) => item.id === placementId,
    )
    if (placement) Object.assign(placement, patch)
  }

  function removeFloorPlacement(floorId, placementId) {
    floorAssignments.value[floorId] = (floorAssignments.value[floorId] || []).filter(
      (item) => item.id !== placementId,
    )
  }

  function setFloorAssignments(floorId, placements) {
    floorAssignments.value[floorId] = cloneDeep(placements || [])
  }

  return {
    employees,
    teams,
    floors,
    canvasLayouts,
    floorAssignments,
    employeeMap,
    teamMap,
    resetSeedData,
    upsertEmployee,
    deleteEmployee,
    cloneEmployee,
    upsertTeam,
    deleteTeam,
    cloneTeam,
    ensurePresetTeam,
    recruitPresetTeamBundle,
    addFloor,
    updateFloorName,
    getFloorDisplayName,
    removeFloor,
    setFloorScale,
    addCanvasNode,
    updateCanvasNode,
    removeCanvasNode,
    createPlacement,
    updateFloorPlacement,
    removeFloorPlacement,
    setFloorAssignments,
  }
})
