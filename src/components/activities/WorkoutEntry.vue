<template>
    <v-card style="margin-top: 10px; border-top: solid 1px black; background-color: #fcb055">
        <v-card-title style="display: flex; align-items: center;">
            <div>Workout Data Entry</div><v-spacer></v-spacer>
            <button @click="initializeSetData(true)" class="cancel-button">
                <span>Clear Entries</span>
            </button>
            <button @click="submitWorkout" class="submit-button" style="margin: 0px">
                <span>Submit Workout</span>
            </button>
        </v-card-title>
        <v-card class="workout-entry">
            <v-container fluid>
                <v-row v-for="(exerciseItem, exerciseIndex) in workoutTemplate.selectedItems" :key="exerciseIndex"
                style="margin-top: -30px">
                    <v-col cols="11" style="padding-left: 20px">
                        <v-card class="table-card">
                            <v-card-title
                                style="padding: 5px; margin-top: 0px; background-color: #003F7D; color: white; border-bottom: solid 1px rgb(175, 171, 171);">
                                <div style="display: flex; align-items: center; width: 100%;">
                                    <span style="margin-left: 10px;">{{ exerciseItem.exercise?.title || 'CustomExercise'
                                        }}</span>
                                </div>
                            </v-card-title>
                            <table
                                style="width: 100%; height: 50px; border-spacing: 0px; border: solid 1px black; background-color: #7986cb">
                                <thead style="height: 25px; width: 100%;">
                                    <tr style="background-color: #5B84C4; color: black;">
                                        <th style="width: 25%">Set</th>
                                        <th style="width: 25%">Weight</th>
                                        <th style="width: 25%">Reps</th>
                                        <th style="">Failure</th>
                                    </tr>
                                </thead>
                            </table>
                            <div class="scroll-container">
                                <div class="table-wrapper">
                                    <table style="width: 100%">
                                        <tbody>
                                            <tr class="table-row" style="width: 100%" v-for="n in exerciseItem.sets"
                                                :key="n">
                                                <td style="width: 25%">{{ `Set ${n}` }}</td>
                                                <td style="width: 25%">
                                                    <v-text-field v-model="getSetData(exerciseIndex, n - 1).weight"
                                                        label="Weight" type="number" min="0" density="compact"
                                                        class="fixed-height-input"></v-text-field>
                                                </td>
                                                <td style="width: 25%">
                                                    <v-text-field v-model="getSetData(exerciseIndex, n - 1).reps"
                                                        label="Reps" type="number" min="0" density="compact"
                                                        class="fixed-height-input"></v-text-field>
                                                </td>
                                                <td style="width: 25%">
                                                    <v-checkbox :theme="'dark'"
                                                        v-model="getSetData(exerciseIndex, n - 1).failure"
                                                        label="Failure" outlined />
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-card>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { WorkoutTemplate, ExerciseItem } from '../../interfaces';

export default defineComponent({
    name: 'WorkoutEntry',
    props: {
        workoutTemplate: {
            type: Object as () => WorkoutTemplate,
            required: true,
        },
        workoutData: {
            type: Object as () => {
                workout_template_id: string;
                user_id: string;
                template_name: string;
                exercise_entries: {
                    exercise_id: string | null;
                    sets: number;
                    weights: number[];
                    reps: number[];
                    failure: boolean[];
                }[];
            } | undefined,
            required: false, // Optional prop
            default: null,
        },
    },
    data() {
        return {
            // Holds the data for each set of each exercise
            setData: [] as {
                weight: number[];  // Array of weights for each set
                reps: number[];    // Array of reps for each set
                failure: boolean[]; // Array of failure flags for each set
            }[],
        };
    },
    mounted() {
        this.initializeSetData();
    },

    watch: {
        workoutTemplate() {
            this.initializeSetData()
        }
    },
    methods: {
        // Initialize setData based on workoutTemplate selectedItems
        initializeSetData(force?: boolean) {
            console.log(this.workoutData)
            if (this.workoutData && this.workoutData.exercise_entries && !force && this.workoutData.workout_template_id == this.workoutTemplate._id) {
                this.setData = this.workoutData.exercise_entries.map((entry) => {
                    return entry.weights.map((weight, index) => ({
                        weight: weight || 0,
                        reps: entry.reps[index] || 0,
                        failure: entry.failure[index] || false,
                    }));
                });
            } else {
                this.setData = this.workoutTemplate.selectedItems.map((exerciseItem) => {
                    return Array.from({ length: exerciseItem.sets }, () => ({
                        weight: 0,
                        reps: 0,
                        failure: false,
                    }));
                });
            }
        },

        // Function to get set data for a specific exercise and set index
        getSetData(exerciseIndex: number, setIndex: number) {
            if (!this.setData[exerciseIndex]) {
                this.setData[exerciseIndex] = [];
            }
            if (!this.setData[exerciseIndex][setIndex]) {
                this.setData[exerciseIndex][setIndex] = {
                    weight: 0,
                    reps: 0,
                    failure: false,
                };
            }
            return this.setData[exerciseIndex][setIndex];
        },

        // Handle form submission
        submitWorkout() {
            let workoutEntry;

            if (this.workoutData && this.workoutData.exercise_entries) {
                // If workoutData exists, structure the workout entry based on it
                workoutEntry = {
                    workout_template_id: this.workoutTemplate._id,
                    user_id: this.workoutData.user_id, // Use provided user ID from workoutData
                    template_name: this.workoutTemplate.name,
                    exercise_entries: this.workoutTemplate.selectedItems.map((entry, exerciseIndex) => ({
                        exercise_id: entry.exercise?._id,
                        sets: entry.sets,
                        weights: this.setData[exerciseIndex]?.map(set => set.weight),
                        reps: this.setData[exerciseIndex]?.map(set => set.reps),
                        failure: this.setData[exerciseIndex]?.map(set => !!set.failure),
                    })),
                };
            } else {
                // If workoutData doesn't exist, structure the workout entry based on workoutTemplate
                workoutEntry = {
                    workout_template_id: this.workoutTemplate._id,
                    user_id: 'user_id_placeholder', // Replace with actual user ID
                    template_name: this.workoutTemplate.name,
                    exercise_entries: this.workoutTemplate.selectedItems.map((exerciseItem, exerciseIndex) => ({
                        exercise_id: exerciseItem.exercise._id || null, // Include exercise_id
                        sets: exerciseItem.sets,
                        weights: this.setData[exerciseIndex]?.map(set => set.weight) || [],
                        reps: this.setData[exerciseIndex]?.map(set => set.reps) || [],
                        failure: this.setData[exerciseIndex]?.map(set => !!set.failure) || [],
                    })),
                };
            }

            // Log to the console for debugging
            console.log('Workout Entry submitted:', workoutEntry);

            // Emit the structured workout entry
            this.$emit("workout-entered", workoutEntry);
        },

    },
});
</script>


<style scoped>
.workout-entry {
    padding: 20px;
    height: calc(51vh - 50px);
    overflow-y: auto;
    background-color: #fcb055;
    width: calc(96%);
}

.v-card {
    margin-bottom: 20px;
}

.cancel-button {
    margin-right: 10px !important;
    margin-top: 0px !important;
    background-color: #fcb055;
    border: solid 1px black;
    font-size: 12pt;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
}

.cancel-button:hover {
    background-color: white
}

.submit-button:hover {
    background-color: rgb(92, 173, 92)
}

.submit-button {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    margin-right: 10px !important;
    margin-top: 0px !important;
    background-color: #fcb055;
    border: solid 1px black;
    font-size: 12pt;
}


.button {
    margin-top: 20px;
}
</style>