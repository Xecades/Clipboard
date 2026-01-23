/**
 * API client for clipboard service.
 */

const API_BASE = import.meta.env.DEV ? "http://localhost:8000/api" : "/api";

export interface LoginResponse {
    token: string;
}

export interface ClipboardData {
    content: string;
}

/**
 * Login with password and get JWT token.
 */
export async function login(password: string): Promise<string> {
    const response = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ password }),
    });

    if (!response.ok) {
        throw new Error("Invalid password");
    }

    const data: LoginResponse = await response.json();
    return data.token;
}

/**
 * Get current clipboard content.
 */
export async function getClipboard(token: string): Promise<string> {
    const response = await fetch(`${API_BASE}/clipboard`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error("Failed to fetch clipboard");
    }

    const data: ClipboardData = await response.json();
    return data.content;
}

/**
 * Update clipboard content.
 */
export async function updateClipboard(token: string, content: string): Promise<void> {
    const response = await fetch(`${API_BASE}/clipboard`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
    });

    if (!response.ok) {
        throw new Error("Failed to update clipboard");
    }
}
