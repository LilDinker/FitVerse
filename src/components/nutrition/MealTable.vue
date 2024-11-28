<template>
    <v-card class="table-card">
        <v-card-title style="padding: 5px; margin-top: 0px; background-color: #FF5003; color: white; border-bottom: solid 1px rgb(175, 171, 171);">
            <div style="display: flex; align-items: center; width: 100%;">
                <span style="margin-left: 10px;">Ingredient Table</span>
                <v-spacer />
                <v-btn @click="addCustom" icon small class="icon-btn"
                    style="margin-left: 10px; color: black; border: solid 1px white; color: white; background-color: #FF5003">
                    <v-tooltip activator="parent" location="top">Add Custom</v-tooltip>
                    <v-icon>mdi-plus</v-icon>
                </v-btn>
            </div>
        </v-card-title>
        <table style="width: 100%; height: 50px; border-spacing: 0px; border: solid 1px black; background-color: #FF8E00">
            <thead style="height: 25px;">
                <tr style="background-color: #FF8E00; color: white;">
                    <th style="width: 20%">Name</th>
                    <th style="width: 12%">Weight (g)</th>
                    <th>Carbs (g)</th>
                    <th>Fats (g)</th>
                    <th>Proteins (g)</th>
                    <th>Sugars (g)</th>
                    <th>Calories</th>

                    <th><v-icon size="15">mdi-delete</v-icon></th>
                </tr>
            </thead>
        </table>
        <div class="scroll-container">
            <div class="table-wrapper">
                <table>
                    <tbody>
                        <tr class="table-row" v-for="(item, index) in selectedItems" :key="index">
                            <td v-if="!item.isCustom" style="width: 20%">{{ item.name }}</td>
                            <td v-else style="width: 20%">
                                <v-text-field v-model="item.name" label="Name" type="string" min="0" density="compact"
                                    class="fixed-height-input"></v-text-field>
                            </td>
                            <td v-if="!item.isCustom" style="width: 12%">
                                <v-text-field v-model="item.weight" label="Weight" type="number" min="0"
                                    density="compact" class="fixed-height-input"
                                    @input="updateMacros(item)"></v-text-field>
                            </td>
                            <td v-else style="width: 12%">
                                <v-text-field label="N/A" type="string" density="compact" class="fixed-height-input"
                                    disabled></v-text-field>
                            </td>
                            <td v-if="!item.isCustom">{{ item.total_macros.carbs.toFixed(2) }}</td>
                            <td v-else>
                                <v-text-field v-model="item.total_macros.carbs" label="Carbs" type="number" min="0"
                                    density="compact" class="fixed-height-input"
                                    @input="item.total_macros.carbs = parseFloat(item.total_macros.carbs) || 0"></v-text-field>
                            </td>
                            <td v-if="!item.isCustom">{{ item.total_macros.fats.toFixed(2) }}</td>
                            <td v-else>
                                <v-text-field v-model="item.total_macros.fats" label="Fats" type="number" min="0"
                                    density="compact" class="fixed-height-input"
                                    @input="item.total_macros.fats = parseFloat(item.total_macros.fats) || 0"></v-text-field>
                            </td>
                            <td  v-if="!item.isCustom">{{ item.total_macros.proteins.toFixed(2) }}</td>
                            <td v-else>
                                <v-text-field v-model="item.total_macros.proteins" label="Proteins" type="number"
                                    min="0" density="compact" class="fixed-height-input"
                                    @input="item.total_macros.proteins = parseFloat(item.total_macros.proteins) || 0"></v-text-field>
                            </td>
                            <td v-if="!item.isCustom">{{ item.total_macros.sugars.toFixed(2) }}</td>
                            <td v-else>
                                <v-text-field v-model="item.total_macros.sugars" label="Sugars" type="number" min="0"
                                    density="compact" class="fixed-height-input"
                                    @input="item.total_macros.sugars = parseFloat(item.total_macros.sugars) || 0"></v-text-field>
                            </td>
                            <td v-if="!item.isCustom">{{ item.total_macros.calories.toFixed(2) }}</td>
                            <td v-else>
                                <v-text-field v-model="item.total_macros.calories" label="Calories" type="number"
                                    min="0" density="compact" class="fixed-height-input"
                                    @input="item.total_macros.calories = parseFloat(item.total_macros.calories) || 0"></v-text-field>
                            </td>
                            <td><v-btn @click="deleteItem(item._id)" style="height: 30px; width: 30px; border: solid 1px black" icon class="icon-btn-opposite"> <v-icon
                                        size="15">mdi-delete</v-icon></v-btn>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <table style="width: 100%; border-spacing: 0px; border: solid 1px black">
            <thead style="height: 40px;">
                <tr class="table-row" style="background-color: #FF8E00; color: white;">
                    <th style="width: 32%">Total</th>
                    <th>{{ totalMacros.carbs.toFixed(2) }}</th>
                    <th>{{ totalMacros.fats.toFixed(2) }}</th>
                    <th>{{ totalMacros.proteins.toFixed(2) }}</th>
                    <th>{{ totalMacros.sugars.toFixed(2) }}</th>
                    <th>{{ totalMacros.calories.toFixed(2) }}</th>

                    <th></th>
                </tr>
            </thead>
        </table>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { NutritionData, NutritionItem } from '../../interfaces'; // Adjust path as necessary

export default defineComponent({
    name: 'NewMeal',
    props: {
        selectedItems: { type: [] as NutritionItem[], required: true }, // Store selected items with weight and calculated macros
    },


    data() {
        return {
            customId: 25000,
        }
    },
    computed: {
        totalMacros(): NutritionData {
            return this.selectedItems.reduce(
                (totals, item) => {
                    totals.carbs += Number(item.total_macros.carbs);
                    totals.fats += Number(item.total_macros.fats);
                    totals.proteins += Number(item.total_macros.proteins);
                    totals.sugars += Number(item.total_macros.sugars);
                    totals.calories += Number(item.total_macros.calories);
                    return totals;
                },
                { carbs: 0, fats: 0, proteins: 0, sugars: 0, calories: 0 }
            );
        },
    },
    methods: {
        updateMacros(item: NutritionItem) {
            // Ensure weight is a positive number
            if (item.weight && item.weight > 0) {
                item.total_macros.carbs = (item.weight / 100) * item.per100.carbs;
                item.total_macros.fats = (item.weight / 100) * item.per100.fats;
                item.total_macros.proteins = (item.weight / 100) * item.per100.proteins;
                item.total_macros.sugars = (item.weight / 100) * item.per100.sugars;
                item.total_macros.calories = (item.weight / 100) * item.per100.calories;
            }
        },

        updateTotals() {

        },

        addCustom() {
            const newItem: NutritionItem = {
                _id: this.customId,
                name: '',
                weight: 0,
                isCustom: true,
                per100: {
                    carbs: 0,
                    fats: 0,
                    proteins: 0,
                    sugars: 0,
                    calories: 0
                },
                total_macros: {
                    carbs: 0,
                    fats: 0,
                    proteins: 0,
                    sugars: 0,
                    calories: 0
                }
            }
            this.customId++
            this.$emit("add-custom", newItem)
        },

        deleteItem(id: number) {
            this.$emit("delete-item", id)
        }
    },
});
</script>

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
    height: 300px;
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
