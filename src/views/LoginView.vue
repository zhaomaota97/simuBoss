<template>
  <div class="flex h-full min-h-0 items-center justify-center bg-[radial-gradient(circle_at_top,#dbeafe,transparent_35%),linear-gradient(180deg,#f8fafc_0%,#eef2ff_100%)] p-6">
    <div class="w-full max-w-[420px] rounded-3xl border border-white/70 bg-white/90 p-8 shadow-[0_20px_60px_rgba(15,23,42,0.12)] backdrop-blur">
      <div class="text-xs font-semibold tracking-[0.28em] text-brand-500">BOSS SIMULATOR</div>
      <h1 class="mt-3 text-3xl font-semibold text-slate-900">登录控制台</h1>
      <p class="mt-3 text-sm leading-6 text-slate-500">
        现在登录会直接走新的 Python 后端。登录成功后，本机会自动记住会话。
      </p>

      <form class="mt-8 space-y-5" @submit.prevent="submitLogin">
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
            autocomplete="current-password"
            class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-brand-500"
            placeholder="请输入密码"
          />
        </label>

        <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-500">
          测试账号：<span class="font-semibold text-slate-700">admin</span>
          <br />
          测试密码：<span class="font-semibold text-slate-700">123456</span>
          <br />
          后端地址：<span class="font-semibold text-slate-700">{{ apiBaseUrl }}</span>
        </div>

        <div v-if="errorText" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600">
          {{ errorText }}
        </div>

        <button
          class="w-full rounded-2xl bg-brand-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-brand-300"
          type="submit"
          :disabled="submitting"
        >
          {{ submitting ? '登录中...' : '登录进入' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const errorText = ref('')
const submitting = ref(false)
const form = reactive({
  username: 'admin',
  password: '123456',
})

async function submitLogin() {
  errorText.value = ''
  submitting.value = true
  const result = await authStore.login(form.username, form.password)
  submitting.value = false

  if (!result.ok) {
    errorText.value = result.message
    return
  }

  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
  router.replace(redirect)
}
</script>
