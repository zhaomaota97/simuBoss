<template>
  <div class="flex h-full min-h-0 gap-5 p-5">
    <section class="panel flex min-h-0 min-w-0 flex-[0.95] flex-col overflow-hidden">
      <div class="panel-header">
        <span>资产库</span>
        <Tabs v-model:model-value="activeTab">
          <TabsList>
            <TabsTrigger value="knowledge">知识库</TabsTrigger>
            <TabsTrigger value="deliverable">交付库</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div class="flex items-center gap-3 border-b border-slate-200 px-4 py-3">
        <input
          v-model="keyword"
          class="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
          placeholder="搜索标题、摘要、标签、路径"
        />
        <button
          class="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white"
          @click="openCreateModal"
        >
          新增资产
        </button>
      </div>

      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div
          v-if="!filteredAssets.length"
          class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-12 text-center text-sm text-slate-400"
        >
          当前分区还没有匹配的资产，先新增一条试试。
        </div>
        <button
          v-for="asset in filteredAssets"
          :key="asset.id"
          class="mb-3 w-full rounded-2xl border bg-white p-4 text-left shadow-sm transition"
          :class="
            selectedAsset?.id === asset.id
              ? 'border-brand-300 ring-2 ring-brand-100'
              : 'border-slate-200 hover:border-brand-300'
          "
          @click="selectedAssetId = asset.id"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <div class="truncate text-sm font-semibold text-slate-900">{{ asset.title }}</div>
                <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">
                  {{ kindLabel(asset.kind) }}
                </span>
              </div>
              <div class="mt-2 text-xs leading-5 text-slate-500">{{ asset.summary }}</div>
              <div class="mt-3 flex flex-wrap gap-2">
                <span
                  v-for="tag in asset.tags || []"
                  :key="tag"
                  class="rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-700"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            <div class="text-right text-[11px] leading-5 text-slate-400">
              <div>{{ formatAssetTime(asset.updatedAt || asset.createdAt) }}</div>
              <div class="mt-1">{{ asset.format }}</div>
            </div>
          </div>
        </button>
      </div>
    </section>

    <aside class="panel flex min-h-0 min-w-0 flex-[1.05] flex-col overflow-hidden">
      <div class="panel-header">
        <span>{{ selectedAsset ? selectedAsset.title : '资产详情' }}</span>
        <div v-if="selectedAsset" class="flex items-center gap-2">
          <button
            class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-brand-300 hover:text-brand-600"
            @click="openEditModal(selectedAsset)"
          >
            编辑
          </button>
          <button
            class="rounded-lg border border-rose-200 px-3 py-1.5 text-xs font-semibold text-rose-600 transition hover:bg-rose-50"
            @click="confirmDeleteAsset(selectedAsset)"
          >
            删除
          </button>
        </div>
      </div>

      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div
          v-if="!selectedAsset"
          class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-12 text-center text-sm text-slate-400"
        >
          左侧选一个资产，这里会显示详情、来源和内容预览。
        </div>
        <template v-else>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="rounded-xl bg-slate-50 p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">摘要</div>
              <div class="mt-2 text-sm leading-6 text-slate-700">{{ selectedAsset.summary }}</div>
            </div>
            <div class="rounded-xl bg-slate-50 p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">路径</div>
              <div class="mt-2 break-all font-mono text-xs leading-6 text-slate-700">{{ selectedAsset.path || '-' }}</div>
            </div>
          </div>

          <div class="mt-4 grid gap-4 md:grid-cols-4">
            <div class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">类型</div>
              <div class="mt-2 text-sm text-slate-700">{{ kindLabel(selectedAsset.kind) }}</div>
            </div>
            <div class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">格式</div>
              <div class="mt-2 text-sm text-slate-700">{{ selectedAsset.format }}</div>
            </div>
            <div class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">来源</div>
              <div class="mt-2 text-sm text-slate-700">
                {{ selectedAsset.sender || selectedAsset.sourceTaskId || '手动入库' }}
              </div>
            </div>
            <div class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">更新时间</div>
              <div class="mt-2 text-sm text-slate-700">{{ formatAssetTime(selectedAsset.updatedAt || selectedAsset.createdAt) }}</div>
            </div>
          </div>

          <div class="mt-4">
            <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">标签</div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in selectedAsset.tags || []"
                :key="tag"
                class="rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-700"
              >
                {{ tag }}
              </span>
              <span v-if="!(selectedAsset.tags || []).length" class="text-sm text-slate-400">
                暂无标签
              </span>
            </div>
          </div>

          <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div class="mb-3 text-sm font-semibold text-slate-700">内容预览</div>
            <pre class="scrollbar-thin max-h-[52vh] overflow-auto whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-700">{{ selectedAsset.content }}</pre>
          </div>
        </template>
      </div>
    </aside>

    <Dialog v-model:open="assetModalOpen">
      <DialogContent class="max-h-[86vh] max-w-3xl p-0">
        <DialogHeader class="border-b border-slate-200 px-5 py-4">
          <DialogTitle>{{ assetModalMode === 'create' ? '新增资产' : '编辑资产' }}</DialogTitle>
          <DialogDescription>支持在知识库和交付库中维护可复用资产。</DialogDescription>
        </DialogHeader>

        <div class="scrollbar-thin max-h-[calc(86vh-132px)] overflow-y-auto p-5">
          <div class="grid gap-4 md:grid-cols-2">
            <label class="block">
              <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">标题</div>
              <input
                v-model="assetForm.title"
                class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              />
            </label>
            <label class="block">
              <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">类型</div>
              <select
                v-model="assetForm.kind"
                class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              >
                <option value="knowledge">知识</option>
                <option value="template">模板</option>
                <option value="deliverable">交付物</option>
              </select>
            </label>
            <label class="block">
              <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">格式</div>
              <input
                v-model="assetForm.format"
                class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                placeholder="markdown / json / csv"
              />
            </label>
            <label class="block">
              <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">路径</div>
              <input
                v-model="assetForm.path"
                class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
                placeholder="assets/knowledge/..."
              />
            </label>
          </div>

          <label class="mt-4 block">
            <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">摘要</div>
            <textarea
              v-model="assetForm.summary"
              rows="3"
              class="w-full rounded-xl border border-slate-200 px-3 py-3 text-sm outline-none focus:border-brand-500"
            />
          </label>

          <label class="mt-4 block">
            <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">标签</div>
            <input
              v-model="assetForm.tagsText"
              class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              placeholder="用逗号分隔，如：模板, 周报, 汇总"
            />
          </label>

          <label class="mt-4 block">
            <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">内容</div>
            <textarea
              v-model="assetForm.content"
              rows="14"
              class="w-full rounded-2xl border border-slate-200 px-4 py-4 text-sm leading-6 outline-none focus:border-brand-500"
            />
          </label>

          <div v-if="assetFormError" class="mt-4 text-sm text-rose-600">{{ assetFormError }}</div>
        </div>

        <div class="flex items-center justify-end gap-3 border-t border-slate-200 px-5 py-4">
          <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="closeAssetModal">
            取消
          </button>
          <button class="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white" @click="submitAssetForm">
            {{ assetModalMode === 'create' ? '创建资产' : '保存修改' }}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog'
import { Tabs, TabsList, TabsTrigger } from '../components/ui/tabs'
import { useAssetLibraryStore } from '../stores/assetLibrary'

const assetStore = useAssetLibraryStore()
const activeTab = ref('knowledge')
const keyword = ref('')
const selectedAssetId = ref('')
const assetModalOpen = ref(false)
const assetModalMode = ref('create')
const assetFormError = ref('')

const assetForm = reactive({
  id: '',
  kind: 'knowledge',
  title: '',
  summary: '',
  format: 'markdown',
  path: '',
  tagsText: '',
  content: '',
})

const activeAssets = computed(() =>
  activeTab.value === 'knowledge' ? assetStore.knowledgeAssets : assetStore.deliverableAssets,
)

const filteredAssets = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  if (!query) return activeAssets.value
  return activeAssets.value.filter((asset) => {
    const haystack = [
      asset.title,
      asset.summary,
      asset.path,
      asset.content,
      ...(asset.tags || []),
    ]
      .join(' ')
      .toLowerCase()
    return haystack.includes(query)
  })
})

const selectedAsset = computed(() =>
  filteredAssets.value.find((item) => item.id === selectedAssetId.value) ||
  activeAssets.value.find((item) => item.id === selectedAssetId.value) ||
  null,
)

watch(
  filteredAssets,
  (value) => {
    if (!value.length) {
      selectedAssetId.value = ''
      return
    }
    if (!value.some((item) => item.id === selectedAssetId.value)) {
      selectedAssetId.value = value[0].id
    }
  },
  { immediate: true },
)

watch(activeTab, () => {
  keyword.value = ''
})

function kindLabel(kind) {
  return {
    knowledge: '知识',
    template: '模板',
    deliverable: '交付物',
  }[kind] || kind
}

function formatAssetTime(value) {
  if (!value) return '未知时间'
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function resetAssetForm() {
  assetForm.id = ''
  assetForm.kind = activeTab.value === 'deliverable' ? 'deliverable' : 'knowledge'
  assetForm.title = ''
  assetForm.summary = ''
  assetForm.format = 'markdown'
  assetForm.path = ''
  assetForm.tagsText = ''
  assetForm.content = ''
  assetFormError.value = ''
}

function openCreateModal() {
  assetModalMode.value = 'create'
  resetAssetForm()
  assetModalOpen.value = true
}

function openEditModal(asset) {
  assetModalMode.value = 'edit'
  assetForm.id = asset.id
  assetForm.kind = asset.kind
  assetForm.title = asset.title
  assetForm.summary = asset.summary
  assetForm.format = asset.format
  assetForm.path = asset.path
  assetForm.tagsText = (asset.tags || []).join(', ')
  assetForm.content = asset.content
  assetFormError.value = ''
  assetModalOpen.value = true
}

function closeAssetModal() {
  assetModalOpen.value = false
  assetFormError.value = ''
}

function submitAssetForm() {
  if (!assetForm.title.trim()) {
    assetFormError.value = '标题不能为空'
    return
  }

  const payload = {
    kind: assetForm.kind,
    title: assetForm.title.trim(),
    summary: assetForm.summary.trim(),
    format: assetForm.format.trim() || 'markdown',
    path: assetForm.path.trim(),
    tags: assetForm.tagsText
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
    content: assetForm.content,
  }

  if (assetModalMode.value === 'create') {
    const asset = assetStore.addAsset(payload)
    selectedAssetId.value = asset.id
  } else {
    const asset = assetStore.updateAsset(assetForm.id, payload)
    if (asset) selectedAssetId.value = asset.id
  }

  closeAssetModal()
}

function confirmDeleteAsset(asset) {
  const ok = window.confirm(`确认删除资产“${asset.title}”吗？`)
  if (!ok) return
  const currentId = asset.id
  assetStore.deleteAsset(currentId)
  if (selectedAssetId.value === currentId) {
    selectedAssetId.value = filteredAssets.value[0]?.id || activeAssets.value[0]?.id || ''
  }
}
</script>
