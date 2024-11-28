<template>
    <LineChart style="width: 100% !important" :data="lineChartData" :options="lineChartOptions" />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Metric } from '../../interfaces';
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
    TimeScale,
} from "chart.js";
import { Bar, Line } from "vue-chartjs";

ChartJS.register(BarElement, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default defineComponent({
    name: "MetricChart",
    components: {
        BarChart: Bar,
        LineChart: Line,
    },

    props: {
        time: {
            type: Array as () => number[], // Array of numbers (seconds since start)
            required: true
        },
        metric: {
            type: Object as () => Metric,
            required: true,
        }
    },

    computed: {
        // Format seconds to MM:SS for x-axis
        formattedTime(): string[] {
            return this.time.map(seconds => {
                const minutes = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
            });
        },

        // Format camelCase keys into readable strings and remove the word "direct"
        formattedMetricKey(): string {
            return this.metric.key
                .replace(/^direct/, '') // Remove the word "direct" if it exists
                .replace(/([A-Z])/g, ' $1') // Add a space before uppercase letters
                .trim() // Remove leading/trailing whitespace
                .replace(/^\w+/, match => match.charAt(0).toUpperCase() + match.slice(1)); // Capitalize the first meaningful word
        },

        lineChartData() {
            return {
                labels: this.formattedTime, // Formatted x-axis labels (MM:SS)
                datasets: [
                    {
                        label: this.formattedMetricKey, // Dataset label (formatted)
                        data: this.metric.values, // Y-axis values
                        borderColor: '#5B84C4', // Line color (updated)
                        backgroundColor: '#5B84C4', // Fill color under the line
                        pointBackgroundColor: '#5B84C4', // Points color
                        pointBorderColor: '#5B84C4', // Points border color
                        tension: 0.4, // Smooth curves
                        pointRadius: 2, // Removes dots on the line
                    },
                ],
            };
        },

        lineChartOptions() {
            return {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${this.formattedMetricKey} Over Time`, // Title based on formatted metric key
                        font: {
                            size: 18,
                        },
                        color: 'black', // Title color (updated)
                    },
                    tooltip: {
                        enabled: true,
                    },
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Time (MM:SS)', // X-axis label
                            color: 'black', // X-axis title color (updated)
                        },
                        ticks: {
                            color: 'black', // X-axis tick color (updated)
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: `${this.formattedMetricKey} (${this.metric.unit})`, // Y-axis label (formatted key with unit)
                            color: 'black', // Y-axis title color (updated)
                        },
                        ticks: {
                            color: 'black', // Y-axis tick color (updated)
                        },
                        beginAtZero: true, // Start y-axis at 0
                    },
                },
            };
        }
    }
});
</script>

<style></style>
