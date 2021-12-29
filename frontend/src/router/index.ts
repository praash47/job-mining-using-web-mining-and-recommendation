import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import RegisterLogin from '../views/RegisterLogin.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'RegisterLogin',
    component: RegisterLogin,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
