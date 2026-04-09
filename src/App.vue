<template>
  <div class="flex h-full min-h-0 flex-col bg-slate-50">
    <header class="flex h-14 items-center border-b-2 border-brand-500 bg-slate-950 px-5 text-white">
      <div class="text-sm font-semibold tracking-[0.18em]">BOSS&#27169;&#25311;&#22120;</div>
      <nav class="ml-6 flex items-center gap-2 text-sm">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="rounded-full border border-white/10 px-3 py-1.5 text-slate-300 transition hover:border-white/30 hover:text-white"
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
  { to: '/employees', label: '\u5458\u5de5\u4e0e\u56e2\u961f' },
  { to: '/building', label: '\u5927\u697c\u6620\u5c04' },
]
</script>
