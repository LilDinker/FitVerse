<template>
    <v-card class="week">
        <v-card-title class="tabs">
            <span style="font-size: 20pt">Activities This Week</span>
            <v-spacer></v-spacer>
            <v-tabs v-model="selectedMetric" background-color="primary" style="margin: 0px;">
                <v-tab class="tab" value="duration"><span>Duration</span></v-tab>
                <v-tab class="tab" value="calories"><span>Calories</span></v-tab>
                <v-tab class="tab" value="distance"><span>Distance</span></v-tab>
            </v-tabs></v-card-title>
        <!-- Display the bar chart -->
        <v-row style="display: flex; align-items: center; height: calc(100% - 48px);">
            <v-col style="display: flex; justify-content: center; height: 100%" cols="8">
                <div style="display: flex; justify-content: center; align-items: center; height: 100%; width: 100%;">
                    <BarChart v-if="chartData.datasets.length" :data="chartData" :options="chartOptions"
                        class="chart" />
                    <v-progress-circular v-else indeterminate color="#003F7D" size="20"></v-progress-circular>
                </div>
            </v-col>
            <v-col
                style="padding: 10px; margin-top: 11px; color: white; height: calc(100% - 12px); border-left: solid 1px white">
                <v-card
                    style="background-color: #5B84C4; box-shadow: none; width: calc(100% - 10px); border-radius: 0px; align-items: center; ">
                    <v-card-title style="display: flex; justify-content: center; font-size: 20pt;">Weekly
                        Summary</v-card-title>
                    <v-card class="summary-card">
                        <v-card-text style="text-align: left;">
                            <span style="font-size: 20pt"> Total Activities: {{
                                totalActivities }}</span>
                        </v-card-text>
                    </v-card>
                    <v-card class="summary-card">
                        <v-card-text style="text-align: left;">
                            <span style="font-size: 20pt"> Total Calories: {{ totalCalories.toLocaleString() }}</span>
                        </v-card-text>
                    </v-card>
                    <v-card class="summary-card">
                        <v-card-text style="text-align: left;">
                            <span style="font-size: 20pt"> Total Distance: {{ totalDistance.toFixed(2) }} mi</span>
                        </v-card-text>
                    </v-card>
                    <v-card class="summary-card">
                        <v-card-text style="text-align: left;">
                            <span style="font-size: 20pt">Active Time: {{ formatDuration(totalSeconds) }}</span>
                        </v-card-text>
                    </v-card>
                    <v-card class="summary-card">
                        <v-card-text style="text-align: left;">
                            <span style="font-size: 20pt">Most Active: {{ dayWithMostActiveMinutes }}</span>
                        </v-card-text>
                    </v-card>

                </v-card>
            </v-col>
        </v-row>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { Api } from "../../interfaces/api";
import { ActivitiesByCategory, CategorizedActivity } from "../../interfaces";
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from "chart.js";
import { Bar } from "vue-chartjs";
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';

dayjs.extend(duration);

// Register Chart.js components
ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default defineComponent({
    name: "WeekAtAGlance",

    components: {
        BarChart: Bar,
    },

    props: {
        activitiesProp: {
            type: Object as () => ActivitiesByCategory,
            required: true
        }
    },

    computed: {
        totalActivities() {
            return Object.values(this.activities).reduce((total, dayActivities) => {
                return total + Object.values(dayActivities).flat().length;
            }, 0);
        },
        totalCalories() {
            return Object.values(this.activities).reduce((total, dayActivities) => {
                return total + Object.values(dayActivities).flat().reduce((sum, activity: CategorizedActivity) => sum + activity.calories, 0);
            }, 0);
        },
        totalDistance() {
            return Object.values(this.activities).reduce((total, dayActivities) => {
                return total + Object.values(dayActivities).flat().reduce((sum, activity: CategorizedActivity) => sum + activity.distance / 1609.34, 0);
            }, 0);
        },
        totalSeconds() {
            return Object.values(this.activities).reduce((total, dayActivities) => {
                return total + Object.values(dayActivities).flat().reduce((sum, activity: CategorizedActivity) => sum + activity.duration, 0);
            }, 0);
        },
        dayWithMostActiveMinutes() {
            const days = Object.keys(this.activities);
            let maxActiveMinutes = 0;
            let dayWithMaxActiveMinutes = "";

            // Mapping for full day names
            const dayNames: Record<number, string> = {
                6: "Sunday",
                0: "Monday",
                1: "Tuesday",
                2: "Wednesday",
                3: "Thursday",
                4: "Friday",
                5: "Saturday",
            };

            days.forEach((day) => {
                const totalActiveMinutesForDay = Object.values(this.activities[day])
                    .flat()
                    .reduce((total, activity: CategorizedActivity) => {
                        return total + (activity.duration / 60); // Convert duration to minutes
                    }, 0);

                if (totalActiveMinutesForDay > maxActiveMinutes) {
                    maxActiveMinutes = totalActiveMinutesForDay;
                    dayWithMaxActiveMinutes = day;
                }
            });

            // Convert the date to a day of the week
            const date = new Date(dayWithMaxActiveMinutes); // Convert the date string to a Date object
            const dayOfWeek = date.getDay(); // Get the day index (0 - Sunday, 6 - Saturday)

            return dayNames[dayOfWeek] || ""; // Return the full day name
        },
    },


    data() {
        return {
            api: new Api(),
            activities: {} as ActivitiesByCategory,
            selectedMetric: "null",
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
                            color: "#FFFFFF", // Legend label color
                            font: {
                                size: 14, // Adjust font size
                                weight: "bold",
                            },
                        },
                    },
                    title: {
                        display: true,
                        color: "#FFFFFF",
                        text: 'Active Minutes by Category'
                    },
                    tooltip: {
                        callbacks: {
                            // Customizing the tooltip to show Hours, Minutes, Seconds or Calories/Distance
                            label: (context) => {
                                const value = context.raw; // Value (duration, calories, distance)
                                // if (this.selectedMetric === 'duration') {
                                const durationObj = dayjs.duration(value, 'seconds');
                                if (durationObj.hours() > 0) {
                                    return "Time: " + durationObj.format('H:mm:ss');
                                } else {
                                    return "Time: " + durationObj.format('m:ss');
                                }
                            }
                        }
                    }
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
                            text: "Duration",
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
            }
        };
    },

    async mounted() {
        this.selectedMetric = 'duration'
    },

    watch: {
        // Watch for changes to the selectedMetric and re-prepare chart data
        selectedMetric(newMetric) {
            this.prepareChartData(); // Reprepare the chart data when selectedMetric changes
        },

        activitiesProp(newVal: ActivitiesByCategory) {
            this.activities = newVal
            this.prepareChartData()
        }
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

        prepareChartData() {
            const days = Object.keys(this.activities);
            if (days.length === 0) {
                return; // If there are no activities, do not continue
            }

            // Abbreviation mapping for the days of the week
            const dayAbbreviations = ["M", "T", "W", "Th", "F", "Sa", "Su"];

            const categories: (keyof ActivitiesByCategory[string])[] = ["running", "cycling", "swimming", "strength"];
            const categoryColors: Record<string, string> = {
                running: "rgba(75, 192, 192, 0.8)",
                cycling: "rgba(153, 102, 255, 0.8)",
                swimming: "rgba(54, 162, 235, 0.8)",
                strength: "rgba(255, 159, 64, 0.8)",
            };

            const datasets = categories.map((category) => ({
                label: category.charAt(0).toUpperCase() + category.slice(1),
                backgroundColor: categoryColors[category],
                data: days.map((day: string) => {
                    const daysActivities = this.activities[day];
                    if (!daysActivities || !daysActivities[category]) return 0; // Avoid undefined data
                    return daysActivities[category].reduce((total: number, activity: CategorizedActivity) => {
                        if (this.selectedMetric === 'duration') {
                            this.chartOptions = {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: "top",
                                        labels: {
                                            color: "#FFFFFF", // Legend label color
                                            font: {
                                                size: 14, // Adjust font size
                                                weight: "bold",
                                            },
                                        },
                                    },
                                    title: {
                                        display: true,
                                        color: "#FFFFFF",
                                        text: 'Active Minutes by Category'
                                    },
                                    tooltip: {
                                        callbacks: {
                                            label: (context) => {
                                                const value = context.raw;
                                                const durationObj = dayjs.duration(value, 'seconds');
                                                if (durationObj.hours() > 0) {
                                                    return "Time " + durationObj.format('H:mm:ss');
                                                } else {
                                                    return "Time: " + durationObj.format('m:ss');
                                                }
                                            }
                                        }
                                    }
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
                                            text: "Duration",
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
                            }
                            return total + activity.duration / 60; // Convert seconds to minutes
                        } else if (this.selectedMetric === 'calories') {
                            this.chartOptions = {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: "top",
                                        labels: {
                                            color: "#FFFFFF", // Legend label color
                                            font: {
                                                size: 14, // Adjust font size
                                                weight: "bold",
                                            },
                                        },
                                    },
                                    title: {
                                        display: true,
                                        color: "#FFFFFF",
                                        text: 'Calories Burnt by Category'
                                    },
                                    tooltip: {
                                        callbacks: {
                                            label: (context) => {
                                                const value = context.raw;
                                                return ("Calories Burnt: " + value.toLocaleString())
                                            }
                                        }
                                    }
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
                            }
                            return total + activity.calories;
                        } else if (this.selectedMetric === 'distance') {
                            this.chartOptions = {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: "top",
                                        labels: {
                                            color: "#FFFFFF", // Legend label color
                                            font: {
                                                size: 14, // Adjust font size
                                                weight: "bold",
                                            },
                                        },
                                    },
                                    title: {
                                        display: true,
                                        color: "#FFFFFF",
                                        text: 'Distance Traveled by Category'
                                    },
                                    tooltip: {
                                        callbacks: {
                                            label: (context) => {
                                                const value = context.raw;
                                                return ("Distance (mi): " + value.toFixed(2))
                                            }
                                        }
                                    }
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
                                            text: "Distance (mi)",
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
                            }
                            return total + (activity.distance / 1609.34);
                        }
                        return total;
                    }, 0);
                }),
            }));

            // Convert the dates to their corresponding day abbreviations
            const labels = days.map((day: string) => {
                const date = new Date(day); // Convert string to Date object
                const dayOfWeek = date.getDay(); // Get day index (0-6)
                return dayAbbreviations[dayOfWeek]; // Get corresponding abbreviation
            });

            this.chartData = {
                labels: labels, // Use the abbreviated days
                datasets: datasets,
            };
        },
    },
});
</script>

<style scoped>
.week {
    width: calc(98%);
    height: 100%;
    border: solid 1px black;
    margin: 0 auto;
    margin-left: 20px;
    padding: 0px;
    background-color: #5B84C4;
}

.chart {
    margin-left: 15px;
}

.tabs {
    background-color: #003F7D;
    display: flex;
    padding-bottom: 0px;
    padding-top: 0px;
    padding-right: 0px;
}

.tab:hover span {
    color: black !important;
    z-index: 1000;
}

.summary-card {
    width: 100%;
    box-shadow: none;
    background-color: #5B84C4;
    border-bottom: solid 1px white;
    border-radius: 0px;
}
</style>
