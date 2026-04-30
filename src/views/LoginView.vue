<template>
  <div class="flex h-full min-h-0 items-center justify-center bg-slate-100 px-4 py-8 text-slate-900">
    <div class="w-full max-w-[400px] rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div class="text-xs font-semibold tracking-[0.22em] text-brand-500">SIMUBOSS</div>
      <h1 class="mt-3 text-2xl font-semibold text-slate-950">
        {{ mode === 'login' ? '登录账号' : '创建账号' }}
      </h1>

      <div class="mt-6 grid grid-cols-2 rounded-xl bg-slate-100 p-1 text-sm font-semibold">
        <button
          type="button"
          class="rounded-lg px-3 py-2 transition"
          :class="mode === 'login' ? 'bg-white text-slate-950 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
          @click="switchMode('login')"
        >
          登录
        </button>
        <button
          type="button"
          class="rounded-lg px-3 py-2 transition"
          :class="mode === 'register' ? 'bg-white text-slate-950 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
          @click="switchMode('register')"
        >
          注册
        </button>
      </div>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <label class="block">
          <span class="mb-2 block text-sm font-medium text-slate-700">账号</span>
          <input
            v-model.trim="form.username"
            autocomplete="username"
            class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
            placeholder="请输入账号"
          />
        </label>

        <label class="block">
          <span class="mb-2 block text-sm font-medium text-slate-700">密码</span>
          <input
            v-model="form.password"
            type="password"
            :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
            class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
            placeholder="请输入密码"
          />
        </label>

        <label v-if="mode === 'register'" class="block">
          <span class="mb-2 block text-sm font-medium text-slate-700">确认密码</span>
          <input
            v-model="form.confirmPassword"
            type="password"
            autocomplete="new-password"
            class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
            placeholder="请再次输入密码"
          />
        </label>

        <div v-if="errorText" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {{ errorText }}
        </div>

        <button
          class="w-full rounded-xl bg-brand-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-brand-300"
          type="submit"
          :disabled="submitting"
        >
          {{ submitting ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const errorText = ref('')
const submitting = ref(false)
const mode = ref('login')
const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

function switchMode(nextMode) {
  mode.value = nextMode
  errorText.value = ''
  form.password = ''
  form.confirmPassword = ''
}

function validateForm() {
  if (!form.username) return '请输入账号'
  if (!form.password) return '请输入密码'
  if (mode.value === 'register' && form.password.length < 6) return '密码至少需要 6 位'
  if (mode.value === 'register' && form.password !== form.confirmPassword) return '两次输入的密码不一致'
  return ''
}

async function submit() {
  errorText.value = validateForm()
  if (errorText.value) return

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
