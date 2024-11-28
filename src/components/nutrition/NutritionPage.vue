<template>
    <v-card class="page">
        <v-row style="height: 100%; width: 100%; margin: 0px; padding: 0px;">
            <v-col style="padding: 0px; max-height: calc(100vh - 64px)" cols="2">
                <v-card class="nutrition-history">
                    <v-card-title
                        style="padding: 5px; margin-top: 0px; border-bottom: solid 1px rgb(175, 171, 171); background-color: #FF5003">Meal
                        History</v-card-title>
                    <MealList @select-meal="handleSelectMeal" :refetch="refetch"></MealList>
                </v-card>
            </v-col>

            <v-col style="padding: 0px;" cols="5">
                <v-row style="height: 60%; width: 100%; margin: 0px; padding: 0px;">
                    <NewMeal :selectedMeal="selectedMeal" @cancel-edit="handleCancelEdit"
                        @update-data="handleUpdateData" @delete-meal="handleDeleteMeal" />
                </v-row>
                <v-row style="height: 40% !important; max-height: 40%; width: 100%; margin: 0px; padding: 0px;">
                    <v-card class="nutrition-history">
                        <MealWeek :meals-data="mealWeek" v-if="mealWeek != null"></MealWeek>
                    </v-card>
                </v-row>
            </v-col>

            <v-col style="padding: 0px;" cols="5">
                <v-card class="nutrition-history" style="background-color: #5B84C4" theme="light"><NutritionData :refetch="refetch"/></v-card>
            </v-col>
        </v-row>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import NewMeal from './NewMeal.vue'; // Import the new component
import { Api } from '../../interfaces/api';
import { Meal } from '../../interfaces';
import MealList from './MealList.vue';
import MealWeek from './MealWeekNutrition.vue';
import { DailyIntake } from "../../interfaces";
import NutritionData from './NutritionData.vue';

export default defineComponent({
    name: "NutritionPage",
    components: {
        NewMeal,
        MealList,
        MealWeek,
        NutritionData
    },

    data() {
        return {
            api: new Api(),
            selectedMeal: {} as Meal,
            refetch: {} as Object,
            mealWeek: null as DailyIntake[] | null
        }
    },

    async mounted() {
        try {
            const response = await this.api.verifyToken()
            if (response == -1 || !response.data.authenticated) {
                this.$router.push('/')
            } else {
                this.fetchWeekMeals()
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
        handleUpdateData() {
            this.refetch = {} as Object
            this.selectedMeal = {} as Meal;
            this.fetchWeekMeals()
        },
        async handleDeleteMeal(_id: string) {
            try {
                const response = await this.api.deleteMeal(_id); // Call the API method
                if (response != -1) {
                    this.handleUpdateData()
                }
            } catch (error) {
                console.error("Error trying to fetch meal data", error);
            }
        },
        handleSelectMeal(meal: Meal) {
            this.selectedMeal = meal;
        },
        handleCancelEdit() {
            this.selectedMeal = {} as Meal
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
}

.nutrition-history {
    border: solid 1px black;
    height: calc(100% - 20px);
    width: calc(100% - 20px);
    margin: 10px;
}
</style>
