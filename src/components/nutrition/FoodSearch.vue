<template>
    <v-card class="search">
        <v-container style="padding: 0px; position: relative">
            <v-text-field style="width: 100%" density="compact" v-model="searchQuery" label="Search for a Food Item"
                @input="searchItems" outlined></v-text-field>

            <v-list class="search-list" v-if="items.length && searchQuery.length" @scroll="onScroll" style="padding-top: 0px !important">
                <div v-for="(item, index) in items" :key="index" class="list-item"
                    @click="handleClickList(item)">
                    <p>{{ item.name }}</p>
                </div>
                <v-progress-circular v-if="loading" indeterminate color="#003F7D" size="20"></v-progress-circular>
            </v-list>
        </v-container>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { NutritionData, NutritionDB, NutritionItem } from '../../interfaces';
import { Api } from '../../interfaces/api';

export default defineComponent({
    name: 'FoodSearch',
    data() {
        return {
            api: new Api(),
            searchQuery: '',
            items: [] as NutritionDB[],
            loading: false,
            startIndex: 0,
        };
    },
    methods: {
        async fetchItems() {
            this.loading = true;
            try {
                const response = await this.api.fetchFoods(this.searchQuery, this.startIndex)

                console.log(response)
                //@ts-ignore
                this.items = [...this.items, ...response.data.data];
                this.startIndex += 20;
            } catch (error) {
                console.error('Error fetching items:', error);
            } finally {
                this.loading = false;
            }
        },

        async searchItems() {
            this.items = [];
            this.startIndex = 0;
            this.fetchItems();
        },

        onScroll(event: any) {
            const bottom = event.target.scrollHeight === event.target.scrollTop + event.target.clientHeight;
            if (bottom && !this.loading) {
                this.fetchItems();
            }
        },

        handleClickList(item: NutritionDB) {
            const newItem: NutritionItem = {
                _id: item._id,
                name: item.name,
                weight: 0,
                isCustom: false,
                per100: {
                    carbs: item.carbs,
                    fats: item.fats,
                    proteins: item.proteins,
                    sugars: item.sugars,
                    calories: item.calories
                },
                total_macros: {
                    carbs: 0,
                    fats: 0,
                    proteins: 0,
                    sugars: 0,
                    calories: 0
                }
            }
            this.$emit('item-selected', newItem);
            this.searchQuery = ''
        }
    }
});
</script>

<style scoped>
.search {
    box-shadow: none;
    width: 90%;
    margin-left: 5%;
    margin-right: 5%;
    position: absolute;
    z-index: 100000000;
    padding: 0px !important;
}

.search-list {
    position: relative;
    left: 0;
    z-index: 10;
    background-color: white;
    border: 1px solid #ccc;
    height: 300px;
    overflow-y: auto;
    overflow-x: hidden;
    width: 100%;

    z-index: 100000000000000000000 !important;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}


.list-item {
    width: 100%;
    margin: 0px;
    padding: 0px;
    height: 50px;
    background-color: white;
    color: black;
    border-bottom: solid 1px black;
    display: flex;
    align-items: center;
    justify-content: center;
}

.list-item p {
    margin: 0px;
    padding: 0px;
}

.list-item:hover {
    background-color: #5B84C4 !important;;
    color: black;
}

.list-item:hover{
    color: white !important;
    z-index: 100000000000000000000000000;
}
</style>