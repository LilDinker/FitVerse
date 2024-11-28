<template>
    <v-dialog v-model="visible" persistent max-width="400px">
        <v-card>
            <v-card-title class="headline">Confirm Action</v-card-title>
            <v-card-text>
                <p>{{ message }}</p>
            </v-card-text>
            <v-card-actions>
                <button class="cancel-button" text @click="cancel">Cancel</button>
                <button class="submit-button" @click="confirm">OK</button>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { defineComponent } from 'vue';
export default defineComponent({
    name: "ConfirmDelete",
    props: {
        message: {
            type: String,
            required: true,
        },
        value: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            visible: this.value,
        };
    },
    watch: {
        value(newVal) {
            this.visible = newVal;
        },
    },
    methods: {
        confirm() {
            this.$emit("confirmed");
            this.visible = false;
        },
        cancel() {
            this.$emit("cancelled");
            this.visible = false;
        },
    },
});
</script>

<style scoped>
.headline {
    font-weight: bold;
    font-size: 18px;
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
    background-color: rgb(156, 148, 148)
}
.submit-button:hover {
    background-color: rgb(199, 105, 105)
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