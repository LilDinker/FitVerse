<template>
    <v-card class="meal-list" theme="light">
        <v-text-field class="input" v-model="searchQuery" label="Search for Meals" @input="searchMeals"
            density="compact" outlined></v-text-field>
        <v-list v-if="Object.values(meals).length != 0 || loading" class="meal-scrollable" @scroll="onScroll">
            <div v-for="(meal, index) in meals" :key="index" class="meal-item" @click="handleMealClick(meal)">
                <p>{{ meal.name }}</p>
            </div>
            <v-progress-circular v-if="loading" indeterminate color="#003F7D" size="20"></v-progress-circular>
        </v-list>
        <v-card v-else style="box-shadow: none; padding: 0px; margin: 0px; height: calc(100% - 150px); width: 80%; margin-left:10%; display: flex; justify-content: center; align-items: center;"><p>You have no recorded meals yet. Record a new meal to get started!</p></v-card>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Api } from '../../interfaces/api';
import { Meal } from '../../interfaces';

export default defineComponent({
    name: 'MealList',
    data() {
        return {
            api: new Api(),
            searchQuery: '',
            meals: {} as Record<string, Meal>, // Simplified meal object
            loading: false,
            startIndex: 0,
            limit: 50,
        };
    },

    props: {
        refetch: {
            type: Object,
            required: true
        }
    },
    methods: {
        async fetchMeals() {
            this.loading = true;
            try {
                const response = await this.api.fetchUserMeals({
                    search: this.searchQuery,
                    startIndex: this.startIndex,
                    limit: this.limit,
                });


                if (response !== -1) {
                    const meals = response?.data.meals; // Assuming response.data is an object

                    if (this.searchQuery != '') {
                        this.meals = {} as Record<string, Meal>
                    }
                    // If meals is an object, loop through each key and push the value (meal)
                    for (const key in meals) {

                        const oldMeals = this.meals
                        const meal = meals[key] as Meal

                        if (!oldMeals[meal._id]) {
                            this.meals[meal._id] = meal
                        }
                    }

                    if (this.searchQuery == '') {
                        this.startIndex += this.limit;
                    }

                }
            } catch (error) {
                console.error('Error fetching meals:', error);
            } finally {
                this.loading = false;
            }
        },
        async searchMeals() {
            // Reset the state for a fresh search
            this.meals = {} as Record<string, Meal>
            this.startIndex = 0;
            await this.fetchMeals();
        },
        onScroll(event: Event) {
            const target = event.target as HTMLElement;
            const bottom = target.scrollHeight === target.scrollTop + target.clientHeight;

            if (bottom && !this.loading) {
                this.fetchMeals();
            }
        },
        handleMealClick(meal: Meal) {
            console.log("emitting select")
            this.$emit("select-meal", meal); // Handle meal click
        },
    },
    mounted() {
        this.fetchMeals(); // Initial fetch when the component is mounted
    },

    watch: {
        async refetch() {
            this.searchQuery = ''
            this.loading = false
            this.meals = {} as Record<string, Meal>
            this.startIndex = 0
            this.limit = 50
            await this.fetchMeals()
        }
    }
});
</script>

<style scoped>
.meal-list {
    padding-top: 0px;
    height: 100%;
    /* Full height of the parent component */
    width: 100%;
    overflow: hidden;
    /* display: flex; */
    flex-direction: column;
}

.meal-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0;
}

.meal-scrollable {
    height: calc(100% - 107px) !important;
    /* margin-top: 36px; */
    padding: 0px;
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    background-color: #fff;
    border: 1px solid #ccc;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.meal-item {
    padding: 8px 16px;
    cursor: pointer;
    background-color: white;
    border-bottom: solid 1px black;
}

.meal-item:hover {
    background-color: #5B84C4 !important;
    z-index: 10000000000;
}

.meal-item:hover p {
    color: black;
    z-index: 1000000000000000;
}

.input {
    /* height: 25px; */
    border-bottom: solid 1px white;
    background-color: white;
    margin-bottom: 0px;
}

.input .v-field {
    background-color: white !important
}
</style>
