<template>
    <!-- Header Section -->
    <v-card-title style="margin-top: 5px" v-if="selectedWorkout?._id">Edit Template</v-card-title>
    <v-card-title v-else style="margin-top: 5px;">New Workout Template</v-card-title>

    <!-- Template Name -->
    <v-text-field style="width: 90%; margin-right: 5%; margin-top: 5px; margin-left: 5%; margin-bottom: 20px"
        label="Template Name" density="compact" v-model="name"></v-text-field>

    <!-- Main Content -->
    <!-- Exercise Search Section -->
    <exercise-search @item-selected="handleItemSelected"></exercise-search>

    <!-- Workout Table Section -->
    <workout-template-table :exercise-items="selectedItems" @add-custom="handleAddCustom"
        @delete-item="handleItemDelete">
    </workout-template-table>

    <!-- Actions -->
    <v-card-actions>
        <button class="cancel-button" @click="handleCancel">
            <div>Cancel</div>
        </button>
        <button v-if="selectedWorkout?._id" @click="addWorkout" class="submit-button">
            <div>Edit Template</div>
        </button>
        <button v-else class="submit-button" @click="addWorkout">
            <div>Create New Template</div>
        </button>
    </v-card-actions>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import ExerciseSearch from './ExerciseSearch.vue';
import WorkoutTemplateTable from './ExerciseTable.vue'; // Import the new component
import { Exercise, WorkoutTemplate, ExerciseItem } from '../../interfaces';
import { Api } from '../../interfaces/api';

export default defineComponent({
    name: 'NewWorkout',
    components: {
        ExerciseSearch,
        WorkoutTemplateTable, // Register the new component
    },
    props: {
        selectedWorkout: {
            type: Object as () => WorkoutTemplate,
            required: false,
            default: null
        },
    },
    data() {
        return {
            api: new Api(),
            selectedItems: [] as ExerciseItem[], // Store selected exercises
            name: '',
        };
    },
    watch: {
        selectedWorkout(newVal) {
            console.log("we are here", newVal)
            if (newVal.selectedItems === undefined) {
                this.selectedItems = [];
                this.name = '';
            } else {
                this.selectedItems = newVal.selectedItems;
                this.name = newVal.name;
            }
        },
    },
    methods: {
        async addWorkout() {
            try {
                const response = this.selectedWorkout?._id
                    ? await this.api.editTemplate(this.selectedWorkout._id, this.name, this.selectedItems)
                    : await this.api.addTemplate(this.name, this.selectedItems);

                if (response !== -1) {
                    console.log(response.data.message);
                }

                const workoutTemplate = { _id: response.data.workout_id, user_id: response.data.user_id, name: this.name, selectedItems: this.selectedItems } as WorkoutTemplate
                this.$emit('update-data', workoutTemplate);
            } catch (error) {
                console.error('Error trying to save data to the DB', error);
            }
        },
        deleteWorkout() {
            this.$emit('delete-workout', this.selectedWorkout?._id);
        },
        handleCancel() {
            console.log("help me pls", this.selectedWorkout)
            this.selectedItems = []
            this.name = ''
            this.$emit('cancel-edit');
        },
        handleItemSelected(item: Exercise) {
            const newItems = this.selectedItems
            const exerciseItem = { isCustom: false, exercise: item, sets: 0 }
            newItems.push(exerciseItem);
            this.selectedItems = [...newItems]

        },
        handleAddCustom(item: ExerciseItem) {
            const newItems = this.selectedItems
            newItems.push(item);
            this.selectedItems = [...newItems]
        },
        handleItemDelete(id: string) {
            this.selectedItems = this.selectedItems.filter((item) => item.exercise._id !== id);
        },
    },
});
</script>

<style scoped>
.exercise-history {
    border: solid 1px black;
    height: calc(100% - 20px);
    width: calc(100% - 20px);
    margin: 10px;
}

.icon-btn:hover div {
    color: white !important;
    z-index: 10000;
}

.icon-btn:hover .icon {
    color: white !important;
    z-index: 10000;
}

.icon-btn:hover {
    background-color: white !important;
}

.icon {
    color: white;
}

.cancel-button {
    background-color: #fcb055;
    border: solid 1px black;
    font-size: 12pt;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    width: 100px;
    margin-top: 530px;
    margin-left: 66%;
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
    background-color: #fcb055;
    border: solid 1px black;
    font-size: 12pt;
    width: 200px;
    margin-top: 530px;
}

.icon-btn {
    height: 35px;
    width: 35px;
    border: solid 1px black;
}
</style>
