<template>
    <v-card theme="light" class="page">
        <v-card theme="light" class="welcome-card">
            <v-card-title class="welcome-title">
                Welcome to FitVerse!
            </v-card-title>
            <v-card-text class="welcome-text">
                FitVerse is your one-stop shop for fitness! Easily track and visualize all aspects of your health. Log
                in or create an account to get started!
            </v-card-text>
        </v-card>

        <v-card class="login-form">
            <v-card-title>{{ activeTab === 0 ? 'Login' : 'Register' }}</v-card-title>
            <v-tabs v-model="activeTab">
                <v-tab style="width: 50%; border-right: solid 1px black" class="hover-black">
                    <p>Login</p>
                </v-tab>
                <v-tab style="width: 50%" class="hover-black">
                    <p>Register</p>
                </v-tab>
            </v-tabs>

            <v-card-text v-if="activeTab == 0">
                <v-form ref="loginForm">
                    <v-text-field :rules="[required]" v-model="loginData.username" label="Username" outlined
                        style="background-color: transparent;color: black; margin-top: 10px" required></v-text-field>

                    <v-text-field @keydown.enter="submitLoginForm" style="background-color: transparent;color: black; margin-top: 10px"
                        :rules="[required]" v-model="loginData.password" label="Password" outlined required
                        type="password"></v-text-field>
                </v-form>
            </v-card-text>
            <v-card-text v-else>
                <v-form ref="registerForm">
                    <v-text-field :rules="[required]" v-model="registerData.username" label="Username" outlined
                        required style="background-color: transparent;color: black; margin-top: 10px"></v-text-field>

                    <v-text-field :rules="[required]" v-model="registerData.email" label="Email" outlined required
                        type="email" style="background-color: transparent;color: black; margin-top: 10px"></v-text-field>

                    <v-text-field @keydown.enter="submitRegisterForm" :rules="[required]"
                        v-model="registerData.password" label="Password" outlined required
                        type="password" style="background-color: transparent;color: black; margin-top: 10px"></v-text-field>
                </v-form>
            </v-card-text>

            <v-card-actions v-if="activeTab == 0" class="login-buttons">
                <button style="height: 50px" text @click="submitLoginForm" class="cancel-button">
                    <p>Cancel</p>
                </button>
                <button style="height: 50px" color="primary" @click="resetLoginForm" class="submit-button">
                    <p>Submit</p>
                </button>
            </v-card-actions>
            <v-card-actions v-else class="login-buttons">
                <button style="height: 50px" text @click="resetRegisterForm" class="cancel-button">
                    <p>Cancel</p>
                </button>
                <button style="height: 50px" color="primary" @click="submitRegisterForm" class="submit-button">
                    <p>Submit</p>
                </button>
            </v-card-actions>
        </v-card>

    </v-card>
</template>

<script>
import { defineComponent, ref } from "vue";
import axios from "axios";
import { createRouter } from "vue-router";
import Cookies from 'js-cookie';
import { Api } from "../interfaces/api.ts"

export default defineComponent({
    name: "Login",

    data() {
        return {
            activeTab: 0,
            loginData: {
                username: "",
                password: "",
            },
            registerData: {
                username: "",
                email: "",
                password: "",
            },
            api: new Api()
        }
    },

    methods: {
        async submitLoginForm() {
            const response = await this.api.login(this.loginData.username, this.loginData.password)
            await this.verifyToken();
            this.resetLoginForm()
        },

        async verifyToken() {
            // Verify JWT token by calling a protected route like /profile
            const profileResponse = await this.api.verifyToken()

            // If token is valid, redirect to /home otherwise do something
            if (profileResponse == -1) {
                Cookies.remove('access_token')
                // TODO: handle failed login
            } else if (profileResponse.data.authenticated) {
                this.$router.push('/home');  // Redirect to /home
            } else {
                Cookies.remove('access_token')
                // TODO: handle failed login
            }

        },

        async submitRegisterForm() {
            const registerResponse = await this.api.register(this.registerData.username, this.registerData.email, this.registerData.password)

            console.log(registerResponse)
            if (registerResponse == -1) {
                // TODO: handle failed registration
            } else if (registerResponse.status == 201) {
                alert("Account created successfully! Logging you in...")
                this.loginData.username = this.registerData.username
                this.loginData.password = this.registerData.password
                await this.submitLoginForm()
            } else {
                console.log("some other status: ", registerResponse)
                // TODO: handle failed registration
            }

            this.resetRegisterForm()
        },

        resetLoginForm() {
            this.loginData.username = "";
            this.loginData.password = "";
        },

        resetRegisterForm() {
            this.registerData.username = "";
            this.registerData.email = "";
            this.registerData.password = "";
        },
        required(v) {
            return !!v || 'Field is required'
        },
    },
})
</script>

<style scoped>
.welcome-card {
    max-width: 400px;
    margin: 50px auto;
    margin-top: 0px;
    padding: 20px;
    background-color: #003F7D;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    text-align: center;
    color: #f5f5f5;
}

.welcome-title {
    font-size: 28px;
    font-weight: bold;
    background-color: #003F7D;
    color: white;
    margin-bottom: 15px;
}

.welcome-text {
    font-size: 16px;
    line-height: 1.6;
    color: #e0e0e0;
}

.login-form {
    margin-top: 20px;
    color: white;
    background-color: #5B84C4;
    border: 1px solid black;
    width: 50%;
    max-width: 500px;
}

.login-buttons {
    justify-content: center;
    padding: 5px;
    margin: 0px;
}

.hover-black {
    justify-content: center;
}

.hover-black:hover .v-icon,
.hover-black:hover p {
    color: black !important;
    z-index: 10000;
}


.page {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: calc(100vh - 64px);
    /* Full viewport height */
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    border-radius: 0px;
}

.cancel-button {
    background-color: transparent;
    border: solid 1px black;
    font-size: 12pt;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    width: 100px;
}

.cancel-button:hover {
    background-color: rgb(199, 105, 105)
}
.submit-button:hover {
    background-color: rgb(92, 173, 92)
}

.submit-button {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    background-color: transparent;
    border: solid 1px black;
    font-size: 12pt;
    width: 100px;
}
</style>