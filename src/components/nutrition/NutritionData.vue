<template>
    <v-card-title
        style="background-color: #003F7D; color: white; height: 51px; padding: 0px; padding-left: 10px; display: flex; align-items: center;">
        <div>Recent Nutritional Trends</div>
        <v-spacer></v-spacer>
        <v-tabs v-model="activeTab" style="padding-top: 0px; height: 100%" slider-color="white" dense>
            <v-tab class="tab" value="day"><span>Days</span></v-tab>
            <v-tab class="tab" value="week"><span>Weeks</span></v-tab>
        </v-tabs>
    </v-card-title>
    <v-row style="height: calc(100% - 48px); background-color: #5B84C4; width: 100%; margin-left: 0px; margin-top: 0px">
        <v-col style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <div
                style="display: flex; flex-wrap:wrap; justify-content: center; align-items: center; width: 100%; height: 100%;">
                <div v-if="macroChartData.datasets.length"
                    style="height: 50%; width: 100%; display: flex; align-items: center; border-bottom: solid 1px white">
                    <!-- Macronutritional Chart -->
                    <LineChart :data="macroChartData" :options="macroChartOptions" />
                </div>
                <!-- Calories Chart -->
                <div v-if="caloriesChartData.datasets.length"
                    style="height: 50%; width: 100%; display: flex; align-items: center;">
                    <LineChart :data="caloriesChartData" :options="caloriesChartOptions" />
                </div>
                <v-progress-circular v-else indeterminate color="#003F7D" size="20"></v-progress-circular>
            </div>
        </v-col>
    </v-row>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Title,
    Tooltip,
    Legend,
} from "chart.js";
import { Line } from "vue-chartjs";
import { Api } from "../../interfaces/api";

// Register Chart.js components
ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default defineComponent({
    name: "MacronutritionalChart",
    components: {
        LineChart: Line,
    },
    props: {
        refetch: {
            type: Object, 
        }
    },
    data() {
        return {
            api: new Api(),
            activeTab: "day", // Default to "week"
            macroChartData: {
                labels: [] as string[],
                datasets: [] as { label: string; borderColor: string; data: number[]; backgroundColor: string }[],
            },
            macroChartOptions: {
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
                        text: "Macronutritional Intake Over Time",
                        color: "#FFFFFF",
                    },
                },
                scales: {
                    x: {
                        title: {
                            text: "Day",
                            display: true,
                            color: "#FFFFFF",
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF",
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)",
                        },
                    },
                    y: {
                        title: {
                            text: "Grams",
                            display: true,
                            color: "#FFFFFF",
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF",
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)",
                        },
                    },
                },
            },
            caloriesChartData: {
                labels: [] as string[],
                datasets: [] as { label: string; borderColor: string; data: number[]; backgroundColor: string }[],
            },
            caloriesChartOptions: {
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
                        text: "Caloric Intake Over Time",
                        color: "#FFFFFF",
                    },
                },
                scales: {
                    x: {
                        title: {
                            text: "Day",
                            display: true,
                            color: "#FFFFFF",
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF",
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)",
                        },
                    },
                    y: {
                        title: {
                            text: "Calories",
                            display: true,
                            color: "#FFFFFF",
                            font: {
                                size: 14,
                                weight: "bold",
                            },
                        },
                        ticks: {
                            color: "#FFFFFF",
                        },
                        grid: {
                            color: "rgba(255, 255, 255, 0.2)",
                        },
                    },
                },
            },
        };
    },
    methods: {
        async fetchData() {
            try {
                const response = await this.api.fetchNutritionData(this.activeTab); // Call the API method
                if (response != -1) {
                    const data = Object.values(response.data.nutrition_summary);
                    // Update Macronutritional Chart Data
                    this.macroChartData = {
                        labels: data.map((entry: any) => this.activeTab == "day" ? entry[this.activeTab].slice(5) : entry[this.activeTab]),
                        datasets: [
                            {
                                label: this.activeTab == "week" ? "Daily Proteins" : "Carbs",
                                borderColor: "rgba(75, 192, 192, 0.8)",
                                backgroundColor: "rgba(75, 192, 192, 0.3)",
                                data: data.map((entry: any) => entry.total_carbs),
                            },
                            {
                                label: this.activeTab == "week" ? "Daily Proteins" : "Proteins",
                                borderColor: "rgba(54, 162, 235, 0.8)",
                                backgroundColor: "rgba(54, 162, 235, 0.3)",
                                data: data.map((entry: any) => entry.total_proteins),
                            },
                            {
                                label: this.activeTab == "week" ? "Daily Fats" : "Fats",
                                borderColor: "rgba(255, 99, 132, 0.8)",
                                backgroundColor: "rgba(255, 99, 132, 0.3)",
                                data: data.map((entry: any) => entry.total_fats),
                            },
                            {
                                label: this.activeTab == "week" ? "Daily Sugars" : "Sugars",
                                borderColor: "rgba(255, 159, 64, 0.8)",
                                backgroundColor: "rgba(255, 159, 64, 0.3)",
                                data: data.map((entry: any) => entry.total_sugars),
                            },
                        ],
                    };

                    // Update Calories Chart Data
                    this.caloriesChartData = {
                        labels: data.map((entry: any) => this.activeTab == "day" ? entry[this.activeTab].slice(5) : entry[this.activeTab]),
                        datasets: [
                            {
                                label: this.activeTab == "week" ? "Average Daily Calories" : "Calories",
                                borderColor: "rgba(255, 159, 64, 0.8)",
                                backgroundColor: "rgba(255, 159, 64, 0.3)",
                                data: data.map((entry: any) => entry.total_calories),
                            },
                        ],
                    };
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        },
    },
    watch: {
        activeTab(newTab: string) {
            this.fetchData();
        },
        refetch() {
            this.fetchData();
        }
    },
    mounted() {
        this.fetchData();
    },
});
</script>


<style scoped>
.tab:hover span {
    color: black !important;
    z-index: 1000;
}
</style>
