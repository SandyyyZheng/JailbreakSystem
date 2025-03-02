import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/attacks',
    name: 'attacks',
    component: () => import('../views/AttacksView.vue')
  },
  {
    path: '/prompts',
    name: 'prompts',
    component: () => import('../views/PromptsView.vue')
  },
  {
    path: '/results',
    name: 'results',
    component: () => import('../views/ResultsView.vue')
  },
  {
    path: '/stats',
    name: 'stats',
    component: () => import('../views/StatsView.vue')
  },
  {
    path: '/attack/:id',
    name: 'attack-detail',
    component: () => import('../views/AttackDetailView.vue'),
    props: true
  },
  {
    path: '/execute-attack',
    name: 'execute-attack',
    component: () => import('../views/ExecuteAttackView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  linkActiveClass: 'router-link-active'
})

export default router 