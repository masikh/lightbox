<template>
  <section
    class="section"
    style="max-width: 95%">
    <loading
      :show="waitForBackend"
      label="Waiting for backend to complete"/>

    <h1 class="align-left">Tuya account settings</h1>
    <b-field
      label="Tuya App username"
      label-position="on-border">
      <b-input
        v-model="username"
        required
        placeholder="john@"
        maxlength="40"
        type="email"/>
    </b-field>

    <b-field
      label="Tuya App password"
      label-position="on-border">
      <b-input
        v-model="password"
        password-reveal
        required
        placeholder="secret"
        maxlength="40"
        icon-pack="fas"
        type="password"/>
    </b-field>

    <b-field
      label="Schema"
      label-position="on-border">
      <b-input
        v-model="schema"
        required
        placeholder="tuyaSmart"
        maxlength="40"/>
    </b-field>

    <b-field
      label="Tuya API endpoint"
      label-position="on-border">
      <b-input
        v-model="end_point"
        required
        placeholder="https://openapi.tuyaeu.com"
        maxlength="100"/>
    </b-field>

    <b-field
      label="Access ID"
      label-position="on-border">
      <b-input
        v-model="access_id"
        required
        placeholder="9tkgeefcazqtd99j0k82"
        maxlength="100"/>
    </b-field>

    <b-field
      label="Access Key"
      label-position="on-border">
      <b-input
        v-model="access_key"
        required
        placeholder="g2ad34d04255b6e2a05cccc533487523"
        maxlength="100"/>
    </b-field>

    <b-field
      label="Your country code"
      label-position="on-border">
      <b-numberinput
        v-model="country_code"
        controls-alignment="left"
        controls-position="compact"
        controls-rounded
        icon-pack="fas"
        placeholder="31"/>
    </b-field>

    <b-field
      label="Chromecast device (google assistent)"
      label-position="on-border">
      <b-input
        v-model="chromecast"
        placeholder="192.168.233.19"
        maxlength="40"/>
    </b-field>

    <div class="save-update-buttons">
      <div class="align-left">
        <b-button
          native-type="submit"
          @click="save()">
          Save changes
        </b-button>
      </div>
      <div class="align-left">
        <b-button
          native-type="submit"
          @click="scan">
          (re-)scan devices
        </b-button>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios'
import loading from 'vue-full-loading'

export default {
  components: {
    loading
  },
  data () {
    return {
      waitForBackend: false,
      username: '',
      password: '',
      country_code: '31',
      schema: 'tuyaSmart',
      end_point: 'https://openapi.tuyaeu.com',
      access_id: '',
      access_key: '',
      chromecast: ''
    }
  },
  created () {
    this.init()
  },
  methods: {
    init: function () {
      // Get current tuya credentials
      axios.get('/get_tuya_credentials').then(response => {
        let credentials = response.data.result
        if (credentials !== null) {
          this.password = credentials.password
          this.username = credentials.username
          this.country_code = credentials.country_code
          this.schema = credentials.schema
          this.end_point = credentials.end_point
          this.access_id = credentials.access_id
          this.access_key = credentials.access_key
          this.chromecast = credentials.chromecast
        }
      }, error => {
        console.log(error)
      })
    },
    save: function () {
      let payload = {
        password: this.password,
        username: this.username,
        country_code: this.country_code,
        schema: this.schema,
        end_point: this.end_point,
        access_id: this.access_id,
        access_key: this.access_key,
        chromecast: this.chromecast
      }
      axios.post('/set_tuya_credentials', payload).then(response => {
        this.$buefy.toast.open('Saved changes.')
        this.scan()
      }, error => {
        console.log(error)
      })
    },
    scan: function () {
      this.waitForBackend = true
      this.$buefy.toast.open('Device scan initiated.')
      axios.get('/rescan_tuya_devices').then(response => {
        this.$buefy.toast.open(response.data.result)
        this.waitForBackend = false
      }, error => {
        this.$buefy.toast.open(error)
        console.log(error)
        this.waitForBackend = false
      })
    }
  }
}
</script>
