import Vue from 'vue'
import VueRouter from 'vue-router'
import Accounts from '@/components/Accounts'
import AccountCreate from '@/components/AccountCreate'
import Password from '@/components/Password'
import Login from '@/components/Login'
import MoodBuilder from '@/components/MoodBuilder'
import TuyaAccountSettings from '@/components/TuyaAccountSettings'
import LightsGrouping from '@/components/LightsGrouping'

Vue.use(VueRouter)

const routes = [
  { path: '/login', component: Login, name: 'login' },
  { path: '/accounts', component: Accounts },
  { path: '/new_account', component: AccountCreate },
  { path: '/password', component: Password },
  { path: '/moodbuilder', component: MoodBuilder },
  { path: '/lightsgrouping', component: LightsGrouping },
  { path: '/tuya-account-settings', component: TuyaAccountSettings }
]

const router = new VueRouter({
  routes
})

export default router
