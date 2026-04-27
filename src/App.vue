<template>
  <div class="flex h-full min-h-0 flex-col bg-slate-50">
    <header
      v-if="showShell"
      class="flex h-14 items-center border-b-2 border-brand-500 bg-slate-950 px-5 text-white"
    >
      <div class="text-sm font-semibold tracking-[0.18em]">BOSS模拟器</div>

      <nav class="ml-6 flex items-center gap-2 text-sm">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="relative inline-flex items-center rounded-full border border-white/10 px-3 py-1.5 text-slate-300 transition hover:border-white/30 hover:text-white"
          active-class="border-brand-500 bg-brand-500/20 text-white"
        >
          {{ item.label }}
          <span
            v-if="item.badge"
            class="pointer-events-none absolute -right-1 -top-1 rounded-full border border-rose-300/30 bg-rose-500 px-1.5 py-0.5 text-[9px] font-bold leading-none tracking-[0.18em] text-white shadow-sm"
          >
            {{ item.badge }}
          </span>
        </RouterLink>
      </nav>

      <button
        type="button"
        class="ml-auto inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-white/30 hover:text-white"
        @click="resetSandbox"
      >
        开发重置
      </button>

      <DropdownMenu v-model:open="accountMenuOpen">
        <DropdownMenuTrigger>
          <button
            class="ml-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition hover:border-white/30 hover:text-white"
          >
            <span
              class="flex h-7 w-7 items-center justify-center rounded-full bg-brand-500/20 text-[11px] font-semibold text-white"
            >
              {{ userInitial }}
            </span>
            <span class="font-semibold text-white">{{ authStore.username || 'admin' }}</span>
            <ChevronDown class="h-4 w-4 text-slate-500" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent class="w-52">
          <div class="rounded-xl px-3 py-2">
            <div class="text-sm font-semibold text-slate-900">{{ authStore.username || 'admin' }}</div>
            <div class="mt-1 text-xs text-slate-400">当前已登录</div>
          </div>
          <div class="my-2 border-t border-slate-100"></div>
          <DropdownMenuItem
            class="text-rose-600 focus:bg-rose-50 focus:text-rose-700"
            @select.prevent="logout"
          >
            {{ loggingOut ? '退出中...' : '退出登录' }}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>

    <main class="min-h-0 flex-1">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ChevronDown } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './components/ui/dropdown-menu'
import { useAssetLibraryStore } from './stores/assetLibrary'
import { useAuthStore } from './stores/auth'
import { useRuntimeStore } from './stores/runtime'
import { useSimuBossStore } from './stores/simuBoss'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const simuBossStore = useSimuBossStore()
const runtimeStore = useRuntimeStore()
const assetLibraryStore = useAssetLibraryStore()

const accountMenuOpen = ref(false)
const loggingOut = ref(false)

const navItems = [
  { to: '/', label: 'Boss视角' },
  { to: '/building', label: '公司大楼' },
  { to: '/employees', label: '员工中心' },
  { to: '/teams', label: '团队中心' },
  { to: '/assets', label: '资产库' },
  { to: '/market', label: '人才市场', badge: 'HOT' },
]

const showShell = computed(() => route.path !== '/login')
const userInitial = computed(() => (authStore.username || 'A').slice(0, 1).toUpperCase())

async function logout() {
  if (loggingOut.value) return
  accountMenuOpen.value = false
  loggingOut.value = true
  await authStore.logout()
  loggingOut.value = false
  router.replace('/login')
}

function resetSandbox() {
  const confirmed = window.confirm(
    '确认还原员工、团队、公司大楼、运行态和资产库到初始状态吗？',
  )
  if (!confirmed) return

  simuBossStore.resetSeedData()
  runtimeStore.clearRuntime()
  assetLibraryStore.resetAssets()
  router.replace('/')
  window.location.reload()
}
</script>
