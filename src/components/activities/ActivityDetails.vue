<template>
    <ConfirmDelete :message="'Are you sure you want to delete this activity?'" v-model="showDialog"
        @confirmed="handleConfirmDeleteActivity" @cancelled="handleCancelDeleteActivity" />
    <AddActivity ref="addActivity" @update-activities="updateData" :original-activity="editingActivity"
        @cancel-edit="() => { editingActivity = {} as Activity }" />
    <!-- Header Section -->
    <v-card-title
        style="background-color: #FF5003; position: relative; color: white; height: 51px; padding: 0px; padding-left: 10px; display: flex; align-items: center;">
        <div>Activity Details</div>
        <v-spacer />
        <v-btn @click="editActivity" icon small class="icon-btn"
            style="margin-right: 10px; background-color: #FF5003; color: white; border-color: white">
            <v-tooltip activator="parent" location="top">Edit Activity</v-tooltip>
            <v-icon class="icon">mdi-pencil</v-icon>
        </v-btn>
        <v-btn @click="showConfirmPopup" icon small class="icon-btn"
            style="margin-right: 10px; background-color: #FF5003; color: white; border-color: white">
            <v-tooltip activator="parent" location="top">Delete Activity</v-tooltip>
            <v-icon class="icon">mdi-delete</v-icon>
        </v-btn>
        <v-btn icon small class="icon-btn"
            style="margin-right: 10px; background-color: #FF5003; color: white; border-color: white"
            @click="openDialog()">
            <v-tooltip activator="parent" location="top">Manual
                Activity Entry</v-tooltip>
            <v-icon class="icon">mdi-plus</v-icon>
        </v-btn>
    </v-card-title>
    <v-card
        style="box-shadow: none; background-color: #fcb055; padding: 0px; margin: 0px; width: 100%; height: 100%; max-height: calc(100vh - 133px); overflow: hidden; border-radius: 0px;"
        v-if="activity && activity._id != undefined && !loading">
        <v-card-title style="display: flex; align-items: center; border-bottom: solid 1px black">
            <div style="display: flex; align-items: center; width: 100%; background-color: #fcb055">
                <v-icon v-if="activity && activity.activityType.includes('running')" class="mdi-icon">mdi-run</v-icon>
                <v-icon v-else-if="activity && activity.activityType.includes('cycling')" class="mdi-icon">mdi-bike</v-icon>
                <v-icon v-else-if="activity && activity.activityType.includes('swimming')" class="mdi-icon">mdi-swim</v-icon>
                <v-icon v-else-if="activity && activity.activityType.includes('strength')" class="mdi-icon">mdi-dumbbell</v-icon>
                <span class="activity-title">{{ activity.activityName }}</span>
                <v-spacer />
                <span style="opacity: 0.5">{{ formattedDate }}</span>
            </div>
        </v-card-title>
        <v-row style="height: calc(24%); padding-bottom: 5px; max-height: 300px">
            <v-col v-if="activity && !activity.activityType.includes('strength')" cols="6"
                style="height: 100%; display: flex; align-items: center;">
                <ActivityCard :activity="activity" :noTitle="true"></ActivityCard>
            </v-col>
            <v-col v-else cols="12" style="height: 100%; max-height: 300px; display: flex; align-items: center;">
                <StrengthOverview :activity="activity"></StrengthOverview>
            </v-col>
            <v-col v-if="activity && !activity.activityType.includes('strength') && !activity.manualActivity" style="height: 100%">
                <SplitsChart :activityId="activity.activityId"></SplitsChart>
            </v-col>
            <v-col v-if="activity && activity.manualActivity">
                <v-card style="background-color: #fcb055; box-shadow: none; border: none; padding: 0px; margin:0px;
                width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">No Additional
                    Data</v-card>
            </v-col>
        </v-row>
        <v-row
            v-if="activity && activityDetails != undefined && !activity.activityType.includes('strength') && !activity.manualActivity"
            style="max-height: calc(85% - 116px); overflow: hidden;">
            <v-col style="padding: 0px;">
                <v-card
                    style="max-height: calc(67vh - 10px); width: calc(100% - 20px); margin-left: 10px; margin-top: 10px; box-shadow: none; background-color: #fcb055; border-top: solid 1px black;">
                    <v-card-title style="border-bottom: solid 1px black">Advanced Metrics</v-card-title>
                    <!-- Make this div scrollable -->
                    <div
                        style="max-height: calc(67vh - 100px); width: calc(100% - 12px); overflow-y: auto; padding-right: 10px;">
                        <MetricChart v-for="metric in activityDetails.metrics" :key="metric.key"
                            :time="activityDetails.activityTime" :metric="metric" />
                    </div>
                </v-card>
            </v-col>
        </v-row>
        <v-row v-else-if="activity && activity.activityType.includes('strength')" style="position: relative">
            <v-col style="padding: 0px;">
                <v-card
                    style="position: relative; z-index: 0; max-height: calc(67vh - 10px); width: calc(100% - 20px); margin-left: 10px; margin-top: 10px; box-shadow: none; background-color: #fcb055; border-top: solid 1px black;">
                    <v-card-title>Workout Template</v-card-title>
                    <WorkoutSearch style="position: relative" @edit-workout="handleEditWorkout"
                        @item-selected="handleWorkoutSelected" :existingWorkout="selectedWorkout">
                    </WorkoutSearch>
                    <WorkoutEntry
                        v-if="selectedWorkout.name != undefined && (selectedEditedWorkout == undefined || selectedEditedWorkout.name == undefined)"
                        :workoutTemplate="selectedWorkout" :workoutData="activity?.workoutData"
                        @workout-entered="handleWorkoutEntered"></WorkoutEntry>
                    <NewTemplate v-else :selected-workout="selectedEditedWorkout" @cancel-edit="handleCancel"
                        @update-data="handleUpdate"></NewTemplate>
                </v-card>
            </v-col>
        </v-row>
        <v-row v-else-if="activity && activity.manualActivity" style="height: calc(85% - 116px); width: 100%; margin-left: 0px">
            <v-card style="background-color: #fcb055; box-shadow: none; border: none; padding: 0px; margin:0px;
                width: 100%; height: 70%; display: flex; align-items: center; justify-content: center;">
                <div style="width: 50%">This is a
                    manually entered activity, so we have no additional data insights at this time. Link your Garmin
                    Account
                    to get more out of FitVerse!</div>
            </v-card>
        </v-row>
    </v-card>
    <v-card v-else
        style="box-shadow: none; background-color: #fcb055; padding: 0px; margin: 0px; width: 100%; height: 100%; max-height: calc(100vh - 133px); overflow: hidden; border-radius: 0px; display: flex; justify-content: center; align-items: center;">
        <v-progress-circular indeterminate color="#003F7D" size="20"></v-progress-circular></v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import ExerciseSearch from './ExerciseSearch.vue';
import WorkoutTemplateTable from './ExerciseTable.vue';
import { Activity, ActivityDetailsData, WorkoutTemplate } from '../../interfaces';
//@ts-ignore
import SplitsChart from './SplitsChart.vue';
import ActivityCard from './ActivityCard.vue';
import dayjs from 'dayjs';
import MetricChart from './MetricChart.vue';
import NewTemplate from './NewTemplate.vue';
import WorkoutSearch from './WorkoutSearch.vue';
import WorkoutEntry from './WorkoutEntry.vue';
import StrengthOverview from './StrengthOverview.vue';
import { Api } from '../../interfaces/api';
//@ts-ignore
import ConfirmDelete from './ConfirmDelete.vue';
import AddActivity from './AddActivity.vue';

export default defineComponent({
    name: 'ActivityDetails',
    components: {
        ExerciseSearch,
        WorkoutTemplateTable,
        ActivityCard,
        MetricChart,
        SplitsChart,
        NewTemplate,
        WorkoutSearch,
        WorkoutEntry,
        StrengthOverview,
        ConfirmDelete,
        AddActivity
    },
    props: {
        activity: {
            type: Object as () => Activity,
            required: true
        },
        activityDetails: {
            type: Object as () => ActivityDetailsData
        }
    },
    data() {
        return {
            selectedWorkout: {} as WorkoutTemplate,
            api: new Api(),
            workoutEntry: {} as Object,
            showDialog: false,
            selectedEditedWorkout: undefined as WorkoutTemplate | undefined,
            editingActivity: {} as Activity,
            loading: false
        }
    },
    watch: {
        activity(newVal) {
            if (newVal != undefined && newVal.activityType && newVal.activityType.includes("strength") && newVal.workoutTemplate) {
                this.selectedWorkout = newVal.workoutTemplate
            }
            this.loading = false
        }
    },
    methods: {
        formatDuration(durationInSeconds: number) {
            const durationObj = dayjs.duration(durationInSeconds, 'seconds');

            // If duration is more than an hour, show HH:MM:SS, otherwise MM:SS
            if (durationObj.hours() > 0) {
                return durationObj.format('H:mm:ss');
            } else {
                return durationObj.format('m:ss');
            }
        },
        handleWorkoutSelected(template: WorkoutTemplate) {
            this.selectedWorkout = template
            this.selectedEditedWorkout = {} as WorkoutTemplate
        },
        async handleWorkoutEntered(workoutData: Object) {
            try {
                const response = await this.api.editActivity(this.activity.activityId, this.activity.activityName,
                    this.activity.activityType, this.activity.distance, this.activity.duration, this.activity.averageHR,
                    this.activity.maxHR, this.activity.maxSpeed, this.activity.calories, this.selectedWorkout, workoutData)

                if (response != -1) {
                    console.log(response.data.message)
                }

                this.$emit("update-data")

                // TODO: emit event to refresh
            } catch (error) {
                console.error("Error trying to edit activity", error)
            }
        },
        handleCancel() {
            if (this.activity.workoutTemplate) {
                this.selectedWorkout = this.activity.workoutTemplate
                this.selectedEditedWorkout = {} as WorkoutTemplate
                //@ts-ignore
                if (this.activity.workoutEntry) {
                    //@ts-ignore
                    this.workoutEntry = this.activity.workoutEntry
                }
            } else {
                this.selectedWorkout = {} as WorkoutTemplate
            }
        },
        handleEditWorkout(workout: WorkoutTemplate) {
            this.selectedEditedWorkout = { ...workout }
        },
        async handleUpdate(template: WorkoutTemplate) {
            this.selectedWorkout = template
            const response = await this.api.editActivity(this.activity.activityId, this.activity.activityName,
                this.activity.activityType, this.activity.distance, this.activity.duration, this.activity.averageHR,
                this.activity.maxHR, this.activity.maxSpeed, this.activity.calories, this.selectedWorkout)

            if (response != -1) {
                console.log(response.data.message)
            }
            this.$emit("update-data")
            this.selectedEditedWorkout = {} as WorkoutTemplate
        },

        async updateData() {
            this.editingActivity = {} as Activity
            this.$emit("update-data")
            this.$refs.addActivity.closeDialog();
        },

        editActivity() {
            this.editingActivity = this.activity
            this.$emit("edit-activity", this.activity)
            this.openDialog()
        },

        showConfirmPopup() {
            this.showDialog = true; // Show the confirm dialog
        },

        async handleConfirmDeleteActivity() {
            try {
                this.loading = true
                const response = await this.api.deleteActivity(this.activity.activityId);
                if (response != -1 && response.status == 200) {
                    this.updateData()
                } else {
                    console.error("Failed to delete activity");
                }
            } catch (error) {
                console.error("Error trying to delete data", error);
            }

            this.showDialog = false;
        },

        openDialog() {
            this.$refs.addActivity.openDialog();
        },

        handleCancelDeleteActivity() {
            this.showDialog = false;
        },
    },
    computed: {
        formattedDate() {
            return dayjs(this.activity.startTimeLocal).format('MM/DD/YYYY h:mm A')
        }
    }
});
</script>

<style scoped>
.exercise-history {
    border: solid 1px black;
    height: calc(100% - 20px);
    width: calc(100% - 20px);
    margin: 10px;
}

.icon-btn:hover div {
    color: black !important;
    z-index: 10000;
}

.icon-btn:hover .icon {
    color: black !important;
    z-index: 10000;
}

.icon {
    color: white;
}

.icon-btn {
    height: 35px;
    width: 35px;
    border: solid 1px black;
}


.mdi-icon {
    margin-left: 10px;
    margin-right: 10px;
}

.activity-title {
    font-size: 20pt;
    margin-bottom: 4pt
}
</style>
