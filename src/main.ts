import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import axios from 'axios';
import { createVuetify } from 'vuetify';
import '@mdi/font/css/materialdesignicons.css'; // Import MDI CSS
import router from './router';

const app = createApp(App)

axios.defaults.baseURL = 'http://127.0.0.1:5000';

app.config.globalProperties.$axios = axios;

const vuetify = createVuetify({
  theme: {
    defaultTheme: "dark"
  },
  icons: {
    defaultSet: 'mdi', // Set default icon set to 'mdi'
  },
}
);

app.use(vuetify);

app.use(router);  // Use the router
app.mount('#app');

