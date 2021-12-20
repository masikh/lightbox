<template>
  <div
    class="section"
    style="max-width: 95%">
    <div class="align-left margin_bottom">
      <b-button
        @click="add_light_group">
        Add new light group
      </b-button>
    </div>
    <div>
      <drag-drop
        :dropzones="light_groups"
        :dropzones-title="'Light groups'"
        :original-data="device_names"
        :original-title="'Unassigned light bulbs'"
        :in-place="true"
        :enable-save="true"
        :enable-cancel="false"
        :key="refresh_light_groups"
        class="align-left"
        @save="save">
        {{ device_names }}
      </drag-drop>
    </div>
  </div>
</template>

<script>
import loading from 'vue-full-loading'
import DragDrop from 'vue-drag-n-drop'

export default {
  components: {
    loading,
    DragDrop
  },
  data () {
    return {
      devices: [],
      device_names: [],
      selected_devices: [],
      selected_light_group_name: '',
      refresh_light_groups: 0,
      new_light_group_added: false,
      light_groups: []
    }
  },
  watch: {
    light_groups: {
      handler: function () {
        if (this.new_light_group_added === true) {
          this.new_light_group_added = false
        } else {
          for (let i = this.light_groups.length - 1; i >= 0; i--) {
            if (this.light_groups[i].children.length === 0) {
              this.light_groups.splice(i, 1)
              this.refresh_light_groups += 1
            }
          }
        }
      },
      deep: true
    }
  },
  created () {
    this.init()
  },
  methods: {
    init: function () {
      this.getDevices()
    },

    getDevices: function () {
      this.waitForBackend = true
      this.$http.get('/get_light_groups')
        .then(response => {
          if (response.data.error) {
            console.log(response.data.error)
          } else {
            this.light_groups = response.data.result.light_groups
            this.device_names = response.data.result.unassigned_lights
            this.refresh_light_groups += 1
          }
        })
    },

    save: function () {
      this.$http.post('/set_light_groups', {'light_groups': this.light_groups})
        .then(response => {
          if (response.data.error) {
            console.log(response.data.error)
          }
        })
      console.log(this.light_groups)
    },

    add_light_group: function () {
      this.$buefy.dialog.prompt({
        title: 'Add new light group',
        message: 'Enter name for new light group',
        inputAttrs: {
          type: 'text',
          maxlength: 50,
          value: this.selected_light_group_name
        },
        confirmText: 'Add',
        cancelText: 'Abort',
        trapFocus: true,
        closeOnConfirm: false,
        onConfirm: (value, {close}) => {
          if (value !== '') {
            this.light_groups.push({'name': value, 'children': []})
            this.selected_light_group_name = value
            this.new_light_group_added = true
            this.refresh_light_groups += 1
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

.dd-result-group {
  overflow-x: auto;
  white-space: nowrap;
  overflow-y: scroll;
  max-height: 200px;
  max-width: 880px;
}

</style>
