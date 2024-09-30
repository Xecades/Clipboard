import { createApp } from "vue";
import { basicSetup } from "codemirror";
import VueCodemirror from "vue-codemirror";

import App from "./App.vue";

import "@/assets/style.css";
import lc from "@/assets/leancloud";

lc.init();

const app = createApp(App);
app.use(VueCodemirror, {
    autofocus: true,
    disabled: false,
    indentWithTab: true,
    tabSize: 4,
    extensions: [basicSetup],
});
app.mount("#app");
