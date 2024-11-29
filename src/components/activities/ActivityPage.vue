<template>
    <v-card class="page">
        <v-row style="height: 100%; width: 100%; margin: 0px; padding: 0px;">
            <v-col style="padding: 0px; height: calc(100vh - 64px)" cols="2">
                <v-card class="nutrition-history" theme="light">
                    <v-card-title
                        style="padding: 5px; margin-top: 0px; border-bottom: solid 1px rgb(175, 171, 171); background-color: #FF5003">Activities</v-card-title>
                    <ActivityList :refetch="refetch" @select-activity="handleActivitySelect"></ActivityList>
                </v-card>
            </v-col>

            <v-col style="padding: 0px;" cols="5">
                <v-row style="height: 100%; width: 100%; margin: 0px; padding: 0px;">
                    <v-card class="nutrition-history" style="background-color: #fcb055 !important" theme="light">
                        <ActivityDetails @update-data="handleUpdate" :activity="selectedActivity"
                            :activity-details="activityDetails" />
                    </v-card>
                </v-row>
            </v-col>

            <v-col style="padding: 0px;" cols="5">
                <v-card class="nutrition-history" style="background-color: #5B84C4" theme="light">
                    <ActivitySummary :refetch="refetch"></ActivitySummary>
                </v-card>
            </v-col>
        </v-row>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import ActivityList from './ActivityList.vue';
import ActivityDetails from './ActivityDetails.vue';
import { Activity, ActivityDetailsData } from '../../interfaces';
import { Api } from '../../interfaces/api';
import ActivitySummary from './ActivitySummary.vue';

export default defineComponent({
    name: "ActivityPage",

    components: { ActivityList, ActivityDetails, ActivitySummary },

    data() {
        return {
            selectedActivity: {} as Activity,
            activityDetails: {} as ActivityDetailsData,
            api: new Api(),
            refetch: {}
        }
    },

    async mounted() {
        try {
            const response = await this.api.verifyToken()
            if (response == -1 || !response.data.authenticated) {
                this.$router.push('/')
            }
        } catch (error) {
            console.error("Error trying to verify token: ", error)
        }

    },

    methods: {
        async handleActivitySelect(activity: Activity) {
            if (activity != null && activity != undefined && !activity.manualActivity && !activity.activityType.includes("strength")) {
                const response = await this.api.fetchActivityDetails(activity.activityId)

                this.activityDetails = response.data as ActivityDetailsData

            }

            this.selectedActivity = { ...activity }
        },
        async handleUpdate(del?: boolean) {
            if (del) {
                this.refetch = {}
            } else {
                this.refetch = { id: this.selectedActivity._id }
            }
            console.log("Changiong refetch: ", this.refetch)
        }
    }
});
</script>

<style scoped>
.page {
    width: 100%;
    height: calc(100vh - 64px);
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    border-radius: 0px;
    background-color: #EBEBEB;
    color: black;
    position: relative;
}

.nutrition-history {
    border: solid 1px black;
    height: calc(100% - 20px);
    width: calc(100% - 20px);
    margin: 10px;
}
</style>
