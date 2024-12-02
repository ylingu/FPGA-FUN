import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/apps',
      name: 'apps',
      component: () => import('../views/AppsView.vue'),
      children: [
        {
          path: 'number',
          name: 'number',
          component: () => import('../components/NumberCanvas.vue'),
        },
      ],
    },
  ],
})

export default router
