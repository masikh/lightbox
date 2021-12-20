import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    isLoggedIn: false,
    token: null,
    username: null,
    isAdmin: false
  },
  mutations: {
    initialiseStore (state) {
      if (localStorage.getItem('token')) {
        state.isLoggedIn = true
        state.token = localStorage.getItem('token')
        state.username = localStorage.getItem('username')
        state.isAdmin = localStorage.getItem('is_admin')
      }
    },
    login (state, payload) {
      state.isLoggedIn = true
      state.token = payload.token
      state.username = payload.username
      state.isAdmin = payload.isAdmin
      localStorage.setItem('token', state.token)
      localStorage.setItem('username', state.username)
      localStorage.setItem('is_admin', state.isAdmin)
      console.log('payload:', payload)
    },
    logout (state) {
      state.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('is_admin')
    }
  }
})

export default store
