<template>
    <v-card-title
        style="background-color: #003F7D; color: white; height: 51px; padding: 0px; padding-left: 10px; display: flex; align-items: center;">
        <div>Activity Trends</div>
        <v-spacer></v-spacer>
        <!-- Granularity Tabs -->
        <v-tabs v-model="activeTab" style="padding-top: 0px; height: 100%" slider-color="white" dense>
            <v-tab class="tab" value="days"><span>Days</span></v-tab>
            <v-tab class="tab" value="weeks"><span>Weeks</span></v-tab>
            <v-tab class="tab" value="months"><span>Months</span></v-tab>
        </v-tabs>
    </v-card-title>
    <v-row style="height: 50%; background-color: #5B84C4; width: 100%; margin-left: 0px; margin-top: 0px">
        <v-col style=" height: 50%; padding: 0px; display: flex">
            <div style="flex: 1; width: 80%; height: 50%; align-items: center; justify-content: center;">
                <div v-if="chartData && chartData.labels.length">
                    <LineChart :data="{
                        labels: chartData.labels,
                        datasets: chartData.datasets,
                    }" :options="chartOptions" style="width: 100%; height: 500px !important;" />
                </div>
                <v-progress-circular v-else indeterminate color="#003F7D" size="20"></v-progress-circular>
            </div>
            <div style="width: 10%;">
                <!-- Category Tabs -->
                <v-tabs v-model="activeCategory" style="margin-bottom: 16px; margin-top: 125px; color: white"
                    slider-color="white" direction="vertical" density="compact">
                    <v-tab class="tab" disabled
                        style="text-align: center; text-decoration: underline !important; font-weight: bold !important;opacity: 1.0!important;"><span>Data</span></v-tab>
                    <v-tab class="tab" value="calories"><span>Calories</span></v-tab>
                    <v-tab class="tab" value="duration"><span>Duration</span></v-tab>
                    <v-tab class="tab" value="distance"><span>Distance</span></v-tab>
                    <v-tab class="tab" value="count"><span>Count</span></v-tab>
                </v-tabs>
                <!-- Chart -->
            </div>
        </v-col>
    </v-row>
    <v-row style="height: 50%; background-color: #5B84C4; width: 100%; margin-left: 0px; margin-top: 0px">
        <v-col style=" height: 50%; padding: 0px; display: flex">
            <div style="flex: 1; width: 100%; height: 50%; align-items: center; justify-content: center;">
                <div v-if="chartDataGarmin.labels.length">
                    <LineChart :data="{
                        labels: chartDataGarmin.labels,
                        datasets: chartDataGarmin.datasets,
                    }" :options="chartOptionsGarmin" style="width: 100%; height: 500px !important;" />
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
    name: "ActivityTrends",
    components: {
        LineChart: Line,
    },
    props: {
        refetch: {
            type: Object
        }
    },
    data() {
        return {
            api: new Api(),
            activeTab: "days", // Granularity: "days", "weeks", or "months"
            activeCategory: "calories", // Category: "calories", "duration", "distance", or "total_count"
            chartData: {
                labels: [] as string[],
                datasets: [] as Array<{
                    label: string;
                    borderColor: string;
                    backgroundColor: string;
                    data: number[];
                }>,
            },
            chartDataGarmin: {
                labels: [] as string[],
                datasets: [] as Array<{
                    label: string;
                    borderColor: string;
                    backgroundColor: string;
                    data: number[];
                }>,
            },
            fetchedData: {} as Object,
            fetchedDataGarmin: {} as Object,
            chartOptions: {
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
                        text: "Activity Data Over Time",
                        color: "#FFFFFF",
                    },
                },
                scales: {
                    x: {
                        title: {
                            text: "Time",
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
                            text: "Value",
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
            chartOptionsGarmin: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                        position: "top",
                        labels: {
                            color: "#FFFFFF",
                        },
                    },
                    title: {
                        display: true,
                        text: "Recent Step Data Over Time",
                        color: "#FFFFFF",
                    },
                },
                scales: {
                    x: {
                        title: {
                            text: "Time",
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
                            text: "Daily Steps",
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
        }
    },
    methods: {
        async fetchData() {
            try {
                // Fetch the activity data
                const response = await this.api.fetchActivitySummary(this.activeTab);
                //console.log("active data response??",response);

                if (response != -1) {
                    this.fetchedData = response.data.activities;
                    this.updateActiveData();
                    //console.log("Chart data:", this.chartData);
                }

                // Fetch the Garmin data
                if (this.activeTab == "days") {
                    const garminResponse = await this.api.fetchHealthSummary(this.activeTab);
                    //console.log("hi???", garminResponse);

                    if (garminResponse != -1) {

                        this.fetchedDataGarmin = garminResponse.data; // Assuming the Garmin data is directly inside the response
                        this.updateGarminData();
                        //console.log("Garmin Chart data:", this.chartDataGarmin);
                    }
                }

            } catch (error) {
                console.error("Error fetching data", error);
            }
        },
        updateActiveData() {
            // Create an array of label-data pairs and sort chronologically
            const sortedData = Object.entries(this.fetchedData).sort(([a], [b]) => {
                const dateA = new Date(`20${a.slice(-2)}-${a.slice(0, 2)}-01`);
                const dateB = new Date(`20${b.slice(-2)}-${b.slice(0, 2)}-01`);
                return dateA - dateB; // Sort chronologically (ascending order)
            });

            // Extract the sorted labels and corresponding data
            this.chartData.labels = sortedData.map(([label]) => label);
            const sortedValues = sortedData.map(([, value]) => value);

            let activityTypes = [];
            let yAxisTitle = "";

            // Determine which activity types and y-axis title to use based on activeCategory
            if (this.activeCategory === "distance") {
                activityTypes = ["cycling", "running", "swimming"];
                yAxisTitle = "Distance (mi)";
            } else if (this.activeCategory === "duration") {
                activityTypes = ["cycling", "running", "strength", "swimming"];
                yAxisTitle = "Duration (hrs)";
            } else if (this.activeCategory === "calories") {
                activityTypes = ["cycling", "running", "strength", "swimming"];
                yAxisTitle = "Calories";
            } else if (this.activeCategory === "count") {
                activityTypes = ["cycling", "running", "strength", "swimming"];
                yAxisTitle = "Count";
            }

            // Update the chartOptions with the dynamic y-axis title based on activeCategory
            this.chartOptions = {
                ...this.chartOptions,
                plugins: {
                    ...this.chartOptions.plugins,
                    tooltip: {
                        ...this.chartOptions.plugins?.tooltip,
                        callbacks: {
                            label: (tooltipItem) => {
                                const value = tooltipItem.raw; // Get the raw value of the point
                                let formattedValue = value;

                                // If the active category is 'duration', convert the value to HH:MM:SS
                                if (this.activeCategory === 'duration') {
                                    const hours = Math.floor(value); // Get the whole hours
                                    const minutes = Math.floor((value - hours) * 60); // Get the minutes
                                    const seconds = Math.round(((value - hours) * 60 - minutes) * 60); // Get the seconds
                                    formattedValue = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                                } else if (this.activeCategory === 'distance') {
                                    formattedValue = `${value.toFixed(2)} miles`
                                } else if (this.activeCategory === 'calories') {
                                    formattedValue = `${value.toFixed(2)} kcal`
                                } else {
                                    formattedValue = `${value} activities`
                                }

                                return `${tooltipItem.dataset.label}: ${formattedValue}`;
                            },
                        },
                    },
                },
            };
            // Generate the datasets by using sorted data values
            this.chartData.datasets = activityTypes.map((activityType) => {
                return {
                    label: activityType.charAt(0).toUpperCase() + activityType.slice(1),
                    borderColor: this.getActivityColor(activityType),
                    backgroundColor: this.getActivityColor(activityType, 0.3),
                    data: this.getActivityData(sortedValues, activityType),
                };
            });

            //console.log("Sorted Chart data:", this.chartData);
        },
        updateGarminData() {

            const labelsGarmin = Object.keys(this.fetchedDataGarmin);  // Get the dates
            const datasetGarmin = {
                data: [],
                borderColor: "#fcb055",
                backgroundColor: "rgba(153, 102, 255, 0.2)",
                fill: true,
            };

            // Loop through the data and fill the dataset based on the active tab
            labelsGarmin.forEach((date) => {
                // console.log(this.fetchedDataGarmin[date][totalDistance])
                // Access the data based on activecategoryGarmin (either 'totalSteps' or 'totalDistance')
                const categoryData = this.fetchedDataGarmin[date]["totalSteps"];

                // Push the selected category's value to the dataset
                datasetGarmin.data.push(categoryData);
            });

            // Final chart data with labels (dates) and the dynamically selected dataset
            this.chartDataGarmin = {
                labels: labelsGarmin,  // Dates
                datasets: [datasetGarmin],  // Dataset with the chart data for active tab
            };
        },
        getActivityColor(activity: string, alpha: number = 1): string {
            const colorMap: Record<string, string> = {
                running: "rgba(75, 192, 192, 0.8)",
                cycling: "rgba(153, 102, 255, 0.8)",
                swimming: "rgba(54, 162, 235, 0.8)",
                strength: "rgba(255, 159, 64, 0.8)",
            };
            return colorMap[activity] || "rgba(0, 0, 0, 1)";
        },
        getActivityData(data: any[], activityType: string) {
            //console.log(activityType)
            return data.map((entry) => {
                if (activityType == "strength" && this.activeCategory == "distance") {
                    return
                }
                if (this.activeCategory == "count") {
                    return entry[activityType].count
                } else if (this.activeCategory == "distance") {
                    const val = entry[activityType].activities?.reduce((sum, activity) => sum + (activity[this.activeCategory] || 0), 0) || 0;
                    return val / 1609.34
                } else if (this.activeCategory == "duration") {
                    const val = entry[activityType].activities?.reduce((sum, activity) => sum + (activity[this.activeCategory] || 0), 0) || 0;
                    return val / 3600
                } else {
                    return entry[activityType].activities?.reduce((sum, activity) => sum + (activity[this.activeCategory] || 0), 0) || 0;
                }
            });
        }
    },
    watch: {
        activeTab(newTab: string) {
            this.fetchData(); // Refetch only on granularity change
        },
        activeCategory(newCategory: string) {
            this.updateActiveData()
        },
        refetch() {
            //console.log("Noticed a rfetch!!!!!")
            this.fetchData()
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