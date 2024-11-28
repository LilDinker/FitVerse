<template>
    <v-card class="page">
        <AddActivity ref="addActivity" @update-activities="updateData" :original-activity="editingActivity" />
        <v-row style="width: 100% !important; height: 55%" justify="center">
            <v-col cols="12" sm="10" md="12" style="height: 100%">
                <v-card-title
                    style="text-align: left; font-size: 20pt; display: flex; justify-content: left; align-items: center;">
                    <span
                        style="padding-right: 10px;border-right: solid rgb(182, 89, 18) 1px; color: rgb(182, 89, 18)">Home</span>
                    <span style="margin-left: 10px; opacity: 0.75; font-size: 10pt; color: rgb(182, 89, 18)">Welcome
                        back, {{ username }}</span>
                </v-card-title>

                <v-card class="activity">
                    <v-card-title style="border-bottom: solid 1px white; background-color: #003F7D;">
                        <div style="display: flex; align-items: center; width: 100%;">
                            <span style="padding-right: 10px;border-right: solid white 1px">Recent Activity</span>
                            <span v-if="lastActivityDate" style="margin-left: 10px; opacity: 0.5;font-size: 10pt">Last
                                activity recorded on
                                {{ lastActivityDate }}</span>
                            <span v-else style="margin-left: 10px; opacity: 0.5;font-size: 10pt">Record your first
                                activity!</span>
                            <v-spacer />
                            <span v-if="syncDate != null" style="margin-left: 10px; opacity: 0.5;font-size: 10pt">Last
                                synced on
                                {{ syncDate
                                }}</span>
                            <v-btn icon small class="icon-btn-title" @click="syncGarmin(true)" v-if="syncDate">
                                <v-tooltip activator="parent" location="top">Manual Garmin Sync</v-tooltip>
                                <v-icon>mdi-sync</v-icon>
                            </v-btn>
                            <v-btn icon small class="icon-btn-title" @click="showGarminDialog = true" v-else>
                                <v-tooltip activator="parent" location="top">Link Your Garmin Account!</v-tooltip>
                                <v-icon>mdi-watch</v-icon>
                            </v-btn>

                            <v-dialog v-model="showGarminDialog" max-width="500px">
                                <GarminConnect></GarminConnect>
                            </v-dialog>

                            <v-btn icon small class="icon-btn-title" @click="openDialog()">
                                <v-tooltip activator="parent" location="top">Manual
                                    Activity Entry</v-tooltip>
                                <v-icon>mdi-plus</v-icon>
                            </v-btn>
                        </div>
                    </v-card-title>
                    <v-row v-if="activities" style="padding: 10px; height: calc(100% - 65px)">
                        <v-col v-if="lastActivityDate" v-for="activity in activities" :key="activity.activityId"
                            cols="3" style="margin: 0px !important; padding: 0px !important">
                            <ActivityCard :activity="activity" @edit-activity="setEdit"
                                @delete-activity="deleteActivity"></ActivityCard>
                        </v-col>
                        <v-col v-else
                            style="margin: 0px !important; height: 100%; padding: 0px !important; align-items: center; justify-content: center; display:flex;">
                            <v-card
                                style="background-color: white; box-shadow: none; color: black; width: 20%; text-align: center;">
                                You haven't recorded any activities yet. Link your Garmin device, or enter an activity
                                manually to get started!
                            </v-card>
                        </v-col>
                    </v-row>
                    <v-row v-else
                        style="justify-content: center;display: flex; align-items: center; padding: 10px; height: calc(100% - 65px)">
                    </v-row>
                </v-card>
            </v-col>
        </v-row>

        <v-row style="width: 100% !important; height: 45%" justify="center">
            <v-col>
                <WeekAtAGlance :activities-prop="weekGlance"></WeekAtAGlance>
            </v-col>
            <v-col>
                <v-card class="week">
                    <MealWeek :meals-data="mealWeek"></MealWeek>
                </v-card>
            </v-col>
        </v-row>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Api } from '../../interfaces/api';
import ActivityCard from '../activities/ActivityCard.vue';
import GarminConnect from '../GarminConnect.vue';
import dayjs from 'dayjs';
import MealWeek from './MealWeekHome.vue';
import { Activity, ActivitiesByCategory, DailyIntake } from '../../interfaces';
import WeekAtAGlance from './WeekAtAGlance.vue';
import AddActivity from '../activities/AddActivity.vue';
export default defineComponent({
    name: "Home",

    components: {
        ActivityCard,
        GarminConnect,
        WeekAtAGlance,
        AddActivity,
        MealWeek
    },
    data() {
        return {
            api: new Api(),
            username: null,
            syncDate: {} as String | null,
            lastActivityDate: {} as String | null,
            activities: null as Activity[] | null,
            weekGlance: {} as ActivitiesByCategory,
            editingActivity: null,
            mealWeek: null as DailyIntake[] | null,
            showGarminDialog: false, // Controls the dialog visibility
        }
    },


    async mounted() {
        try {
            const response = await this.api.verifyToken()
            if (response == -1 || !response.data.authenticated) {
                this.$router.push('/')
            } else {
                this.username = response.data.username
                if (response.data.last_synced_garmin == "first_sync") {
                    const now = new Date()
                    this.syncDate = dayjs(now).format("MM/DD/YYYY")
                    await this.syncGarmin(true)
                } else if (response.data.last_synced_garmin) {
                    this.syncDate = dayjs(response.data.last_synced_garmin).format("MM/DD/YYYY")
                    await this.syncGarmin(false)
                } else {
                    this.syncDate = null
                }
                await this.fetchActivities()
                await this.fetchWeekGlance()
                await this.fetchWeekMeals()
            }
        } catch (error) {
            console.error("Error trying to verify token: ", error)
        }

    },

    methods: {
        async fetchWeekMeals() {
            try {
                const response = await this.api.mealsByWeek(); // Call the API method
                if (response != -1) {
                    // Populate meals data and set the date of the most recent meal
                    const meals = response.data.meals_by_day as DailyIntake[]; // Assuming Meal[] is defined elsewhere
                    const dayArr = [] as DailyIntake[]
                    for (const key in meals) {
                        const meal = meals[key] as DailyIntake
                        dayArr.push(meal)
                    }
                    this.mealWeek = [...dayArr]

                }
            } catch (error) {
                console.error("Error trying to fetch meal data", error);
            }
        },
        async updateData() {
            await this.fetchActivities()
            await this.fetchWeekGlance()
            this.editingActivity = null
        },
        async syncGarmin(force: boolean) {
            try {
                const response = await this.api.garminSync(force)
                if (force) {
                    this.fetchActivities()
                }
                if (response != -1) {
                    console.log(response.data.message)
                }
            } catch (error) {
                console.error("Error trying to sync data with Garmin", error)
            }

        },

        async fetchActivities() {
            try {
                const response = await this.api.fetchActivities()
                if (response != -1) {
                    if (response.status != 201) {
                        this.activities = response.data.activities as Activity[]
                        this.lastActivityDate = dayjs(this.activities[0].startTimeLocal).format('MM/DD/YYYY')
                    } else {
                        this.lastActivityDate = null
                    }
                }
            } catch (error) {
                console.error("Error trying to fetch activity data", error)
            }
        },

        async fetchWeekGlance() {
            try {
                const response = await this.api.fetchWeekGlance();
                if (response != -1) {
                    const weekGlance = response.data.activities as ActivitiesByCategory;

                    this.weekGlance = { ...weekGlance }
                    // this.prepareChartData();
                } else {
                    console.error("Failed to fetch week's data");
                }
            } catch (error) {
                console.error("Error trying to fetch week's data", error);
            }
        },

        linkGarmin() {
            console.log("Bonk!")
        },

        openDialog() {
            this.$refs.addActivity.openDialog();
        },

        setEdit(activity: Activity) {
            this.editingActivity = activity
            this.openDialog()
        },

        async deleteActivity(activity: Activity) {
            try {
                const response = await this.api.deleteActivity(activity.activityId);
                if (response != -1 && response.status == 200) {
                    this.updateData()
                } else {
                    console.error("Failed to delete activity");
                }
            } catch (error) {
                console.error("Error trying to delete data", error);
            }
        }

    }
})
</script>

<style scoped>
.title {
    width: 100%;
    justify-content: left;
}

.week {
    width: calc(98%);
    height: 100%;
    border: solid 1px black;
    margin: 0 auto;
    margin-left: 20px;
    padding: 0px;
    background-color: #5B84C4;
}

.page {
    /* display: flex;
    flex-direction: column; */
    text-align: left;
    /* justify-content: center; */
    /* align-items: center; */
    width: 100%;
    height: calc(100vh - 64px);
    /* Full viewport height */
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    border-radius: 0px;
    background-color: #EBEBEB;
    color: black;
}

.activity {
    width: calc(98%);
    /* Adjust width as needed */
    border: solid 1px black !important;
    margin: 0 auto;
    background-color: white;
    /* Center the card horizontally */
    padding: 0px;
    height: 90%;
    /* Add padding inside the card */
}

.title-with-buttons {
    display: flex;
    align-items: center;
    width: 100%;
}

.icon-btn-title {
    margin-left: 5px;
    margin-right: 5px;
    border: solid 1px white;
    background-color: #0f579e;

}

.icon-btn-title:hover .v-icon {
    color: black !important;
    z-index: 10000;
}

.icon-btn {
    margin-left: 5px;
    margin-right: 5px;
    border: solid 1px white;
}

.icon-btn:hover .v-icon {
    color: black !important;
    z-index: 10000;
}
</style>