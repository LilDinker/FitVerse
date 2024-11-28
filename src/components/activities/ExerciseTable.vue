<template>
    <v-card class="table-card">
        <v-card-title
            style="padding: 5px; margin-top: 0px; background-color: #003F7D; color: white; border-bottom: solid 1px rgb(175, 171, 171);">
            <div style="display: flex; align-items: center; width: 100%;">
                <span style="margin-left: 10px;">Workout Template Table</span>
                <v-spacer />
                <v-btn @click="addCustom" icon small class="icon-btn"
                    style="margin-left: 10px; color: white; border: solid 1px white; background-color: #003F7D">
                    <v-tooltip activator="parent" location="top">Add Exercise</v-tooltip>
                    <v-icon>mdi-plus</v-icon>
                </v-btn>
            </div>
        </v-card-title>
        <table
            style="width: 100%; height: 50px; border-spacing: 0px; border: solid 1px black; background-color: #7986cb">
            <thead style="height: 25px;">
                <tr style="background-color: #5B84C4; color: black;">
                    <th style="width: 30%">Exercise Title</th>
                    <th style="width: 20%">Body Part</th>
                    <th style="width: 15%">Level</th>
                    <th style="width: 15%">Sets</th>
                    <th style="width: 5%"><v-icon size="15">mdi-delete</v-icon></th>
                </tr>
            </thead>
        </table>
        <div class="scroll-container">
            <div class="table-wrapper">
                <table>
                    <tbody>
                        <tr class="table-row" v-for="(item, index) in localItems" :key="index">
                            <td v-if="!item.isCustom" style="width: 30%">{{ item.exercise.title }}</td>
                            <td v-else style="width: 30%">
                                <v-text-field v-model="item.exercise.title" label="Title" type="string" min="0"
                                    density="compact" class="fixed-height-input"></v-text-field>
                            </td>
                            <td v-if="!item.isCustom" style="width: 20%">{{ item.exercise.body_part }}</td>
                            <td v-else style="width: 20%">
                                <v-text-field v-model="item.exercise.body_part" label="Name" type="string" min="0"
                                    density="compact" class="fixed-height-input"></v-text-field>
                            </td>
                            <td v-if="!item.isCustom" style="width: 15%">{{ item.exercise.level }}</td>
                            <td v-else style="width: 15%">
                                <v-text-field label="N/A" type="string" density="compact" class="fixed-height-input"
                                    disabled></v-text-field>
                            </td>
                            <td style="width: 15%">
                                <v-text-field v-model="item.sets" label="Sets" type="number" min="0" density="compact"
                                    class="fixed-height-input"
                                    @input="item.sets = parseInt(item.sets, 10) || 0"></v-text-field>
                            </td>
                            <td style="width: 5%">
                                <v-btn @click="deleteItem(item.exercise._id)"
                                    style="height: 30px; width: 30px; border: solid 1px black" icon
                                    class="icon-btn-opposite">
                                    <v-icon size="15">mdi-delete</v-icon>
                                </v-btn>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <!-- <table style="width: 100%; border-spacing: 0px; border: solid 1px black">
            <thead style="height: 40px;">
                <tr class="table-row" style="background-color: #7986cb; color: white;">
                    <th style="width: 30%">Total Exercises</th>
                    <th>{{ exerciseItems.length }}</th>
                    <th></th>
                    <th></th>
                    <th></th>
                </tr>
            </thead>
        </table> -->
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { ExerciseItem, Exercise } from '../../interfaces'; // Adjust path as necessary

export default defineComponent({
    name: 'WorkoutTemplateTable',
    props: {
        exerciseItems: { type: Array as () => ExerciseItem[], required: true }, // Store exercise items
    },
    data() {
        return {
            localItems: [] as ExerciseItem[],
            localId: 80000000
        }
    },
    methods: {
        addCustom() {
            const newItem: ExerciseItem = {
                isCustom: true,
                exercise: { _id: String(this.localId), title: '', desc: '', type: '', body_part: '', equipment: '', level: '' },
                sets: 0,
            };

            console.log(newItem)

            this.localId = this.localId + 1

            this.$emit('add-custom', newItem);
        },
        deleteItem(id: string) {
            this.$emit('delete-item', id);
        },
    },

    watch: {
        exerciseItems(newVal) {
            this.localItems = Object.values(newVal)
            console.log(this.localItems)
        }
    }
});
</script>

<style scoped>
/* Add similar styles as in your previous table */
</style>


<style scoped>
.table-row {
    height: 25px !important;
    /* Enforce fixed height for the row */
    display: table-row;
    vertical-align: middle;
}

.table-row td,
.table-row th {
    height: 25px !important;
    /* Fixed height for table cells */
    vertical-align: middle;
    /* Vertically center content */
    padding: 0 !important;

    border: solid 1px black;
    margin: 0px;
    /* Remove padding from table cells */
}

table {
    table-layout: fixed;
    /* Fix column widths */
    width: 100%;
    border-spacing: 0px !important;
}

td {
    overflow: hidden;
    /* Prevent overflow inside cells */
}

.fixed-height-input .v-input__control {
    height: 25px !important;
    /* Set fixed height for input control */
}

.fixed-height-input .v-input__slot {
    height: 25px !important;
    /* Set height for input slot */
    display: flex;
    align-items: center;
    /* Center content vertically */
}

.fixed-height-input .v-text-field__details {
    display: none !important;
}

.fixed-height-input .v-text-field__input {
    height: 25px !important;
    /* Ensure the text field input respects the row height */
    line-height: 25px !important;
    /* Vertically center the text inside input */
}

.table-card {
    border: solid 1px black;
    box-shadow: none;
    width: 90%;
    margin-left: 5%;
    margin-right: 5%;
    margin-top: 10px;
    position: absolute;
    z-index: 10;
    margin-top: 80px;
}

.icon-btn:hover .v-icon {
    color: black !important;
    z-index: 10000;
}

.icon-btn {
    width: 40px;
    height: 40px;
}

.icon-btn-opposite:hover .v-icon {
    color: white !important;
    z-index: 10000;
}

.icon-btn-opposite {
    width: 40px;
    height: 40px;
}

.scroll-container {
    width: calc(100% + 8px);
    height: 350px;
    /* Adjust to your preferred height */
    overflow-y: auto;
    position: relative;
    overflow-x: hidden;
    scrollbar-gutter: stable;
    z-index: 1000;
    /* Ensures the scroll does not interfere */
}

.scroll-container::-webkit-scrollbar {
    width: 8px;
    z-index: 10000
        /* Width of the scrollbar */
}

.scroll-container::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.5);
    /* Scrollbar color */
    border-radius: 4px;
    z-index: 10000
}


.scroll-container::-webkit-scrollbar-thumb:hover {
    background-color: rgba(255, 255, 255, 0.8);
    /* Hover effect for scrollbar */
    z-index: 10000
}

.scroll-container::-webkit-scrollbar-track {
    background-color: transparent;
    z-index: 10000
        /* Transparent track */
}

.table-wrapper {
    display: block;
    width: calc(100%);
    /* Compensates for scrollbar width */
    overflow-x: hidden
        /* Ensures no clipping due to scrollbar */
}
</style>
