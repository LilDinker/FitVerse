<template>
    <!-- Confirm Dialog -->
    <ConfirmDelete :message="'Are you sure you want to delete this activity?'" v-model="showDialog"
        @confirmed="handleConfirm" @cancelled="handleCancel" />
    <v-card :class="noTitle ? 'activity-card-no-title' : 'activity-card'">
        <v-card-title
            style="padding: 5px; margin-top: 0px; margin-bottom: 15px; border-bottom: solid 1px rgb(175, 171, 171); background-color: #FF5003">
            <div style="display: flex; align-items: center; width: 100%;" v-if="!noTitle">
                <v-icon v-if="activity.activityType.includes('running')" class="mdi-icon">mdi-run</v-icon>
                <v-icon v-else-if="activity.activityType.includes('cycling')" class="mdi-icon">mdi-bike</v-icon>
                <v-icon v-else-if="activity.activityType.includes('swimming')" class="mdi-icon">mdi-swim</v-icon>
                <v-icon v-else-if="activity.activityType.includes('strength')" class="mdi-icon">mdi-dumbbell</v-icon>
                <span class="activity-title">{{ activity.activityName }}</span>
                <v-spacer />
                <span style="opacity: 0.5">{{ dateString }}</span>
                <v-btn @click="editActivity" icon small class="icon-btn"
                    style="margin-left: 10px; background-color: #FF5003; color: white; border-color: white">
                    <v-tooltip activator="parent" location="top">Edit Activity</v-tooltip>
                    <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn @click="showConfirmPopup" icon small class="icon-btn"
                    style="margin-right: 10px; background-color: #FF5003; color: white; border-color: white">
                    <v-tooltip activator="parent" location="top">Delete Activity</v-tooltip>
                    <v-icon>mdi-delete</v-icon>
                </v-btn>
            </div>
            <div v-else>Overview</div>
        </v-card-title>
        <v-row>
            <v-col class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none;     background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Distance (mi)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ convertToMiles(activity.distance) }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none;     background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Duration</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ formatDuration(activity.duration) }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none;     background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Avg Pace (min/mi) </span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ convertToMinPerMile(activity.averageSpeed) }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none;     background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Avg HR (bpm)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.averageHR ? activity.averageHR : "N/A" }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <v-row style="margin-bottom: 1px;">
            <v-col class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none;     background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Calories (kcal)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.calories ? activity.calories.toLocaleString() : "N/A"
                            }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col v-if="!activity.activityType.includes('strength')" class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none;     background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Max Speed (mph)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.maxHR ? convertToMPH(activity.maxSpeed) : "N/A"
                            }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col v-else class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Steps</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.steps != undefined ? activity.steps : "N/A"
                            }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
                        <v-col class="data-col">
                <v-card style="width: 100%; max-width: 200px; box-shadow: none;     background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Max HR (bpm)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.maxHR ? activity.maxHR : "N/A" }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Activity } from '../../interfaces';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import ConfirmDelete from './ConfirmDelete.vue';

dayjs.extend(duration);

export default defineComponent({
    name: "ActivityCard",

    props: {
        activity: {
            type: Object as () => Activity,
            required: true,
        },
        noTitle: {
            type: Boolean
        }
    },

    components: {
        ConfirmDelete
    },

    data() {
        return {
            dateString: dayjs(this.activity.startTimeLocal).format('MM/DD/YYYY h:mm A'),
            showDialog: false
        };
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

        convertToMiles(distanceInMeters: number) {
            // Convert meters to miles using dayjs
            return (distanceInMeters * 0.000621371).toFixed(2);
        },

        convertToMinPerMile(speedInMetersPerSecond: number) {
            // Convert meters per second to miles per hour using dayjs
            if (speedInMetersPerSecond > 0) {
                const minPerMile = (60 / (speedInMetersPerSecond * 2.23694));
                const durationObj = dayjs.duration(minPerMile, 'minutes');
                return durationObj.format('m:ss');
            } else {
                return "N/A"
            }
        },

        convertToMPH(speedInMetersPerSecond: number) {
            // Convert meters per second to miles per hour using dayjs
            if (speedInMetersPerSecond > 0) {
                return ((speedInMetersPerSecond * 2.23694)).toFixed(2);
            } else {
                return "N/A"
            }
        },

        editActivity() {
            this.$emit("edit-activity", this.activity)
        },

        showConfirmPopup() {
            this.showDialog = true; // Show the confirm dialog
        },

        handleConfirm() {
            this.$emit("delete-activity", this.activity)

            this.showDialog = false;
        },

        handleCancel() {
            this.showDialog = false;
        },
    }
});
</script>

<style scoped>
.title-with-buttons {
    display: flex;
    align-items: center;
    width: 100%;
}

.activity-card {
    margin-top: 20px !important;
    margin: 10px;
    width: calc(100% - 20px);
    border: solid 1px white !important;
    padding: 0px;
    background-color: #fcb055;
}

.activity-card-no-title {
    margin-left: 5px;
    width: calc(100% - 5px);
    border: solid 1px black !important;
    padding: 0px;
    background-color: #fcb055;
    box-shadow: none;
}
.icon-btn {
    margin-right: 5px;
    width: 40px;
    height: 40px;
    border: solid 1px white
}

.icon-btn:hover .v-icon {
    color: black !important;
    z-index: 10000;
}

.mdi-icon {
    margin-left: 10px;
    margin-right: 10px;
}

.activity-title {
    max-width: 38%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
}

.data-col {
    padding: 0px !important;
}
</style>