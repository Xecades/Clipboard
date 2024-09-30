import { createApp } from "vue";
import { basicSetup } from "codemirror";
import VueCodemirror from "vue-codemirror";

import App from "./App.vue";

import "@/assets/style.css";

createApp(App)
    .use(VueCodemirror, {
        autofocus: true,
        disabled: false,
        indentWithTab: true,
        tabSize: 4,
        extensions: [basicSetup],
    })
    .mount("#app");
