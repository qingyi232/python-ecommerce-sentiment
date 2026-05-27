import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '数据总览' } },
      { path: 'products', name: 'Products', component: () => import('@/views/Products.vue'), meta: { title: '商品管理' } },
      { path: 'reviews', name: 'Reviews', component: () => import('@/views/Reviews.vue'), meta: { title: '评论管理' } },
      { path: 'sentiment', name: 'Sentiment', component: () => import('@/views/Sentiment.vue'), meta: { title: '情感分析' } },
      { path: 'demand', name: 'Demand', component: () => import('@/views/Demand.vue'), meta: { title: '需求挖掘' } },
      { path: 'crawl', name: 'Crawl', component: () => import('@/views/Crawl.vue'), meta: { title: '数据采集' } },
      { path: 'visualization', name: 'Visualization', component: () => import('@/views/Visualization.vue'), meta: { title: '可视化展示' } },
      { path: 'users', name: 'Users', component: () => import('@/views/Users.vue'), meta: { title: '用户管理' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
