<template>
    <!-- Confirm Dialog -->
    <ConfirmDelete :message="'Are you sure you want to delete this item?'" v-model="showDialog"
        @confirmed="handleConfirm" @cancelled="handleCancel" />
    <v-card class="strengthCard">
        <v-card-title
            style="padding: 5px; margin-top: 0px; margin-bottom: 15px; border-bottom: solid 1px rgb(175, 171, 171); background-color: #FF5003">
            Overview
        </v-card-title>
        <v-row style="padding: 0px; width: 100%; margin-left: 0px">
            <v-col class="data-col">
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Duration</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ formatDuration(activity.duration) }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col class="data-col">
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Avg HR (bpm)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.averageHR ? activity.averageHR : "N/A" }}</span>
                    </v-card-text>
                </v-card>
            </v-col>

            <v-col class="data-col">
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Max HR (bpm)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.maxHR ? activity.maxHR : "N/A" }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col class="data-col">
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Total Exercises</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity?.workoutTemplate ? activity.workoutTemplate.selectedItems.length : "N/A"}}</span>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <v-row style="padding: 0px; width: 100%; margin-left: 0px; margin-bottom: 10px">
            <v-col class="data-col">
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Calories (kcal)</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity.calories ? activity.calories.toLocaleString() : "N/A"
                            }}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col class="data-col">
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
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
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Workout</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ activity?.workoutTemplate ? activity.workoutTemplate.name : "None"}}</span>
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col class="data-col">
                <v-card style="width: 100%;   box-shadow: none; background-color: #fcb055">
                    <v-card-title style="text-align: center; padding: 0px">
                        <span style="font-size: 10pt; opacity: 0.8;">Total Sets</span>
                    </v-card-title>
                    <v-card-text style="text-align: center;">
                        <span style="font-size: 20pt"> {{ totalSets != undefined ? totalSets : "N/A"}}</span>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Activity, ExerciseItem } from '../../interfaces';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import ConfirmDelete from './ConfirmDelete.vue';

dayjs.extend(duration);

export default defineComponent({
    name: "StrengthOverview",

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

    computed: {
        totalSets() {
            if (this.activity.workoutTemplate) {
                if ( this.activity.workoutTemplate.selectedItems) {
                    let sumSets = 0
                    console.log(this.activity.workoutTemplate.selectedItems)
                    this.activity.workoutTemplate.selectedItems.forEach((item, index) => {
                        sumSets += item.sets
                    })
                    return sumSets
                } else {
                    return 0
                }
            } else {
                return undefined
            }
        }
    },

    methods: {
        formatDuration(durationInSeconds: number) {
            console.log("asdasdasdadas", this.activity)
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
            console.log("jahlksdahf")
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

.strengthCard {
    width: 90%;
    margin-left: 4%;
    border: solid 1px black;
    background-color: #fcb055;
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