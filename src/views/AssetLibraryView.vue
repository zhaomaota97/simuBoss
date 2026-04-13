<template>
  <div class="flex h-full min-h-0 gap-5 p-5">
    <section class="panel flex min-h-0 min-w-0 flex-[0.95] flex-col overflow-hidden">
      <div class="panel-header">
        <span>资产库</span>
        <div class="flex items-center gap-2 text-xs">
          <button
            class="rounded-full px-3 py-1.5 font-semibold transition"
            :class="activeTab === 'knowledge' ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-600'"
            @click="activeTab = 'knowledge'"
          >
            知识库
          </button>
          <button
            class="rounded-full px-3 py-1.5 font-semibold transition"
            :class="activeTab === 'deliverable' ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-600'"
            @click="activeTab = 'deliverable'"
          >
            交付库
          </button>
        </div>
      </div>
      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div v-if="!activeAssets.length" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-12 text-center text-sm text-slate-400">
          这个分区还没有资产，先跑几个任务试试。
        </div>
        <button
          v-for="asset in activeAssets"
          :key="asset.id"
          class="mb-3 w-full rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-brand-300"
          @click="selectedAsset = asset"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <div class="truncate text-sm font-semibold text-slate-900">{{ asset.title }}</div>
                <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">
                  {{ asset.kind === 'deliverable' ? '交付物' : asset.kind === 'template' ? '模板' : '知识' }}
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
              <div>{{ formatAssetTime(asset.createdAt) }}</div>
              <div class="mt-1">{{ asset.format }}</div>
            </div>
          </div>
        </button>
      </div>
    </section>

    <aside class="panel flex min-h-0 min-w-0 flex-[1.05] flex-col overflow-hidden">
      <div class="panel-header">
        <span>{{ selectedAsset ? selectedAsset.title : '资产详情' }}</span>
      </div>
      <div class="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-4">
        <div v-if="!selectedAsset" class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-5 py-12 text-center text-sm text-slate-400">
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
              <div class="mt-2 break-all font-mono text-xs leading-6 text-slate-700">{{ selectedAsset.path }}</div>
            </div>
          </div>
          <div class="mt-4 grid gap-4 md:grid-cols-3">
            <div class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">类型</div>
              <div class="mt-2 text-sm text-slate-700">{{ selectedAsset.kind }}</div>
            </div>
            <div class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">格式</div>
              <div class="mt-2 text-sm text-slate-700">{{ selectedAsset.format }}</div>
            </div>
            <div class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="text-xs font-semibold tracking-[0.18em] text-slate-400">来源</div>
              <div class="mt-2 text-sm text-slate-700">{{ selectedAsset.sender || selectedAsset.sourceTaskId || '手动入库' }}</div>
            </div>
          </div>
          <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div class="mb-3 text-sm font-semibold text-slate-700">内容预览</div>
            <pre class="scrollbar-thin max-h-[52vh] overflow-auto whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-700">{{ selectedAsset.content }}</pre>
          </div>
        </template>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useAssetLibraryStore } from '../stores/assetLibrary'

const assetStore = useAssetLibraryStore()
const activeTab = ref('knowledge')
const selectedAsset = ref(null)

const activeAssets = computed(() =>
  activeTab.value === 'knowledge' ? assetStore.knowledgeAssets : assetStore.deliverableAssets,
)

watch(
  activeAssets,
  (value) => {
    if (!value.length) {
      selectedAsset.value = null
      return
    }
    if (!selectedAsset.value || !value.some((item) => item.id === selectedAsset.value.id)) {
      selectedAsset.value = value[0]
    }
  },
  { immediate: true },
)

function formatAssetTime(value) {
  if (!value) return '未知时间'
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
