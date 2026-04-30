<template>
  <div class="flex h-full min-h-0 items-center justify-center bg-[radial-gradient(circle_at_top,#dbeafe,transparent_35%),linear-gradient(180deg,#f8fafc_0%,#eef2ff_100%)] p-6">
    <div class="w-full max-w-[420px] rounded-3xl border border-white/70 bg-white/90 p-8 shadow-[0_20px_60px_rgba(15,23,42,0.12)] backdrop-blur">
      <div class="text-xs font-semibold tracking-[0.28em] text-brand-500">BOSS SIMULATOR</div>
      <h1 class="mt-3 text-3xl font-semibold text-slate-900">{{ mode === 'login' ? '登录控制台' : '注册账号' }}</h1>
      <p class="mt-3 text-sm leading-6 text-slate-500">
        账号和业务数据会保存到后端数据库。登录后，员工、团队、楼层、资产和运行记录会按账号隔离同步。
      </p>

      <div class="mt-6 grid grid-cols-2 rounded-2xl bg-slate-100 p-1 text-sm font-semibold">
        <button
          type="button"
          class="rounded-xl px-3 py-2 transition"
          :class="mode === 'login' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'"
          @click="mode = 'login'"
        >
          登录
        </button>
        <button
          type="button"
          class="rounded-xl px-3 py-2 transition"
          :class="mode === 'register' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'"
          @click="mode = 'register'"
        >
          注册
        </button>
      </div>

      <form class="mt-6 space-y-5" @submit.prevent="submit">
        <label class="block">
          <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">账号</div>
          <input
            v-model="form.username"
            autocomplete="username"
            class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-brand-500"
            placeholder="请输入账号"
          />
        </label>

        <label class="block">
          <div class="mb-2 text-xs font-semibold tracking-[0.18em] text-slate-400">密码</div>
          <input
            v-model="form.password"
            type="password"
            :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
            class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-brand-500"
            placeholder="请输入密码"
          />
        </label>

        <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-500">
          后端地址：<span class="font-semibold text-slate-700">{{ apiBaseUrl }}</span>
          <br />
          初始管理员仍可用环境变量配置，首次登录会自动写入数据库。
        </div>

        <div v-if="errorText" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600">
          {{ errorText }}
        </div>

        <button
          class="w-full rounded-2xl bg-brand-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-brand-300"
          type="submit"
          :disabled="submitting"
        >
          {{ submitting ? '处理中...' : mode === 'login' ? '登录进入' : '注册并进入' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getApiBaseUrl } from '../services/api'
import { useAuthStore } from '../stores/auth'

const apiBaseUrl = getApiBaseUrl()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const errorText = ref('')
const submitting = ref(false)
const mode = ref('login')
const form = reactive({
  username: 'admin',
  password: '123456',
})

async function submit() {
  errorText.value = ''
  submitting.value = true
  const result =
    mode.value === 'login'
      ? await authStore.login(form.username, form.password)
      : await authStore.register(form.username, form.password)
  submitting.value = false

  if (!result.ok) {
    errorText.value = result.message
    return
  }

  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
  router.replace(redirect)
}
</script>
