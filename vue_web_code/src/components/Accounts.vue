<template>
  <section>
    <div class="card container">
      <h1>Account manager</h1>

      <form>
        <b-table
          :data="accounts"
          class="b-table-transparent">
          <b-table-column
            v-slot="props"
            sortable
            field="name"
            label="User">
            {{ props.row.username }}
          </b-table-column>
          <b-table-column
            v-slot="props"
            sortable
            field="admin"
            label="Administrator">
            <b-icon
              v-if="props.row.admin"
              icon="check"
              type="is-success"
              pack="fas"/>
          </b-table-column>
          <b-table-column
            v-slot="props"
            numeric>
            <b-tooltip
              label="Toggle administrator"
              type="is-danger">
              <b-button
                type="is-primary is-light">
                <b-icon
                  icon="user-edit"
                  pack="fas"
                  @click.native="setAdmin(props.row.username, props.row.admin)"/>
              </b-button>
            </b-tooltip>
            <b-tooltip
              label="Delete User"
              type="is-danger">
              <b-button
                type="is-danger"
                class="delete-button">
                <b-icon
                  icon="trash-alt"
                  pack="fas"
                  @click.native="deleteUser(props.row.username)"/>
              </b-button>
            </b-tooltip>
          </b-table-column>
        </b-table>
      </form>
    </div>
  </section>
</template>

<script>
import AccountCreate from '@/components/AccountCreate'

export default {
  name: 'Accounts',
  components: { AccountCreate },
  data () {
    return {
      showAccountCreateModal: false,
      accounts: [],
      message: ''
    }
  },
  created () {
    this.getUsers()
  },
  methods: {
    getUsers: function () {
      this.$http.get('users/query').then(response => {
        this.accounts = response.data.message
      }).catch(error => {
        this.message = JSON.stringify(error.data.message || error)
      })
    },
    deleteUser: function (username) {
      let data = {
        username: username
      }
      this.message = ''
      this.$http.delete('user/delete', {data: data})
        .then(response => {
          this.getUsers()
        })
        .catch(error => {
          this.message = error.data.message || JSON.stringify(error)
        })
    },
    setAdmin: function (username, admin) {
      let data = {
        username: username,
        admin: !admin
      }
      this.message = ''
      this.$http.post('user/admin', data)
        .then(response => {
          this.getUsers()
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

.iets {
    display: flex;
    justify-content: flex-end;
}

/deep/ table {
  width: 100%;
  text-align: left;
  background-color: transparent!important;
}

.delete-button {
  margin-left: 10px;
}
</style>
