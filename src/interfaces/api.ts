import axios, { AxiosResponse } from "axios";
import Cookies from "js-cookie";
import { Activity, Meal, WorkoutTemplate } from ".";
import { NutritionData, NutritionItem } from ".";

export class Api {
    async login(username: string, password: string): Promise<AxiosResponse | -1> {
        try {
            const response = await axios.post("http://127.0.0.1:5000/login", {
                username,
                password,
            });

            // Set JWT token as a cookie
            Cookies.set("access_token", response.data.access_token, {
                expires: 7,
                secure: process.env.NODE_ENV === "production",
                path: "/",
            });

            return response;
        } catch (error) {
            console.error("Login error:", error);
            return -1;
        }
    }

    async logout() {
        // Delete the JWT token from cookies
        Cookies.remove("access_token");

        // Optionally, you can clear other user-related data as well

        console.log("Logged out successfully");
    }

    

    async verifyToken(): Promise<AxiosResponse | -1> {
        try {
            const response = await axios.get("http://127.0.0.1:5000/profile", {
                headers: {
                    Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                }
            });

            return response;
        } catch (error) {
            console.error("Error validating token:", error);
            return -1;
        }
    }

    async register(username: String, email: String, password: String) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/register", {
                username: username,
                email: email,
                password: password,
            });

            return response
        } catch (error) {
            console.error("Error registering user:", error);
            return -1;
        }
    }

    async garminLogin(email: String, password: String) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/login_garmin", {
                email: email,
                password: password
            }, {
                headers: {
                    Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                }
            },)

            return response
        } catch (error) {
            console.error("Error logging into Garmin:", error);
            return -1
        }
    }

    async garminSync(force: boolean) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/get_activities_from_date",
                {
                    force: force
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })

            return response
        } catch (error) {
            console.error("Error logging into Garmin:", error);
            return -1
        }
    }

    async fetchActivities() {
        try {
            const response = await axios.get("http://127.0.0.1:5000/fetch_user_activities", {
                headers: {
                    Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                }
            })
            return response
        } catch (error) {
            console.error("Error logging into Garmin:", error);
            return -1

        }
    }

    async fetchWeekGlance() {
        try {
            const response = await axios.get("http://127.0.0.1:5000/fetch_user_activities_last_week_by_category", {
                headers: {
                    Authorization: `Bearer ${Cookies.get("access_token")}`, // Send token in Authorization header
                },
            });

            return response;
        } catch (error) {
            console.error("Error fetching activities by category:", error);
            return -1;
        }
    }

    async addActivity(name: string, type: string, distance: number, duration: number, averageHR: number | null, maxHR: number | null, maxSpeed: number | null, calories: number | null) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/add_activity",
                {
                    name: name,
                    type: type,
                    distance: distance,
                    duration: duration,
                    averageHR: averageHR,
                    maxHR: maxHR,
                    maxSpeed: maxSpeed,
                    calories: calories
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })

            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async editActivity(originalID: number, name: string, type: string, distance: number, duration: number, averageHR: number | null, maxHR: number | null, maxSpeed: number | null, calories: number | null, workoutTemplate?: WorkoutTemplate, workoutData?: Object) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/edit_activity",
                {
                    activity_id: originalID,
                    name: name,
                    type: type,
                    distance: distance,
                    duration: duration,
                    averageHR: averageHR,
                    maxHR: maxHR,
                    maxSpeed: maxSpeed,
                    calories: calories,
                    workoutData: workoutData,
                    workoutTemplate: workoutTemplate
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })

            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async deleteActivity(activity_id: number) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/delete_activity",
                {
                    activity_id: activity_id,
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })

            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async fetchFoods(searchQuery: string, start_index: number) {
        try {
            const response = await axios.get('http://localhost:5000/get_nutrition', {
                params: {
                    search: searchQuery,
                    start_index: start_index,
                    limit: 20
                }
            });

            // Update the items array with the fetched data
            return response;

            return response;
        } catch (error) {
            console.error("Error fetching items from the database: ", error);
            return -1;
        }
    }

    async addMeal(name: string, totalMacros: NutritionData, selectedItems: NutritionItem[]) {
        try {
            const payload = {
                name: name,
                totalMacros: totalMacros,
                selectedItems: selectedItems
            };

            const response = await axios.post('http://localhost:5000/add_meal', payload, {
                headers: {
                    Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                }
            });

            // Return the response from the server
            return response;
        } catch (error) {
            console.error("Error adding the meal to the database: ", error);
            return -1;
        }
    }


    async fetchUserMeals({
        search = '',
        startIndex = 0,
        limit = 50,
    }: {
        search?: string;
        startIndex?: number;
        limit?: number;
    } = {}): Promise<AxiosResponse | -1> { // Added default empty object
        try {
            // Build the query string
            const queryParams = new URLSearchParams();

            if (search) queryParams.append('search', search);
            queryParams.append('start_index', startIndex.toString());
            queryParams.append('limit', limit.toString());

            // Make the request
            const response = await axios.get(`http://localhost:5000/fetch_user_meals?${queryParams.toString()}`, {
                headers: {
                    Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                },
            })

            // Return the response data
            return response;
        } catch (error) {
            console.error("Error fetching user meals: ", error);
            return -1;
        }
    }


    async editMeal(originalID: string, name: string, totalMacros: NutritionData, selectedItems: NutritionItem[]) {
        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/edit_meal",
                {
                    meal_id: originalID,      // meal ID to identify which meal to update
                    name: name,               // meal name to update
                    totalMacros: totalMacros, // the total macros object containing carbs, fats, proteins, sugars, calories
                    selectedItems: selectedItems, // the list of selected items in the meal
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Authorization header with the token
                    }
                }
            );

            return response;  // return the response object from the backend
        } catch (error) {
            console.error("Error editing the meal: ", error);
            return -1;  // return -1 in case of an error
        }
    }

    async mealsByWeek() {
        try {
            const response = await axios.get(
                "http://127.0.0.1:5000/fetch_meals_last_week",
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Authorization header with the token
                    }
                }
            );

            return response;  // return the response object from the backend
        } catch (error) {
            console.error("Error editing the meal: ", error);
            return -1;  // return -1 in case of an error

        }
    }

    async deleteMeal(_id: string) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/delete_meal",
                {
                    _id: _id
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })

            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async fetchNutritionData(granularity: string) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/fetch_nutrition_summary",
                {
                    granularity: granularity
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })


            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async fetchExercises(searchQuery: string, start_index: number) {
        try {
            const response = await axios.get('http://localhost:5000/get_exercises', {
                params: {
                    search: searchQuery,
                    start_index: start_index,
                    limit: 20
                }
            });

            // Return the fetched data
            return response;
        } catch (error) {
            console.error("Error fetching exercises from the database: ", error);
            return -1;
        }
    }

    async fetchUserActivities({
        search = '',
        startIndex = 0,
        limit = 50,
    }: {
        search?: string;
        startIndex?: number;
        limit?: number;
    } = {}): Promise<AxiosResponse | -1> { // Added default empty object
        try {
            // Build the query string
            const queryParams = new URLSearchParams();

            if (search) queryParams.append('search', search);
            queryParams.append('start_index', startIndex.toString());
            queryParams.append('limit', limit.toString());

            // Make the request
            const response = await axios.get(`http://localhost:5000/fetch_paginated_activities?${queryParams.toString()}`, {
                headers: {
                    Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                },
            });

            // Return the response data
            return response;
        } catch (error) {
            console.error("Error fetching user meals: ", error);
            return -1;
        }
    }

    async fetchActivityDetails(activityId: number) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/get_activity_details",
                {
                    activityId: activityId
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })
            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async fetchActivitySplits(activityId: number) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/get_activity_splits",
                {
                    activityId: activityId
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })
            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async editTemplate(originalID: string, name: string, selectedItems: NutritionItem[]) {
        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/edit_template",
                {
                    workout_id: originalID,      // meal ID to identify which meal to update
                    name: name,               // meal name to update
                    selectedItems: selectedItems, // the list of selected items in the meal
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Authorization header with the token
                    }
                }
            );

            return response;  // return the response object from the backend
        } catch (error) {
            console.error("Error editing the meal: ", error);
            return -1;  // return -1 in case of an error
        }
    }

    async addTemplate(name: string, selectedItems: NutritionItem[]) {
        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/add_template",
                {
                    name: name,               // meal name to update
                    selectedItems: selectedItems, // the list of selected items in the meal
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Authorization header with the token
                    }
                }
            );

            return response;  // return the response object from the backend
        } catch (error) {
            console.error("Error editing the meal: ", error);
            return -1;  // return -1 in case of an error
        }
    }

    async fetchUserTemplates({
        search = '',
        startIndex = 0,
        limit = 50,
    }: {
        search?: string;
        startIndex?: number;
        limit?: number;
    } = {}): Promise<AxiosResponse | -1> { // Added default empty object
        try {
            // Build the query string
            const queryParams = new URLSearchParams();

            if (search) queryParams.append('search', search);
            queryParams.append('start_index', startIndex.toString());
            queryParams.append('limit', limit.toString());

            // Make the request
            const response = await axios.get(`http://localhost:5000/fetch_user_workout_templates?${queryParams.toString()}`, {
                headers: {
                    Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                },
            });

            // Return the response data
            return response;
        } catch (error) {
            console.error("Error fetching user meals: ", error);
            return -1;
        }
    }

    async fetchActivitySummary(granularity: string) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/fetch_user_activities_by_category_options",
                {
                    granularity: granularity
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })


            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }

    async fetchHealthSummary(granularity: string) {
        try {
            const response = await axios.post("http://127.0.0.1:5000/get_garmin_stats_options",
                {
                    granularity: granularity
                },
                {
                    headers: {
                        Authorization: `Bearer ${Cookies.get('access_token')}`, // Send token in Authorization header
                    }
                })


            return response
        } catch (error) {
            console.error("Error posting an activity to the database: ", error);
            return -1
        }
    }
}
