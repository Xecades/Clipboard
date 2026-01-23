/**
 * Authentication utilities for token management.
 */

const TOKEN_KEY = "clipboard_token";

/**
 * Save JWT token to localStorage.
 */
export function saveToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Get JWT token from localStorage.
 */
export function getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Remove JWT token from localStorage.
 */
export function clearToken(): void {
    localStorage.removeItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
    return getToken() !== null;
}
