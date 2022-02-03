import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import RegisterLogin from '../views/RegisterLogin.vue';
import Skills from '../views/Skills.vue';
import Recommend from '../views/Recommend.vue';
import Job from '../views/Job.vue';
import EditProfile from '../views/EditProfile.vue';
import Daemon from '../views/Daemon.vue';
import CV from '../views/CV.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'RegisterLogin',
    component: RegisterLogin,
  },
  {
    path: '/skills',
    name: 'Skills',
    component: Skills,
  },
  {
    path: '/recommend',
    name: 'Recommend',
    component: Recommend,
  },
  {
    path: '/job/:id',
    name: 'Job',
    component: Job,
  },
  {
    path: '/editprofile',
    name: 'EditProfile',
    component: EditProfile,
  },
  {
    path: '/daemon',
    name: 'Daemon',
    component: Daemon,
  },
  {
    path: '/cv',
    name: 'CV',
    component: CV,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
