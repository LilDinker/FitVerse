<template>
    <ConfirmDelete theme="light" :message="'Are you sure you want to delete this meal?'" v-model="showDialog"
        @confirmed="deleteMeal" @cancelled="showDialog = false" />
    <v-card class="nutrition-history" theme="light">
        <v-card-title style="background-color: #003F7D; color: white; display: flex;" v-if="selectedMeal?._id">
            <div>Edit Meal</div> <v-spacer v-if="selectedMeal?._id"></v-spacer>
            <v-btn theme="dark" @click="showDialog = true" icon v-if="selectedMeal?._id" small class="icon-btn"
                style="margin-right: 10px; background-color: #003F7D; border-color: white">
                <v-tooltip activator="parent" location="top">Delete Meal</v-tooltip>
                <v-icon class="icon" size="18">mdi-delete</v-icon>
            </v-btn>
        </v-card-title>
        <v-card-title
            style="background-color: #003F7D; color: white; height: 51px; padding: 0px; padding-left: 10px; display: flex; align-items: center;"
            v-else>
            <div>New Meal</div>
        </v-card-title>
        <v-text-field style="width: 90%; margin-right: 5%; margin-top: 5px; margin-left: 5%; margin-bottom: 20px"
            label="Meal Name" density="compact" v-model="name"></v-text-field>
        <v-container style="padding: 0px;">
            <!-- Food Search Section -->
            <food-search @item-selected="handleItemSelected"></food-search>

            <!-- Meal Table Section -->
            <meal-table :selectedItems="selectedItems" @add-custom="handleItemSelected"
                @delete-item="handleItemDelete"></meal-table>
        </v-container>
        <v-card-actions>
            <v-btn style="margin-top: 535px; margin-left: 80%" class="icon-btn" @click="handleCancel">
                <div>Cancel</div>
            </v-btn>
            <v-btn style="margin-top: 535px;" class="icon-btn" @click="addMeal">
                <div>Submit</div>
            </v-btn>
        </v-card-actions>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import FoodSearch from './FoodSearch.vue';
import MealTable from './MealTable.vue';
import { NutritionItem, NutritionData, Meal } from '../../interfaces';
import { Api } from '../../interfaces/api';
import ConfirmDelete from '../activities/ConfirmDelete.vue';

export default defineComponent({
    name: 'NewMeal',
    components: {
        FoodSearch,
        MealTable,
        ConfirmDelete
    },
    props: {
        selectedMeal: {
            type: Object as () => Meal
        }
    },
    data() {
        return {
            api: new Api(),
            selectedItems: [] as NutritionItem[],
            name: '',
            showDialog: false
        };
    },

    watch: {
        selectedMeal(newVal) {
            if (newVal.selectedItems == undefined) {
                this.selectedItems = [] as NutritionItem[];
                this.name = '';
            } else {
                this.selectedItems = newVal.selectedItems;
                this.name = newVal.name
            }
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
        async addMeal() {
            if (this.selectedMeal._id == undefined) {
                try {
                    const response = await this.api.addMeal(this.name, this.totalMacros, this.selectedItems)

                    if (response != -1) {
                        console.log(response.data.message)
                    }
                    this.$emit("update-data")
                } catch (error) {
                    console.error("Error trying to add data to DB", error)
                }
            } else {
                try {
                    const response = await this.api.editMeal(this.selectedMeal._id, this.name, this.totalMacros, this.selectedItems)

                    if (response != -1) {
                        console.log(response.data.message)
                    }
                    this.$emit("update-data")
                } catch (error) {
                    console.error("Error trying to edit data in DB", error)
                }
            }
        },

        deleteMeal() {
            this.$emit("delete-meal", this.selectedMeal?._id)
            this.showDialog = false
        },
        handleCancel() {
            this.$emit("cancel-edit")
        },
        handleItemSelected(item: NutritionItem) {
            const existingItem = this.selectedItems.find((i) => i._id === item._id);

            if (!existingItem) {
                this.selectedItems.push(item);
            }
        },

        handleItemDelete(id: number) {
            const index = this.selectedItems.findIndex((i) => i._id === id);

            if (index !== -1) {
                this.selectedItems.splice(index, 1); // Removes the item at the specified index
            }
        }
    }
});
</script>

<style scoped>
.nutrition-history {
    border: solid 1px black;
    height: calc(100% - 20px);
    width: calc(100% - 20px);
    margin: 10px;

}

.icon-btn:hover div {
    color: black !important;
    z-index: 10000;
}

.icon-btn:hover .icon {
    color: black !important;
    z-index: 10000;
}

.icon {
    color: white;
}

.icon-btn {
    height: 35px;
    width: 35px;
    border: solid 1px black;
}
</style>