import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../services/api'

import Home from '../views/Home.vue'
import TreeView from '../views/TreeView.vue'
import Directory from '../views/Directory.vue'
import PersonProfile from '../views/PersonProfile.vue'
import Login from '../views/Login.vue'
import NotFound from '../views/NotFound.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminPeople from '../views/admin/AdminPeople.vue'
import AdminPersonEdit from '../views/admin/AdminPersonEdit.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/tree', name: 'Tree', component: TreeView, meta: { hideFooter: true } },
  { path: '/people', name: 'Directory', component: Directory },
  { path: '/person/:id', name: 'Person', component: PersonProfile },
  { path: '/login', name: 'Login', component: Login, meta: { bare: true } },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { bare: true, requiresAuth: true },
    children: [
      { path: '', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'people', name: 'AdminPeople', component: AdminPeople },
      { path: 'people/:id', name: 'AdminPersonEdit', component: AdminPersonEdit },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    if (to.name === 'Person' || to.name === 'Tree') return { top: 0 }
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && isAuthenticated()) {
    next({ name: 'AdminDashboard' })
  } else {
    next()
  }
})

export default router
