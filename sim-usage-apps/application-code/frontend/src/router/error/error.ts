import type { RouteRecordRaw } from 'vue-router';

import MainLayout from '@/components/templates/MainLayout.vue';
const SystemErrorView = () => import('@/views/error/SystemError.vue');
const NotFoundView = () => import('@/views/error/NotFound.vue');

export const errorRoutes: RouteRecordRaw[] = [
  {
    path: '/error',
    component: MainLayout,
    children: [
      {
        path: 'system',
        name: 'error/system',
        component: SystemErrorView,
      },
    ],
  },
  {
    path: '/error',
    component: MainLayout,
    children: [
      {
        path: 'not-found',
        name: 'error/not-found',
        component: NotFoundView,
      },
    ],
  },
];
