<template>
  <v-card class="activity-list" theme="light">
    <v-text-field class="input" v-model="searchQuery" label="Search for Activities" density="compact" outlined
      @input="searchActivities"></v-text-field>
    <v-list class="activity-scrollable">
      <v-progress-circular v-if="loading" indeterminate color="#003F7D" size="20"></v-progress-circular>
      <div v-else v-for="(activity, index) in activities" :key="index" class="activity-item"
        @click="handleActivityClick(activity)">
        <v-icon v-if="activity.activityType.includes('running')" class="mdi-icon">mdi-run</v-icon>
        <v-icon v-else-if="activity.activityType.includes('cycling')" class="mdi-icon">mdi-bike</v-icon>
        <v-icon v-else-if="activity.activityType.includes('swimming')" class="mdi-icon">mdi-swim</v-icon>
        <v-icon v-else-if="activity.activityType.includes('strength')" class="mdi-icon">mdi-dumbbell</v-icon>
        <div class="item-title">{{ activity.activityName }}</div>
        <div style="display:flex; justify-content: center; align-items: center; width: 40%; height: 100%; margin-top: 2px;">{{ activity.startTimeLocal.substring(0, 10) }}</div>
      </div>
    </v-list>
    <v-card v-if="!loading && Object.keys(activities).length === 0"
      style="box-shadow: none; padding: 0px; margin: 0px; height: calc(100% - 150px); width: 80%; margin-left:10%; display: flex; justify-content: center; align-items: center;">
      <p>No activities found. Try searching or scroll to load more!</p>
    </v-card>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Api } from '../../interfaces/api';
import { Activity } from '../../interfaces';

export default defineComponent({
  name: 'ActivityList',
  data() {
    return {
      api: new Api(),
      searchQuery: '',
      activities: {} as Record<string, Activity>, // Simplified activity object
      loading: false,
      startIndex: 0,
      limit: 50,
      activitySelected: false
    };
  },
  props: {
    refetch: {
      type: Object,
      required: true
    }
  },
  methods: {
    async fetchActivities() {
      this.loading = true;
      try {
        const response = await this.api.fetchUserActivities({
          search: this.searchQuery,
          startIndex: this.startIndex,
          limit: this.limit,
        });

        if (response !== -1) {
          const fetchedActivities = response?.data.activities; // Assuming response is structured like { activities: [...] }

          if (this.searchQuery) {
            this.activities = {} as Record<string, Activity>;
          }

          // Loop through fetched activities and add them to the list
          for (const activity of fetchedActivities) {
            const oldActivities = this.activities;

            if (!oldActivities[activity._id]) {
              this.activities[activity._id] = activity;
            }
          }

          if (!this.activitySelected) {
            this.$emit("select-activity", fetchedActivities[0])
            this.activitySelected = true
          }

          if (!this.searchQuery) {
            this.startIndex += this.limit;
          }
        }
      } catch (error) {
        console.error('Error fetching activities:', error);
      } finally {
        this.loading = false;
      }
    },
    async searchActivities() {
      // Reset the state for a fresh search
      this.activities = {} as Record<string, Activity>;
      this.startIndex = 0;
      await this.fetchActivities();
    },
    onScroll(event: Event) {
      const target = event.target as HTMLElement;
      const bottom = target.scrollHeight === target.scrollTop + target.clientHeight;

      if (bottom && !this.loading) {
        this.fetchActivities();
      }
    },
    handleActivityClick(activity: Activity) {
      this.$emit("select-activity", activity); // Emit the selected activity
    },
  },
  mounted() {
    this.fetchActivities(); // Initial fetch when the component is mounted
  },
  watch: {
    async refetch(newVal) {
      this.searchQuery = '';
      this.loading = false;
      this.activities = {} as Record<string, Activity>;
      this.startIndex = 0;
      this.limit = 50;
      await this.fetchActivities();
      if (newVal.id) {
        if (this.activities[newVal.id]) {
          this.$emit("select-activity", this.activities[newVal.id])
        } else {
          this.$emit("select-activity", Object.values(this.activities)[0])
        }
        this.$emit("select-activity", this.activities[newVal.id])
      }
    },
  }
});
</script>

<style scoped>
.activity-list {
  padding-top: 0px;
  height: 100%;
  width: 100%;
  overflow: hidden;
  flex-direction: column;
}

.activity-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.activity-scrollable {
  height: calc(100% - 107px) !important;
  padding: 0px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #fff;
  border: 1px solid #ccc;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.activity-item {
  padding: 8px 16px;
  cursor: pointer;
  background-color: white;
  border-bottom: solid 1px black;
  display: flex;
  align-items: center;
  height: 40px;
}

.item-title {
  font-size: 16pt;
  text-align: center;
  margin-left: 15px;
  margin-right: 5px;
  border-left: solid 1px black;
  border-right: solid 1px black;
  padding-left: 10px;
  padding-right: 5px;
  width: 50%;
  height: 100%;
  white-space: nowrap; /* Prevents text from wrapping */
  overflow: hidden; /* Hides overflow text */
  text-overflow: ellipsis; /* Adds ellipsis to overflowing text */
  margin-top: 10px;
  /* display: flex; */
}

.activity-item:hover {
  background-color: #5B84C4 !important;
  z-index: 10000000000;
}

.activity-item:hover p {
  color: black;
  z-index: 1000000000000000;
}

.input {
  border-bottom: solid 1px white;
  background-color: white;
  margin-bottom: 0px;
}

.input .v-field {
  background-color: white !important;
}
</style>