<template>
  <b-navbar class="is-spaced has-shadow">
    <template slot="brand">
      <b-navbar-item
        to="/moodbuilder"
        tag="router-link">
        <img
          alt="Lightweight UI components for Vue.js based on Bulma"
          src="@/assets/ankh.png">
      </b-navbar-item>
    </template>
    <template slot="start">
      <b-navbar-item
        class="is-active"
        tag="router-link"
        to="/moodbuilder">
        Mood Builder
      </b-navbar-item>
    </template>
    <template slot="start">
      <b-navbar-item
        class="is-active"
        tag="router-link"
        to="/lightsgrouping">
        Lights grouping
      </b-navbar-item>
    </template>
    <template slot="start">
      <b-navbar-item
        class="is-active"
        tag="router-link"
        to="/tuya-account-settings">
        Tuya Settings
      </b-navbar-item>
    </template>
    <template slot="end">
      <b-navbar-dropdown
        :label="$store.state.username"
        right>
        <b-navbar-item
          v-if="$store.state.isAdmin"
          tag="router-link"
          to="/accounts">
          Account Manager
        </b-navbar-item>
        <b-navbar-item
          v-if="$store.state.isAdmin"
          tag="router-link"
          to="/new_account">
          New account
        </b-navbar-item>
        <b-navbar-item
          tag="router-link"
          to="/password">
          Change Password
        </b-navbar-item>
        <b-navbar-item @click.native="logout">
          Logout
        </b-navbar-item>
      </b-navbar-dropdown>
    </template>
  </b-navbar>
</template>

<script>
export default {
  name: 'Navigation',
  methods: {
    logout: function () {
      this.$http.get('logout')
      this.$http.defaults.headers.common['Authorization'] = ''
      this.$store.commit('logout')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>

</style>
