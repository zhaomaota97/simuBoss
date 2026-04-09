import { createRouter, createWebHistory } from 'vue-router'
import BossView from '../views/BossView.vue'
import EmployeeStudioView from '../views/EmployeeStudioView.vue'
import BuildingView from '../views/BuildingView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: BossView },
    { path: '/employees', component: EmployeeStudioView },
    { path: '/building', component: BuildingView },
  ],
})
