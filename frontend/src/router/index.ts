import { createRouter, createWebHistory } from "vue-router";
import { isAuthenticated } from "../utils/auth";
import EditorView from "../views/EditorView.vue";
import LoginView from "../views/LoginView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "Editor",
            component: EditorView,
            meta: { requiresAuth: true },
        },
        {
            path: "/login",
            name: "Login",
            component: LoginView,
        },
    ],
});

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
    const authed = isAuthenticated();

    if (requiresAuth && !authed) {
        // Redirect to login if not authenticated
        next("/login");
    } else if (to.path === "/login" && authed) {
        // Redirect to home if already authenticated
        next("/");
    } else {
        next();
    }
});

export default router;
