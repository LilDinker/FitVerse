<template>
    <v-card-title class="tabs">
        <span style="font-size: 16pt">Week at a Glance</span>
        <v-spacer></v-spacer>
        <v-tabs v-model="activeTab" background-color="primary" style="margin: 0px;">
            <v-tab class="tab" value="macros"><span>Macros</span></v-tab>
            <v-tab class="tab" value="calories"><span>Calories</span></v-tab>
        </v-tabs>
    </v-card-title>
    <v-row style="height: calc(100% - 48px); background-color: #5B84C4; width: 100%; margin-left: 0px; margin-top: 0px">
        <v-col cols="8" style="display: flex; justify-content: center; height: 100%; padding: 10px; margin: 0px">
            <div
                style="display: flex; justify-content: center; align-items: center; height: calc(100% - 20px); width: 100%;">
                <BarChart v-if="activeTab === 'macros' && chartData.datasets.length" :data="chartData"
                    :options="chartOptions" />
                <LineChart v-else-if="activeTab === 'calories' && lineChartData.datasets.length" :data="lineChartData"
                    :options="lineChartOptions" />
                <v-progress-circular v-else indeterminate color="#003F7D" size="20"></v-progress-circular>
            </div>
        </v-col>
        <v-col
            style="display: flex; justify-content: center; align-items: center; color: white; height: calc(100%); width: 100%; background-color: #5B84C4; border-left: solid 1px white; padding: 0px;">
            <v-card
                style="background-color: #5B84C4; box-shadow: none; width: calc(100% - 10px); height: 90%; border-radius: 0px; align-items: center; ">
                <v-card-title style="display: flex; justify-content: center; font-size: 16pt;">Weekly
                    Summary</v-card-title>
                <v-card class="summary-card">
                    <v-card-text style="text-align: left;">
                        <span style="font-size: 16pt"> Total Calories: {{ totalCalories.toFixed(2).toLocaleString()
                            }}</span>
                    </v-card-text>
                </v-card>
                <v-card class="summary-card">
                    <v-card-text style="text-align: left;">
                        <span style="font-size: 16pt"> Total Carbs: {{
                            totalCarbs.toFixed(2) }}g</span>
                    </v-card-text>
                </v-card>
                <v-card class="summary-card">
                    <v-card-text style="text-align: left;">
                        <span style="font-size: 16pt"> Total Fats: {{
                            totalFats.toFixed(2) }}g</span>
                    </v-card-text>
                </v-card>
                <v-card class="summary-card">
                    <v-card-text style="text-align: left;">
                        <span style="font-size: 16pt"> Total Protein: {{
                            totalProtein.toFixed(2) }}g</span>
                    </v-card-text>
                </v-card>
                <v-card class="summary-card">
                    <v-card-text style="text-align: left;">
                        <span style="font-size: 16pt"> Total Sugars: {{
                            totalSugars.toFixed(2) }}g</span>
                    </v-card-text>
                </v-card>

            </v-card>
        </v-col>
    </v-row>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import {
    Chart as ChartJS,
    BarElement,
    LineElement,
    CategoryScale,
    LinearScale,
    Title,
    Tooltip,
    Legend,
    PointElement,
} from "chart.js";
import { Bar, Line } from "vue-chartjs";
import { DailyIntake } from "../../interfaces";

// Register Chart.js components
ChartJS.register(BarElement, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default defineComponent({
    name: "MealWeek",

    components: {
        BarChart: Bar,
        LineChart: Line,
    },

    props: {
        mealsData: {
            type: Array as () => DailyIntake[],
            required: true,
        }
    },

    data() {
        return {
            activeTab: "macros", // Tracks the current active tab
            chartData: {
                labels: [] as string[],
                datasets: [] as { label: string; backgroundColor: string; data: number[] }[],
            },
            chartOptions: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            color: "#FFFFFF",
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                    },
                    title: {
                        display: true,
                        color: "#FFFFFF",
                        text: "Macronutrients by Day",
                    },
                },
                scales: {
                    x: {
                        title: {
                            text: "Day",
                            display: true,
                            color: "#FFFFFF", // X-axis title color
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF", // X-axis tick color
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)", // Gridline color
                        },
                        stacked: true,
                    },
                    y: {
                        title: {
                            text: "Grams",
                            display: true,
                            color: "#FFFFFF", // Y-axis title color
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF", // Y-axis tick color
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)", // Gridline color
                        },
                        stacked: true,
                    },
                },
            },
            lineChartData: {
                labels: [] as string[],
                datasets: [
                    {
                        label: "Calories",
                        borderColor: "rgba(255, 159, 64, 0.8)",
                        backgroundColor: "rgba(255, 159, 64, 0.3)",
                        data: [] as number[],
                        fill: true,
                    },
                ],
            },
            lineChartOptions: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: "top",
                        labels: {
                            color: "#FFFFFF",
                        },
                    },
                    title: {
                        display: true,
                        text: "Calories by Day",
                        color: "#FFFFFF",
                    },
                },
                scales: {
                    x: {
                        title: {
                            text: "Day",
                            display: true,
                            color: "#FFFFFF", // X-axis title color
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF", // X-axis tick color
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)", // Gridline color
                        },
                        stacked: true,
                    },
                    y: {
                        title: {
                            text: "Calories",
                            display: true,
                            color: "#FFFFFF", // Y-axis title color
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF", // Y-axis tick color
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)", // Gridline color
                        },
                        stacked: true,
                    },
                },
            },
        };
    },

    watch: {
        mealsData: {
            handler() {
                this.prepareChartData();
                this.prepareLineChartData();
            },
            immediate: true,
        },
    },

    computed: {
        totalCalories(): number {
            return this.mealsData.reduce((acc, meal) => acc + meal.total_calories, 0);
        },
        totalCarbs(): number {
            return this.mealsData.reduce((acc, meal) => acc + meal.total_carbs, 0);
        },
        totalFats(): number {
            return this.mealsData.reduce((acc, meal) => acc + meal.total_fats, 0);
        },
        totalProtein(): number {
            return this.mealsData.reduce((acc, meal) => acc + meal.total_proteins, 0);
        },
        totalSugars(): number {
            return this.mealsData.reduce((acc, meal) => acc + meal.total_sugars, 0);
        },
    },

    methods: {
        prepareChartData() {
            const dayAbbreviations = ["M", "T", "W", "Th", "F", "Sa", "Su"];
            const labels = this.mealsData.map((meal) => {
                const date = new Date(meal.day);
                const dayOfWeek = date.getDay();
                return dayAbbreviations[dayOfWeek];
            });

            this.chartData = {
                labels,
                datasets: [
                    {
                        label: "Carbs",
                        backgroundColor: "rgba(75, 192, 192, 0.8)",
                        data: this.mealsData.map((meal) => meal.total_carbs),
                    },
                    {
                        label: "Fats",
                        backgroundColor: "rgba(255, 99, 132, 0.8)",
                        data: this.mealsData.map((meal) => meal.total_fats),
                    },
                    {
                        label: "Proteins",
                        backgroundColor: "rgba(54, 162, 235, 0.8)",
                        data: this.mealsData.map((meal) => meal.total_proteins),
                    },
                ],
            };
        },

        prepareLineChartData() {
            const dayAbbreviations = ["M", "T", "W", "Th", "F", "Sa", "Su"];
            const labels = this.mealsData.map((meal) => {
                const date = new Date(meal.day);
                const dayOfWeek = date.getDay();
                return dayAbbreviations[dayOfWeek];
            });

            this.lineChartData = {
                labels,
                datasets: [
                    {
                        label: "Calories",
                        borderColor: "rgba(255, 159, 64, 0.8)",
                        backgroundColor: "rgba(255, 159, 64, 0.3)",
                        data: this.mealsData.map((meal) => meal.total_calories),
                        fill: true,
                    },
                ],
            };
        },
    },
});
</script>

<style scoped>
.macronutrient-chart {
    width: calc(98%);
    height: 100%;
    border: solid 1px black;
    margin: 0 auto;
    margin-left: 20px;
    padding: 0px;
    background-color: #5B84C4;
}

.tabs {
    background-color: #003F7D;
    display: flex;
    align-items: center;
    padding-bottom: 0px;
    padding-top: 0px;
    padding-right: 0px;
}

.summary-card {
    width: 100%;
    box-shadow: none;
    background-color: #5B84C4;
    border-bottom: solid 1px white;
    border-radius: 0px;
}

.tab:hover span {
    color: black !important;
    z-index: 1000;
}
</style>
