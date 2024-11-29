<template>
    <v-card>
        <v-card-title>Link Your Garmin Account</v-card-title>
        <v-card-text>
            <v-form ref="loginForm">
                <v-text-field :rules="[required]" v-model="garminData.email" label="Email" outlined
                    style="background-color: transparent;" required></v-text-field>

                <v-text-field @keydown.enter="submitLoginForm" :rules="[required]" v-model="garminData.password"
                    label="Password" outlined required type="password"></v-text-field>
            </v-form>
        </v-card-text>
        <v-card-actions>
            <v-btn @click="$emit('close-login')">Cancel</v-btn>
            <v-btn @click="submitLoginForm">Submit</v-btn>
        </v-card-actions>
    </v-card>

</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Api } from '../interfaces/api';

export default defineComponent({
    name: "GarminConnect",

    data() {
        return {
            api: new Api(),
            garminData: {
                email: "",
                password: "",
            },
        }
    },

    methods: {
        async submitLoginForm() {
            const response = await this.api.garminLogin(this.garminData.email, this.garminData.password)
            this.resetLoginForm()

            if (response == -1) {
                //TODO: handle failure
                alert(
                    "Failed to connect to Garmin. Confirm your username and password, or try again later!"
                )
            } else {
                alert ("Successfully logged in!")
            }
        },

        resetLoginForm() {
            this.garminData.email = "";
            this.garminData.password = "";
        },
        required(v: any) {
            return !!v || 'Field is required'
        },
    }
})

</script>

<style></style>