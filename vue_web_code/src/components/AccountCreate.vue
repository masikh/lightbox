<template>
  <section>
    <div class="card container">
      <h1>Create new account</h1>
      <form @submit="createUser">
        <div class="d-flex justify-content-start">
          <b-field
            :type="message ? 'is-danger' : 'is-primary'"
            label="Username"
            label-position="on-border">
            <b-input
              v-model="newUser.username"
              placeholder="Username"
              required/>
          </b-field
          >

          <b-field
            :type="message ? 'is-danger' : 'is-primary'"
            :message="message"
            label="Password"
            label-position="on-border">
            <b-input
              v-model="newUser.password"
              type="password"
              password-reveal
              placeholder="Password"
              required/>
          </b-field>
        </div>
        <div class="div-checkbox">
          <b-checkbox
            v-model="newUser.isAdmin">Admin</b-checkbox>
        </div>

        <div class="create-button">
          <b-button
            @click="$emit('close')">Close</b-button>
          <b-button
            class="button is-primary"
            native-type="submit"><b-icon
              icon="user-plus"
              pack="fas"/>
            <span>Create</span>
          </b-button>
        </div>
      </form>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AccountCreate',
  data () {
    return {
      newUser: {
        username: '',
        password: '',
        isAdmin: false
      },
      message: ''
    }
  },
  methods: {
    createUser: function () {
      let data = {
        username: this.newUser.username,
        password: this.newUser.password,
        admin: this.newUser.isAdmin
      }
      this.message = ''
      this.$http.post('user/add', data)
        .then(response => {
          this.$emit('created')
          this.$router.push('/Accounts')
        })
        .catch(error => {
          this.message = error.data.message || JSON.stringify(error)
        })
    }
  }
}
</script>

<style scoped>
.card {
  max-width: 500px;
  padding: 20px;
  background: rgba(255,255,255,0.7);
}

.div-checkbox {
  display: flex;
  justify-content: flex-start;
  margin-top: 8px;
}

.create-button {
  display: flex;
  justify-content: center;
}

.create-button > * {
  margin: 5px;
}

</style>
