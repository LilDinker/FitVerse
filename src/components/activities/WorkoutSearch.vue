<template>
  <ConfirmDelete :message="'Are you sure you want to delete this workout? Existing activities associated with this workout will maintain their data until edited.'" v-model="showDialog"
    @confirmed="handleConfirmDelete" @cancelled="handleCancelDelete" />
  <v-card class="search">
    <v-container style="padding: 0px; background-color: #fcb055">
      <div style="display: flex; background-color: #fcb055; align-items: center;">
        <v-text-field style="width: 85%; margin-right: 2%; border: solid 1px black" density="compact"
          v-model="searchQuery" id="menu-activator" label="Search for a Workout Template" @focus="onFocus"
          @input="searchItems" outlined>
        </v-text-field>
        <v-btn theme="dark" class="icon-btn" icon
          style="background-color: #fcb055; border: solid 1px black; margin-right: 5px;" @click="handleEditTemplate">
          <v-tooltip activator="parent" location="top">Edit Workout Template</v-tooltip>
          <v-icon class="icon" style="color: black">mdi-pencil</v-icon>
        </v-btn>
        <v-btn theme="dark" class="icon-btn" icon
          style="background-color: #fcb055; border: solid 1px black; margin-right: 5px;"
          @click="() => { showDialog = true }">
          <v-tooltip activator="parent" location="top">Delete Workout Template</v-tooltip>
          <v-icon class="icon" style="color: black">mdi-delete</v-icon>
        </v-btn>
        <v-btn theme="dark" class="icon-btn" icon
          style="background-color: #fcb055; border: solid 1px black; margin-right: 5px;"
          @click="handleClickList({} as WorkoutTemplate)">
          <v-tooltip activator="parent" location="top">Add New Workout Template</v-tooltip>
          <v-icon class="icon" style="color: black">mdi-plus</v-icon>
        </v-btn>
      </div>

      <!-- v-dialog for displaying the list -->
      <v-menu v-model="isMenuVisible" class="menu">

        <!-- Menu content -->
        <v-list v-if="items.length" class="search-list">
          <div v-for="(item, index) in items" :key="index" @click="handleClickList(item)" class="list-item">
            <v-list-item-title>{{ item.name }}</v-list-item-title>
          </div>
          <v-progress-circular v-if="loading" indeterminate color="#003F7D" size="20">
          </v-progress-circular>
        </v-list>
      </v-menu>
    </v-container>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { WorkoutTemplate } from '../../interfaces';
import { Api } from '../../interfaces/api';
//@ts-ignore
import ConfirmDelete from './ConfirmDelete.vue';

export default defineComponent({
  name: 'WorkoutSearch',
  components: { ConfirmDelete },
  props: {
    existingWorkout: {
      type: Object as () => WorkoutTemplate,
    }
  },
  watch: {
    existingWorkout(newVal: WorkoutTemplate) {
      this.searchQuery = newVal?.name ?? '';
    },
  },
  data() {
    return {
      api: new Api(),
      searchQuery: this.existingWorkout?.name ?? '',
      items: [] as WorkoutTemplate[],
      loading: false,
      isMenuVisible: false, // Menu visibility
      showDialog: false,
    };
  },
  methods: {
    onFocus() {
      this.isMenuVisible = true;
      this.fetchItems();
    },

    async fetchItems() {
      this.loading = true;
      try {
        const response = await this.api.fetchUserTemplates({ search: this.searchQuery, startIndex: 0 });
        //@ts-ignore
        this.items = [...response.data.workout_templates];
      } catch (error) {
        console.error('Error fetching workout templates:', error);
      } finally {
        this.loading = false;
      }
    },

    handleCancelDelete() {
      this.showDialog = false
    },

    handleConfirmDelete() {
      this.$emit("delete-template", this.existingWorkout?._id)
      this.showDialog = false
    },

    handleEditTemplate() {
      this.$emit("edit-workout", this.existingWorkout)
    },

    searchItems() {
      if (this.searchQuery.trim() === '') {
        this.items = []; // Clear the items if search is empty
        return;
      }
      this.fetchItems(); // Fetch items when there's a query
    },

    handleClickList(item: WorkoutTemplate) {
      this.$emit('item-selected', item);
      this.searchQuery = '';
      this.isMenuVisible = false;
    },
  },
});
</script>

<style scoped>
.search {
  box-shadow: none;
  width: 90%;
  margin-left: 5%;
  margin-right: 5%;
  padding: 0px !important;
  position: relative;
}

.search-list {
  max-height: 300px;
  width: calc(30vw - 8px);
  overflow-y: auto;
  overflow-x: hidden !important;
  text-align: center;
  border-radius: 0px !important;
  padding: 0px;
}

.menu {
  margin-left: calc(19% + 5px);
  margin-top: 585px;
  /* width: 100%; */
  overflow-x: none;
  border-radius: 0px !important;
}

.list-item {
  padding: 8px 16px;
  cursor: pointer;
  background-color: white;
  border-bottom: solid 1px black;
  display: flex;
  align-items: center;
  height: 40px;
}


.list-item:hover {
  background-color: #5B84C4 !important;
  z-index: 10000000000;
}

.list-item:hover p {
  color: black;
  z-index: 1000000000000000;
}
</style>
