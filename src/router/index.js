import { createRouter, createWebHistory } from 'vue-router'
import BossView from '../views/BossView.vue'
import RecruitView from '../views/RecruitView.vue'
import TeamStudioPage from '../views/TeamStudioPage.vue'
import BuildingView from '../views/BuildingView.vue'
import AssetLibraryView from '../views/AssetLibraryView.vue'
import MarketView from '../views/MarketView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView, meta: { guestOnly: true } },
    { path: '/', component: BossView, meta: { requiresAuth: true } },
    { path: '/recruit', redirect: '/market?tab=employee' },
    { path: '/employees', component: RecruitView, meta: { requiresAuth: true } },
    { path: '/teams', component: TeamStudioPage, meta: { requiresAuth: true } },
    { path: '/market', component: MarketView, meta: { requiresAuth: true } },
    { path: '/assets', component: AssetLibraryView, meta: { requiresAuth: true } },
    { path: '/building', component: BuildingView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (!authStore.isLoggedIn && authStore.session?.token) {
    await authStore.restoreSession()
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.guestOnly && authStore.isLoggedIn) {
    return '/'
  }

  return true
})

export default router
