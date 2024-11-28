import { createRouter, createWebHistory } from 'vue-router';
import Home from '../components/home/Home.vue';
import Login from '../components/Login.vue';
import ActivityPage from '../components/activities/ActivityPage.vue';
import NutritionPage from '../components/nutrition/NutritionPage.vue';
import GarminConnect from '../components/GarminConnect.vue';
import Cookies from 'js-cookie';

const routes = [
  { path: '/', component: Login },
  { path: '/home', component: Home, meta: { requiresAuth: true } },
  { path: '/nutrition', component: NutritionPage, meta: { requiresAuth: true } },
  { path: '/activities', component: ActivityPage, meta: {requiredAuth: true}},
  {
    path: '/:catchAll(.*)',  // This is the catch-all route
    redirect: '/home'  // Redirect to the home page (or '/home')
  }
];

const router = createRouter({
  history: createWebHistory(), 
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!Cookies.get('access_token'); 

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/');
  } else {
    next(); 
  }
});

export default router;
