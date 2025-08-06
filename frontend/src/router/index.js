import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/lobby/:sessionCode',
      name: 'lobby',
      component: () => import('../views/LobbyView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/host',
      name: 'host',
      component: () => import('../views/HostPanelView.vue')
    },
    {
      path: '/game/:sessionCode',
      name: 'game',
      component: () => import('../views/GameView.vue')
    }
  ]
})

export default router