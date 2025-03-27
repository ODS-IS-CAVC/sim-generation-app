import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from 'vue-router';
import { errorRoutes } from '@/router/error/error';

import MainLayout from '@/components/templates/MainLayout.vue';

const SearchView = () => import('@/views/SearchView.vue');
const scenarioInfoView = () => import('@/views/scenarioInfoView.vue');
const _routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: 'search',
        name: 'search',
        component: SearchView,
      },
    ],
  },

  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: 'scenario',
        name: 'scenario',
        component: scenarioInfoView,
      },
    ],
  },
  ...errorRoutes,
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: _routes,
});

export default router;
