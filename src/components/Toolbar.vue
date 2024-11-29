<template>
    <v-toolbar class="toolbar">
        <v-btn class="hover-black" icon>
            <v-icon>mdi-menu</v-icon>
        </v-btn>

        <v-toolbar-title class="custom-title">
            FitVerse
        </v-toolbar-title>

        <v-spacer></v-spacer>
        <v-toolbar-items>
            <v-btn @click="goToHome" class="hover-black">
                <p>Home</p>
            </v-btn>
            <v-btn @click="goToActivities" class="hover-black">
                <p>Activities</p>
            </v-btn>
            <v-btn @click="goToNutrition" class="hover-black">
                <p>Nutrition</p>
            </v-btn>
            <v-btn @click="logout" class="hover-black">
                <v-tooltip activator="parent" location="left">Logout</v-tooltip>
                <v-icon class="icon">mdi-logout</v-icon>
            </v-btn>
        </v-toolbar-items>
    </v-toolbar>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Api } from '../interfaces/api';

export default defineComponent({
    name: "Toolbar",

    methods: {
        async goToHome() {
            try {
                const response = await this.api.verifyToken()
                if (response == -1 || !response.data.authenticated) {
                    this.$router.push('/')
                } else {
                    this.$router.push("/home")
                }
            } catch (error) {
                console.error("Error trying to verify token: ", error)
            }
        },
        async goToActivities() {
            try {
                const response = await this.api.verifyToken()
                if (response == -1 || !response.data.authenticated) {
                    this.$router.push('/')
                } else {
                    this.$router.push("/activities")
                }
            } catch (error) {
                console.error("Error trying to verify token: ", error)
            }
        },
        async goToNutrition() {
            try {
                const response = await this.api.verifyToken()
                if (response == -1 || !response.data.authenticated) {
                    this.$router.push('/')
                } else {
                    this.$router.push("/nutrition")
                }
            } catch (error) {
                console.error("Error trying to verify token: ", error)
            }
        },
        async logout() {
            await this.api.logout()
            this.$router.push("/")
        }
    },

    data() {
        return {
            api: new Api()
        }
    }
})
</script>

<style scoped>
.toolbar {
    max-width: calc(100vw - 10px);
    padding-left: 5px;
    padding-right: 5px;
    background-color: #003F7D;
}

.hover-black {
    --v-hover-overlay: #FFFFFF;
}

.hover-black:hover .v-icon,
.hover-black:hover p {
    color: black !important;
    z-index: 10000;
}

.custom-title {
    width: 100px;
    text-align: center;
    height: 100%;
    display: flex;
    /* justify-content: center; */
    align-items: center;
    /* margin: 0px; */
    /* padding: 0px; */
    font-size: 25pt;
    margin-bottom: 5px;
    text-align: left;
}
</style>