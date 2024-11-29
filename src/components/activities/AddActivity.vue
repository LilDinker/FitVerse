<template>
    <v-dialog theme="light" v-model="dialogVisible" persistent style="width: 50%">
        <v-card>
            <v-card-title>
                {{ originalActivity?.activityId ? "Edit Activity" : "Manual Activity" }}
            </v-card-title>

            <v-form style="width: 80%; margin-left: 10%;">
                <!-- Dropdown Menu (v-select) -->
                <v-select v-model="dropdownValue" :items="['Run', 'Strength', 'Cycling', 'Swim']" label="Activity Type"
                    density="compact"></v-select>

                <!-- Title Field -->
                <v-text-field class="entry" v-model="title" label="Title" :rules="[rules.required]"
                    density="compact" />

                <!-- Conditionally Render Fields -->
                <v-text-field class="entry" v-if="dropdownValue !== 'Strength'" v-model.number="distance" label="Distance (mi)"
                    type="number" :rules="[rules.required, rules.numeric]" density="compact" />

                <!-- Time Fields: Hours, Minutes, Seconds -->
                <div v-if="dropdownValue !== 'Strength'" class="duration-section">
                    <span class="duration-title">Duration</span>
                    <div class="duration-inputs">
                        <v-text-field  v-model.number="time.hours" label="Hours" type="number" :rules="[rules.numeric]"
                            density="compact" class="duration-field" />
                        <v-text-field  v-model.number="time.minutes" label="Minutes" type="number"
                            :rules="[rules.numeric]" density="compact" class="duration-field" />
                        <v-text-field v-model.number="time.seconds" label="Seconds" type="number"
                            :rules="[rules.numeric]" density="compact" class="duration-field" />
                    </div>
                    <span v-if="durationError" class="error-message">
                        Duration cannot be all zeros.
                    </span>
                </div>

                <v-text-field class="entry" v-model.number="averageHR"
                    label="Average HR (bpm) (optional)" type="number" :rules="[rules.numeric]" density="compact" />

                <v-text-field class="entry" v-model.number="maxHR" label="Max HR (bpm) (optional)"
                    type="number" :rules="[rules.numeric]" density="compact" />

                <v-text-field class="entry" v-if="dropdownValue !== 'Strength'" v-model.number="maxSpeed"
                    label="Max Speed (mph) (optional)" type="number" :rules="[rules.numeric]" density="compact" />

                <v-text-field class="entry" v-model.number="calories" label="Calories (optional)"
                    type="number" :rules="[rules.numeric]" density="compact" />
            </v-form>

            <v-card-actions>
                <button class="cancel-button" @click="closeDialog"><span class="txt">Cancel</span></button>
                <button class="submit-button" @click="saveData"><div>Save</div></button>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Api } from '../../interfaces/api';
import { Activity } from '../../interfaces';

export default defineComponent({
    name: 'AddActivity',

    props: {
        originalActivity: {
            type: Object as () => Activity
        }
    },
    data() {
        return {
            api: new Api(),
            dialogVisible: false,
            dropdownValue: 'Run',
            title: '',
            distance: null as number | null,
            time: {
                hours: 0,
                minutes: 0,
                seconds: 0,
            },
            averageHR: null as number | null,
            maxHR: null as number | null,
            maxSpeed: null as number | null,
            calories: null as number | null,
            durationError: false,
            rules: {
                required: (value: string | number) =>
                    !!value || 'This field is required',
                numeric: (value: string | number) =>
                    !isNaN(Number(value)) || 'Must be a number',
            },
        };
    },

    watch: {
        originalActivity() {
            this.checkEdit();
        }
    },

    methods: {
        checkEdit() {
            if (this.originalActivity?.activityType) {
                this.distance = this.originalActivity?.distance / 1609.34
                const totalSeconds = this.originalActivity.duration
                const hours = Math.floor(totalSeconds / 3600);
                const minutes = Math.floor((totalSeconds % 3600) / 60);
                const seconds = Math.floor(totalSeconds % 60);

                this.time = { hours: hours, minutes: minutes, seconds: seconds }

                this.title = this.originalActivity.activityName

                if (this.originalActivity.averageHR) {
                    this.averageHR = this.originalActivity.averageHR
                }
                if (this.originalActivity.maxHR) {
                    this.maxHR = this.originalActivity.maxHR
                }
                if (this.originalActivity.calories) {
                    this.calories = this.originalActivity.calories
                }
                if (this.originalActivity.maxSpeed) {
                    this.maxSpeed = this.originalActivity.maxSpeed
                }
                

                console.log(this.originalActivity)

                if (this.originalActivity.activityType.includes('strength')) {
                    this.dropdownValue = "Strength"
                } else if (this.originalActivity.activityType.includes('running')) {
                    this.dropdownValue = "Run"
                } else if (this.originalActivity.activityType.includes('cycling')) {
                    this.dropdownValue = "Cycling"
                } else if (this.originalActivity.activityType.includes('swimming')) {
                    this.dropdownValue = "Swim"
                }
            }
        },
        openDialog() {
            this.dialogVisible = true;
        },
        closeDialog() {
            this.dialogVisible = false;
            this.$emit("cancel-edit")
            this.clearData();
        },
        validateForm() {
            if (!this.title) {
                alert('Title is required.');
                return false;
            }
            if (this.dropdownValue !== 'Strength') {
                if (!this.distance) {
                    alert('Distance is required.');
                    return false;
                }
                if (
                    this.time.hours === 0 &&
                    this.time.minutes === 0 &&
                    this.time.seconds === 0
                ) {
                    this.durationError = true;
                    alert('Duration is required to be non-zero.');
                    return false;
                }
                this.durationError = false;
            }
            return true;
        },
        async saveData() {
            if (this.validateForm()) {
                const time_seconds = (this.time.hours * 3600) + (this.time.minutes * 60) + this.time.seconds
                //@ts-ignore because if distance is null we will not validate the form
                const distance_m = this.distance * 1609.34;

                let maxSpeed_ms = null
                if (this.maxSpeed) {
                    maxSpeed_ms = this.maxSpeed * 0.44704
                }
                if (this.originalActivity?.activityName) {
                    try {
                        const response = await this.api.editActivity(this.originalActivity.activityId, this.title, this.dropdownValue, distance_m, time_seconds, this.averageHR, this.maxHR, maxSpeed_ms, this.calories)

                        if (response != -1) {
                            console.log(response.data.message)
                        }
                    } catch (error) {
                        console.error("Error trying to edit activity", error)
                    }
                } else {
                    try {
                        const response = await this.api.addActivity(this.title, this.dropdownValue, distance_m, time_seconds, this.averageHR, this.maxHR, maxSpeed_ms, this.calories)

                        if (response != -1) {
                            console.log(response.data.message)
                        }
                    } catch (error) {
                        console.error("Error trying to add data to DB", error)
                    }
                }

                this.$emit("update-activities")
                this.closeDialog();
            }
        },

        clearData() {
            this.dropdownValue = 'Run',
                this.title = '',
                this.distance = null,
                this.time = {
                    hours: 0,
                    minutes: 0,
                    seconds: 0,
                },
                this.averageHR = null,
                this.maxHR = null,
                this.maxSpeed = null,
                this.calories = null
        }
    },
});
</script>

<style scoped>
.headline {
    font-weight: bold;
}

.duration-section {
    margin-top: -6px;
}

.duration-title {
    margin-top: 10px;
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 8px;
    display: block;
}

.entry {
    margin-top: 10px
}

.duration-inputs {
    display: flex;
    gap: 16px;
    /* Space between the input fields */
    align-items: center;
}

.duration-field {
    flex: 1;
    /* Ensures equal width for all inputs */
}

.error-message {
    color: red;
    font-size: 12px;
    margin-top: 4px;
}

.cancel-button {
    background-color: white;
    border: solid 1px black;
    font-size: 12pt;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    width: 100px;
}

.cancel-button:hover {
    background-color: rgb(199, 105, 105)
}
.submit-button:hover {
    background-color: rgb(92, 173, 92)
}

.submit-button {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    background-color: white;
    border: solid 1px black;
    font-size: 12pt;
    width: 100px;
}
</style>
