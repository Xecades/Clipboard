<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import CodeEditor from "../components/CodeEditor.vue";
import { getClipboard } from "../api/clipboard";
import { ClipboardWebSocket } from "../api/websocket";
import { getToken, clearToken } from "../utils/auth";

const router = useRouter();
const content = ref("");
const selectedChars = ref(0);
const totalChars = ref(0);
let ws: ClipboardWebSocket | null = null;
let updateTimer: number | null = null;

onMounted(async () => {
    const token = getToken();
    if (!token) {
        router.push("/login");
        return;
    }

    try {
        const initialContent = await getClipboard(token);
        content.value = initialContent;
        totalChars.value = initialContent.length;

        ws = new ClipboardWebSocket(token);
        ws.connect((newContent) => {
            if (newContent !== content.value) {
                content.value = newContent;
            }
        });
    } catch (error) {
        console.error("Failed to load clipboard:", error);
        clearToken();
        router.push("/login");
    }
});

onBeforeUnmount(() => {
    if (ws) {
        ws.disconnect();
    }
    if (updateTimer !== null) {
        clearTimeout(updateTimer);
    }
});

const handleContentUpdate = (newContent: string) => {
    content.value = newContent;

    if (updateTimer !== null) {
        clearTimeout(updateTimer);
    }

    updateTimer = window.setTimeout(() => {
        if (ws) {
            ws.send(newContent);
        }
        updateTimer = null;
    }, 200);
};

const handleSelectionChange = (stats: { selected: number; total: number }) => {
    selectedChars.value = stats.selected;
    totalChars.value = stats.total;
};

const handleLogout = () => {
    clearToken();
    if (ws) {
        ws.disconnect();
    }
    router.push("/login");
};
</script>

<template>
    <div class="editor-layout">
        <div class="editor-wrapper">
            <CodeEditor
                :model-value="content"
                @update:model-value="handleContentUpdate"
                @selection-change="handleSelectionChange"
            />
        </div>
        <div class="statusbar">
            <div class="statusbar-left">
                <span class="statusbar-item">{{ totalChars }} characters</span>
                <span v-if="selectedChars > 0" class="statusbar-item"
                    >{{ selectedChars }} selected</span
                >
            </div>
            <div class="statusbar-right">
                <button @click="handleLogout" class="logout-btn">
                    <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                    Logout
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.editor-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
    background: #ffffff;
}

.editor-wrapper {
    flex: 1;
    overflow: hidden;
    border-bottom: 1px solid #e0e0e0;
}

.statusbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 32px;
    background-color: #fafafa;
    border-top: 1px solid #e0e0e0;
    padding: 0 12px;
    font-size: 12px;
    color: #666;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    user-select: none;
}

.statusbar-left {
    display: flex;
    gap: 16px;
    align-items: center;
}

.statusbar-item {
    display: inline-block;
}

.statusbar-right {
    display: flex;
    align-items: center;
}

.logout-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    font-size: 12px;
    color: #666;
    background: transparent;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s ease;
    font-family: inherit;
}

.logout-btn:hover {
    color: #1a1a1a;
    border-color: #999;
    background: #f0f0f0;
}

.logout-btn svg {
    width: 14px;
    height: 14px;
}
</style>
