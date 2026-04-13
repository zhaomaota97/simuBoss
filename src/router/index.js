import { createRouter, createWebHistory } from 'vue-router'
import BossView from '../views/BossView.vue'
import RecruitView from '../views/RecruitView.vue'
import TeamStudioPage from '../views/TeamStudioPage.vue'
import BuildingView from '../views/BuildingView.vue'
import AssetLibraryView from '../views/AssetLibraryView.vue'
import MarketView from '../views/MarketView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: BossView },
    { path: '/recruit', redirect: '/market?tab=employee' },
    { path: '/employees', component: RecruitView },
    { path: '/teams', component: TeamStudioPage },
    { path: '/market', component: MarketView },
    { path: '/assets', component: AssetLibraryView },
    { path: '/building', component: BuildingView },
  ],
})
