<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { login } from "../api/clipboard";
import { saveToken } from "../utils/auth";

const router = useRouter();
const password = ref("");
const error = ref("");
const loading = ref(false);

const handleSubmit = async () => {
    if (!password.value) {
        error.value = "Please enter password";
        return;
    }

    loading.value = true;
    error.value = "";

    try {
        const token = await login(password.value);
        saveToken(token);
        router.push("/");
    } catch {
        error.value = "Invalid password";
        password.value = "";
    } finally {
        loading.value = false;
    }
};

const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === "Enter") {
        handleSubmit();
    }
};
</script>

<template>
    <div class="login-container">
        <div class="login-box">
            <h1 class="login-title">Clipboard</h1>
            <p class="login-subtitle">Authentication required</p>

            <div class="login-form">
                <input
                    v-model="password"
                    type="password"
                    placeholder="Enter password"
                    class="login-input"
                    :disabled="loading"
                    @keydown="handleKeydown"
                    autofocus
                />

                <div v-if="error" class="login-error">{{ error }}</div>

                <button @click="handleSubmit" class="login-button" :disabled="loading">
                    {{ loading ? "Authenticating..." : "Login" }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background-color: #fafafa;
}

.login-box {
    background: #ffffff;
    padding: 2.5rem;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    width: 100%;
    max-width: 360px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.login-title {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    text-align: center;
    color: #1a1a1a;
    letter-spacing: -0.02em;
}

.login-subtitle {
    margin: 0 0 2rem 0;
    text-align: center;
    color: #666;
    font-size: 0.875rem;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.login-input {
    padding: 0.75rem;
    font-size: 0.9375rem;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    transition: all 0.15s ease;
    font-family: inherit;
    background: #fafafa;
}

.login-input:focus {
    outline: none;
    border-color: #333;
    background: #ffffff;
}

.login-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.login-error {
    padding: 0.625rem;
    background: #fff5f5;
    color: #d32f2f;
    border-radius: 4px;
    font-size: 0.875rem;
    text-align: center;
    border: 1px solid #ffcdd2;
}

.login-button {
    padding: 0.75rem;
    font-size: 0.9375rem;
    font-weight: 500;
    color: #ffffff;
    background: #1a1a1a;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s ease;
    font-family: inherit;
}

.login-button:hover:not(:disabled) {
    background: #000000;
}

.login-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>
