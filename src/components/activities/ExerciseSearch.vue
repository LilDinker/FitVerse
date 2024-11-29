<template>
    <v-card class="search">
        <v-container style="padding: 0px; position: relative;  background-color: #fcb055; ;">
            <v-text-field
                style="width: 100%"
                density="compact"
                v-model="searchQuery"
                label="Search for an Exercise"
                @input="searchItems"
                outlined
            ></v-text-field>

            <v-list
                class="search-list"
                v-if="items.length && searchQuery.length"
                @scroll="onScroll"
                style="padding-top: 0px !important"
            >
                <div
                    v-for="(item, index) in items"
                    :key="index"
                    class="list-item"
                    @click="handleClickList(item)"
                >
                    <p>{{ item.title }}</p>
                </div>
                <v-progress-circular
                    v-if="loading"
                    indeterminate
                    color="#003F7D"
                    size="20"
                ></v-progress-circular>
            </v-list>
        </v-container>
    </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Exercise } from '../../interfaces';
import { Api } from '../../interfaces/api';

export default defineComponent({
    name: 'ExerciseSearch',
    data() {
        return {
            api: new Api(),
            searchQuery: '',
            items: [] as Exercise[],
            loading: false,
            startIndex: 0,
        };
    },
    methods: {
        async fetchItems() {
            this.loading = true;
            try {
                const response = await this.api.fetchExercises(this.searchQuery, this.startIndex);

                console.log(response);
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

        handleClickList(item: Exercise) {
            const newItem: Exercise = {
                _id: item._id,
                title: item.title,
                desc: item.desc,
                type: item.type,
                body_part: item.body_part,
                equipment: item.equipment,
                level: item.level,
            };
            this.$emit('item-selected', newItem);
            this.searchQuery = '';
        },
    },
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
    background-color: #5B84C4 !important;
    color: black;
}

.list-item:hover {
    color: white !important;
    z-index: 100000000000000000000000000;
}
</style>
