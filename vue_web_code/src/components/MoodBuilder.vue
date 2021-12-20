<template>
  <div
    class="section"
    style="max-width: 95%">
    <div id="resp-table">
      <loading
        :show="waitForBackend"
        label="Waiting for backend to complete"/>

      <div id="resp-table-body">
        <div class="resp-table-row">
          <div class="table-body-cell">
            <h1 class="align-left">Mood Builder</h1>
          </div>
        </div>

        <div class="resp-table-row">
          <div class="table-body-cell">

            <div class="align-left margin_bottom">
              <b-dropdown
                :key="update_moods"
                v-model="mood_name"
                append-to-body
                aria-role="menu"
                scrollable
                max-height="200"
                class="align-left"
                trap-focus>
                <template #trigger>
                  <a
                    class="navbar-item"
                    role="button">
                    <span>Current selected moods: {{ mood_name }}</span>
                    <b-icon
                      class="middle"
                      pack="fas"
                      icon="chevron-down"
                      size="is-small"/>
                  </a>
                </template>

                <b-dropdown-item
                  custom
                  aria-role="listitem">
                  <b-button
                    @click="showAddMood">
                    Add new mood
                  </b-button>
                </b-dropdown-item>

                <b-dropdown-item
                  v-for="item of moods"
                  :key="item.name"
                  :value="item.name"
                  aria-role="listitem">
                  {{ item.name }}
                </b-dropdown-item>
              </b-dropdown>
              <hr>
            </div>

            <div style="width: 100%; display: table;">
              <div style="display: table-row">
                <div style="width: 150px; display: table-cell;">
                  <color-picker
                    v-model="colour"
                    :start-color="startColour"
                    :disabled="colorWheel===false"
                    width="150"
                    height="150"
                    @color-change="setColor(true)"/>
                </div>
                <div
                  v-if="bulb_icon !== null"
                  style="display: table-cell;">
                  <img
                    :src="bulb_icon"
                    height="150px"
                    width="150px"
                    alt="">
                </div>
                <div
                  v-else
                  style="width: 300px; display: table-cell;">
                  <img
                    src="@/assets/1px-transparent.png"
                    alt="">
                </div>
              </div>
            </div>

            <div class="align-left">
              <span class="margin_left">Color mode</span>
              <hr>
              <span class="margin_left">White mode</span>
            </div>

            <b-field label="brightness (%)">
              <b-slider
                v-model="brightness"
                :value="80"
                type="is-info"
                @change="setColor(false)"/>
            </b-field>

            <b-field label="colour temperature (%)">
              <b-slider
                v-model="colourtemp"
                :value="20"
                type="is-warning"
                @change="setColor(false)"/>
            </b-field>

            <b-field label="Color rotation speed (0 sec = off)">
              <b-slider
                v-model="colour_rotation_speed"
                :min="0"
                :max="300"
                type="is-primary"
                @change="colourRotationSpeed()"/>
            </b-field>

          </div>

          <div class="table-body-cell">
            <b-select
              v-model="selected_device_ids"
              multiple
              expanded
              native-size="14">
              <optgroup label="White bulbs">
                <option
                  v-for="(device, key) in devices"
                  v-if="device.colour===false"
                  :value="key"
                  :key="key">
                  {{ device.name }}
                </option>
              </optgroup>
              <optgroup label="Colour bulbs">
                <option
                  v-for="(device, key) in devices"
                  v-if="device.colour===true"
                  :value="key"
                  :key="key">
                  {{ device.name }}
                </option>
              </optgroup>
            </b-select>
          </div>
        </div>

        <div class="resp-table-row">
          <div class="table-body-cell">
            <div class="align-left">
              <b-button
                native-type="submit"
                @click="saveMood">
                Save changes
              </b-button>
              <b-button
                class="margin_left"
                native-type="submit"
                type="is-danger"
                @click="deleteMood">
                Delete selected mood
              </b-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ColorPicker from 'vue-color-picker-wheel'
import loading from 'vue-full-loading'

export default {
  components: {
    ColorPicker,
    loading
  },
  data () {
    return {
      bulb_icon: null,
      update_moods: 0,
      waitForBackend: false,
      colour: '#c24141',
      startColour: '#c24141',
      devices: [],
      selected_device_ids: [],
      colorWheel: true,
      brightness: 80,
      colourtemp: 20,
      moods: [],
      mood_name: '',
      default_mood: null,
      selected_mood: null,
      colour_rotation_speed: 60
    }
  },
  watch: {
    selected_device_ids: function () {
      // Set bulb icon (if multiple devices are selected use the first in line)
      this.bulb_icon = this.devices[this.selected_device_ids[0]].icon

      // Set current color in color-wheel for selected device (if and only if 1 device is selected)
      if (this.selected_device_ids.length === 1) {
        this.colour = this.selected_mood.profile[this.selected_device_ids[0]].colour
        this.brightness = this.selected_mood.profile[this.selected_device_ids[0]].brightness
        this.colourtemp = this.selected_mood.profile[this.selected_device_ids[0]].colourtemp
      }

      // Set color-wheel on or off depending on device capability
      this.colorWheel = true
      for (let i = 0; i < this.selected_device_ids.length; i++) {
        this.colorWheel = this.devices[this.selected_device_ids[i]].colour === true
        if (this.colorWheel === false) { return }
      }
    },

    mood_name: function () {
      this.activateMood()
    },

    colour: function () {
      for (let i = 0; i < this.selected_device_ids.length; i++) {
        this.selected_mood.profile[this.selected_device_ids[i]].colour = this.colour
      }
    },

    brightness: function () {
      for (let i = 0; i < this.selected_device_ids.length; i++) {
        this.selected_mood.profile[this.selected_device_ids[i]].brightness = this.brightness
      }
    },

    colourtemp: function () {
      for (let i = 0; i < this.selected_device_ids.length; i++) {
        this.selected_mood.profile[this.selected_device_ids[i]].colourtemp = this.colourtemp
      }
    }
  },

  created () {
    this.init()
  },

  methods: {
    init: function () {
      this.getDevices()
      this.getMoods()
    },

    getDevices: function () {
      this.$http.get('/get_tuya_devices')
        .then(response => {
          if (response.data.error) {
            this.errorMessage = response.data.error
          } else {
            this.devices = response.data.result
          }
        })
        .catch(error => {
          this.errorMessage = error.data.message
        })
    },

    getMoods: function () {
      this.$http.get('/tuya_get_moods')
        .then(response => {
          if (response.data.result.length === 0) {
            this.moods = [{'name': 'Sunny day.', 'profile': {}}]
            this.mood_name = this.moods[0].name
          } else {
            this.moods = response.data.result
            this.getDefaultMood()
          }
        })
        .catch(error => {
          console.log(error)
        })
    },

    getDefaultMood: function () {
      this.$http.get('/tuya_get_default_mood')
        .then(response => {
          if (response.data.result !== null) {
            this.mood_name = response.data.result
          } else {
            this.mood_name = this.moods[0].name
          }
        })
        .catch(error => {
          console.log(error)
          this.mood_name = this.moods[0].name
        })
    },

    activateMood: function () {
      if (this.mood_name !== '') {
        for (let i = 0; i < this.moods.length; i++) {
          if (this.moods[i].name === this.mood_name) {
            this.selected_mood = this.moods[i]
            this.colour_rotation_speed = this.moods[i].colour_rotation_speed

            // Send activateMood request to backend
            this.waitForBackend = true
            this.$http.post('/tuya_activate_mood', {'name': this.mood_name})
              .then(response => {
                this.waitForBackend = false
              })
              .catch(error => {
                console.log(error)
                this.waitForBackend = false
              })
          }
        }
      }
    },

    setColor: function (setColour) {
      let params = {
        colour: this.colour,
        brightness: this.brightness,
        colourtemp: this.colourtemp,
        set_colour: setColour
      }

      for (let i = 0; i < this.selected_device_ids.length; i++) {
        this.devices[this.selected_device_ids[i]].last_setting = params
        this.selected_mood.profile[this.selected_device_ids[i]] = params
      }

      params['identifiers'] = this.selected_device_ids
      this.$http.post('/tuya_set_color', params)
        .then(response => {
          // console.log(response.data)
        })
        .catch(error => {
          console.log(error)
        })
    },

    colourRotationSpeed: function () {
      let params = {mood: this.selected_mood.name, colour_rotation_speed: this.colour_rotation_speed}
      this.$http.post('/tuya_colour_rotation_speed', params)
        .then(response => {
          // console.log(response.data.result
        })
        .catch(error => {
          console.log(error)
        })
    },

    saveMood: function () {
      this.selected_mood.colour_rotation_speed = this.colour_rotation_speed
      this.$http.post('/tuya_save_mood', {'mood': this.selected_mood})
        .then(response => {
          console.log(response.data.result)
        })
        .catch(error => {
          console.log(error)
        })
    },

    deleteMood: function () {
      this.$buefy.dialog.confirm({
        title: 'Remove mood profile',
        message: this.mood_name,
        confirmText: 'Delete mood',
        cancelText: 'Cancel',
        type: 'is-danger',
        hasIcon: true,
        onConfirm: () => {
          this.$http.post('/tuya_delete_mood', {'name': this.mood_name})
            .then(response => {
              this.init()
              this.update_moods += 1
              this.$buefy.toast.open('Mood profile removed.')
            })
            .catch(error => {
              console.log(error)
            })
        }
      })
    },

    showAddMood: function () {
      this.$buefy.dialog.prompt({
        title: 'Add new mood',
        message: 'Enter name for new mood',
        inputAttrs: {
          type: 'text',
          maxlength: 50,
          value: this.mood_name
        },
        confirmText: 'Add',
        cancelText: 'Abort',
        trapFocus: true,
        closeOnConfirm: false,
        onConfirm: (value, {close}) => {
          if (value !== '') {
            let data = {name: value, profile: this.selected_mood.profile}
            this.moods.push(data)
            this.mood_name = value
            this.saveMood()
            this.update_moods += 1
          }
          close()
        }
      })
    }
  }
}
</script>

<style>
section {
  margin: 25px;
}
hr {
  position: relative;
  border: none;
  height: 3px;
  background: black;
  margin: 2px;
}

.modal .animation-content {
    background-color: #f5f5f5;
}

.margin_bottom {
  margin-bottom: 25px;
}

.margin_left {
  margin-left: 10px;
}

.middle {
  margin-top: 5px;
  margin-left: 5px;
}

#resp-table {
  width: 100%;
  display: table;
}

#resp-table-body{
  display: table-row-group;
}

.resp-table-row{
  display: table-row;
}

.table-body-cell{
  display: table-cell;
  padding: 10px;
}

</style>
