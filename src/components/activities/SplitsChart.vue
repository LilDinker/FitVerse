<template>
    <div>
        <BarChart v-if="chartData" :data="chartData" :options="chartOptions" :height="130" :width="250" />
        <div v-else>Loading chart data...</div>
    </div>
</template>

<script>
import { defineComponent, watch } from "vue";
import { Bar } from "vue-chartjs";
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from "chart.js";
import { Api } from "../../interfaces/api"; // Ensure the Api is correctly imported

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default defineComponent({
    name: "SplitsChart",
    components: {
        BarChart: Bar,
    },
    props: {
        activityId: {
            type: String,
            required: true,
        },
    },
    data() {
        return {
            api: new Api(),
            chartData: null,
            chartOptions: {
                responsive: true,
                indexAxis: 'y', // Set horizontal bar chart
                plugins: {
                    title: {
                        display: true,
                        text: "Average Pace (min/mile)",
                        color: "black", // Set title color to black
                    },
                    legend: false,
                    tooltip: {
                        callbacks: {
                            label: function (tooltipItem) {
                                const paceInSeconds = tooltipItem.raw;
                                const minutes = Math.floor(paceInSeconds / 60); // Calculate minutes
                                const seconds = Math.round(paceInSeconds % 60); // Calculate remaining seconds

                                // Get the distance for the current lap (in meters), convert to miles
                                const lapIndex = tooltipItem.dataIndex;  // Get the current index of the lap
                                const distanceInMeters = tooltipItem.chart.data.datasets[0].distance[Number(lapIndex)]; // Access the distance array (meters)
                                const distanceInMiles = (distanceInMeters / 1609.344).toFixed(2); // Convert distance to miles

                                // Return the pace and distance on separate lines
                                return [
                                    `Pace: ${minutes}:${seconds.toString().padStart(2, '0')} min/mi`,
                                    `Distance: ${distanceInMiles} miles`,
                                ];
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Pace (min/mile)",
                            color: "black", // Set x-axis title color to black
                        },
                        ticks: {
                            color: "black", // Set x-axis ticks color to black
                            callback: function (value) {
                                const minutes = Math.floor(value / 60); // Convert seconds to minutes
                                const seconds = value % 60; // Convert to seconds
                                return `${minutes}:${seconds.toString().padStart(2, '0')}`; // Display in MM:SS format
                            },
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: "Lap",
                            color: "black", // Set y-axis title color to black
                        },
                        ticks: {
                            color: "black", // Set y-axis ticks color to black
                        },
                    },
                },
            },
        };
    },
    methods: {
        // Fetch chart data from the API when activityId changes or on component mount
        async fetchChartData() {
            try {
                const response = await this.api.fetchActivitySplits(this.activityId);

                const data = response.data.splits;
                const categories = Object.values(data.categories); // Lap numbers (y-axis)
                const series = data.series; // Various metrics

                // Extracting only "Average Speed (m/s)" and converting to "Pace (min/mile)"
                const averageSpeedData = Object.values(series).find(metric => metric.name === "Average Speed (m/s)");
                const distanceData = Object.values(series).find(metric => metric.name === "Distance (meters)");

                if (!averageSpeedData || !distanceData) return;

                const paceInSeconds = averageSpeedData.data.map((speed) => {
                    const paceInMps = 1 / speed; // Convert speed to pace (seconds per meter)
                    const paceInSeconds = paceInMps * 1609.344; // Convert to pace in seconds per mile
                    return paceInSeconds;
                });

                const distanceInMeters = distanceData.data; // Distance in meters

                // Populate chart data
                this.chartData = {
                    labels: categories, // Lap indices (y-axis)
                    datasets: [
                        {
                            label: "Pace (min/mile)",
                            data: paceInSeconds,
                            backgroundColor: '#5B84C4',
                            borderColor: "#5B84C4",
                            borderWidth: 1,
                            distance: distanceInMeters, // Include distance in meters for each lap
                        },
                    ],
                };
            } catch (error) {
                console.error("Error fetching chart data:", error);
            }
        }

    },
    watch: {
        // Fetch chart data when the activityId prop changes
        activityId(newActivityId) {
            this.fetchChartData();
        },
    },
    mounted() {
        // Fetch chart data on component mount
        this.fetchChartData();
    },
});
</script>

<style scoped>
/* You can add additional styling here if needed */
</style>
