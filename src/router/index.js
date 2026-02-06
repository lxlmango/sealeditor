import { createRouter, createWebHistory } from 'vue-router'
import ActivationView from '../views/ActivationView.vue'
import InstructionsView from '../views/InstructionsView.vue'
import SealAppView from '../views/SealAppView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'activation', component: ActivationView },
    { path: '/instructions', name: 'instructions', component: InstructionsView },
    { path: '/app', name: 'app', component: SealAppView },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

export default router
