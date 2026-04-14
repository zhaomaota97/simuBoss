import { computed } from 'vue'
import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'

const DEFAULT_ASSETS = [
  {
    id: 'tpl-weekly-report',
    kind: 'template',
    title: '周报模板',
    summary: '适合经理汇总团队周进展、风险和下周计划。',
    format: 'markdown',
    path: 'assets/knowledge/templates/weekly-report.md',
    tags: ['模板', '周报', '汇总'],
    content: '# 本周进展\n\n## 已完成\n- \n\n## 风险\n- \n\n## 下周计划\n- ',
    createdAt: '2026-04-13T00:00:00.000Z',
    updatedAt: '2026-04-13T00:00:00.000Z',
  },
  {
    id: 'kb-approval-rules',
    kind: 'knowledge',
    title: '审批计划编写规则',
    summary: '约束经理拆解时必须清楚写出目标理解、最终交付、子任务、负责人和依赖。',
    format: 'markdown',
    path: 'assets/knowledge/references/approval-rules.md',
    tags: ['知识', '审批', '计划'],
    content:
      '1. 明确目标理解\n2. 明确最终交付\n3. 子任务可执行\n4. 负责人必须合法\n5. 依赖关系可验证',
    createdAt: '2026-04-13T00:00:00.000Z',
    updatedAt: '2026-04-13T00:00:00.000Z',
  },
]

function slugify(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/gi, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 48) || 'asset'
}

function summarize(text, max = 96) {
  const normalized = String(text || '').replace(/\s+/g, ' ').trim()
  if (normalized.length <= max) return normalized
  return `${normalized.slice(0, max)}...`
}

function normalizeAsset(payload = {}) {
  const now = new Date().toISOString()
  return {
    id: payload.id || crypto.randomUUID(),
    kind: payload.kind || 'knowledge',
    title: String(payload.title || '').trim() || '未命名资产',
    summary: String(payload.summary || '').trim(),
    format: String(payload.format || 'markdown').trim() || 'markdown',
    path: String(payload.path || '').trim(),
    tags: Array.isArray(payload.tags)
      ? payload.tags.map((item) => String(item || '').trim()).filter(Boolean)
      : [],
    content: String(payload.content || ''),
    sourceTaskId: String(payload.sourceTaskId || ''),
    sourcePlanId: String(payload.sourcePlanId || ''),
    sender: String(payload.sender || ''),
    createdAt: payload.createdAt || now,
    updatedAt: payload.updatedAt || now,
  }
}

export const useAssetLibraryStore = defineStore('assetLibrary', () => {
  const assets = useStorage('sb_assets', DEFAULT_ASSETS)

  const sortedAssets = computed(() =>
    [...assets.value].sort(
      (a, b) =>
        new Date(b.updatedAt || b.createdAt || 0).getTime() -
        new Date(a.updatedAt || a.createdAt || 0).getTime(),
    ),
  )

  const knowledgeAssets = computed(() =>
    sortedAssets.value.filter((item) => item.kind === 'knowledge' || item.kind === 'template'),
  )
  const deliverableAssets = computed(() =>
    sortedAssets.value.filter((item) => item.kind === 'deliverable'),
  )

  function addAsset(payload) {
    const asset = normalizeAsset(payload)
    if (!asset.summary) asset.summary = summarize(asset.content || asset.title)
    assets.value.unshift(asset)
    return asset
  }

  function updateAsset(id, patch) {
    const index = assets.value.findIndex((item) => item.id === id)
    if (index === -1) return null
    const previous = assets.value[index]
    const next = normalizeAsset({
      ...previous,
      ...patch,
      id: previous.id,
      createdAt: previous.createdAt,
      updatedAt: new Date().toISOString(),
    })
    if (!next.summary) next.summary = summarize(next.content || next.title)
    assets.value[index] = next
    return next
  }

  function deleteAsset(id) {
    const index = assets.value.findIndex((item) => item.id === id)
    if (index === -1) return false
    assets.value.splice(index, 1)
    return true
  }

  function getAssetById(id) {
    return assets.value.find((item) => item.id === id) || null
  }

  function registerDeliverable({
    title,
    result,
    sender,
    sourceTaskId = '',
    sourcePlanId = '',
    format = 'markdown',
  }) {
    const createdAt = new Date().toISOString()
    const dateChunk = createdAt.slice(0, 10)
    const filename = `${slugify(title)}-${slugify(sender)}.${
      format === 'json' ? 'json' : format === 'csv' ? 'csv' : 'md'
    }`

    return addAsset({
      kind: 'deliverable',
      title: title || '未命名交付物',
      summary: summarize(result),
      format,
      path: `assets/deliverables/${dateChunk}/${filename}`,
      tags: ['交付物', sender].filter(Boolean),
      content: String(result || ''),
      sourceTaskId,
      sourcePlanId,
      sender,
      createdAt,
      updatedAt: createdAt,
    })
  }

  return {
    assets,
    sortedAssets,
    knowledgeAssets,
    deliverableAssets,
    addAsset,
    updateAsset,
    deleteAsset,
    getAssetById,
    registerDeliverable,
  }
})
