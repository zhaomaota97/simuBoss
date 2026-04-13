<template>
  <div class="flex h-full min-h-0 flex-col bg-slate-50">
    <header class="flex h-14 items-center border-b-2 border-brand-500 bg-slate-950 px-5 text-white">
      <div class="text-sm font-semibold tracking-[0.18em]">BOSS&#27169;&#25311;&#22120;</div>
      <nav class="ml-6 flex items-center gap-2 text-sm">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="rounded-full border px-3 py-1.5 transition"
          :class="
            item.emphasis
              ? 'border-sky-300/35 bg-gradient-to-r from-sky-400/18 to-cyan-300/18 text-sky-100 shadow-[0_0_0_1px_rgba(125,211,252,0.08),0_8px_24px_rgba(14,165,233,0.12)] hover:border-sky-200/55 hover:from-sky-300/24 hover:to-cyan-200/24 hover:text-white'
              : 'border-white/10 text-slate-300 hover:border-white/30 hover:text-white'
          "
          active-class="border-brand-500 bg-brand-500/20 text-white"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="ml-auto text-xs text-slate-400">Vue 3 + Tailwind + Pinia + DeepSeek</div>
    </header>
    <main class="min-h-0 flex-1">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
const navItems = [
  { to: '/', label: 'Boss \u89c6\u89d2' },
  { to: '/employees', label: '\u5458\u5de5\u4e2d\u5fc3' },
  { to: '/teams', label: '\u56e2\u961f\u4e2d\u5fc3' },
  { to: '/assets', label: '\u8d44\u4ea7\u5e93' },
  { to: '/building', label: '\u5927\u697c\u6620\u5c04' },
  { to: '/market', label: '\u62db\u52df\u5458\u5de5', emphasis: true },
]
</script>
