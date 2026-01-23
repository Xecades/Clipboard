<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import { EditorState } from "@codemirror/state";
import { EditorView, keymap, lineNumbers } from "@codemirror/view";
import { defaultKeymap, indentWithTab } from "@codemirror/commands";

const props = defineProps<{
    modelValue: string;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: string];
    selectionChange: [stats: { selected: number; total: number }];
}>();

const editorContainer = ref<HTMLDivElement>();
let editorView: EditorView | null = null;
let isUpdatingFromExternal = false;

onMounted(() => {
    if (!editorContainer.value) return;

    const startState = EditorState.create({
        doc: props.modelValue,
        extensions: [
            lineNumbers(),
            keymap.of([...defaultKeymap, indentWithTab]),
            EditorView.updateListener.of((update) => {
                if (update.docChanged && !isUpdatingFromExternal) {
                    emit("update:modelValue", update.state.doc.toString());
                }

                if (update.selectionSet || update.docChanged) {
                    const { state } = update;
                    const selectedLength = state.selection.ranges.reduce(
                        (sum, range) => sum + range.to - range.from,
                        0,
                    );
                    const totalLength = state.doc.length;

                    emit("selectionChange", {
                        selected: selectedLength,
                        total: totalLength,
                    });
                }
            }),
            EditorView.theme({
                "&": {
                    height: "100%",
                    fontSize: "24px",
                    backgroundColor: "#ffffff",
                },
                ".cm-content": {
                    fontFamily: 'Menlo, Monaco, "Courier New", monospace',
                    padding: "8px 0",
                },
                ".cm-line": {
                    padding: "0 8px",
                },
                ".cm-gutters": {
                    backgroundColor: "#fafafa",
                    borderRight: "1px solid #e0e0e0",
                    color: "#999",
                },
                ".cm-activeLineGutter": {
                    backgroundColor: "#f0f0f0",
                },
                ".cm-lineNumbers .cm-gutterElement": {
                    padding: "0 12px 0 8px",
                    minWidth: "50px",
                },
                "&.cm-focused": {
                    outline: "none",
                },
                ".cm-cursor": {
                    borderLeftColor: "#1a1a1a",
                },
                ".cm-selectionBackground, &.cm-focused .cm-selectionBackground": {
                    backgroundColor: "#d0d0d0",
                },
            }),
        ],
    });

    editorView = new EditorView({
        state: startState,
        parent: editorContainer.value,
    });

    editorView.focus();
});

watch(
    () => props.modelValue,
    (newValue) => {
        if (editorView && editorView.state.doc.toString() !== newValue) {
            isUpdatingFromExternal = true;

            editorView.dispatch({
                changes: {
                    from: 0,
                    to: editorView.state.doc.length,
                    insert: newValue,
                },
            });

            isUpdatingFromExternal = false;
        }
    },
);

onBeforeUnmount(() => {
    if (editorView) {
        editorView.destroy();
        editorView = null;
    }
});
</script>

<template>
    <div ref="editorContainer" class="editor-container"></div>
</template>

<style scoped>
.editor-container {
    height: 100%;
    width: 100%;
}
</style>
