<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { server } from "@/assets/leancloud";

import type { Ref } from "vue";
import type { ViewUpdate } from "@codemirror/view";

const code: Ref<string> = ref("");
const selected: Ref<number> = ref(0);
const length: Ref<number> = ref(0);

let edited: boolean = false;
let unwatch = watch(code, () => {
    edited = true;
});

const update = (value: string) => {
    unwatch();

    code.value = value;

    unwatch = watch(code, () => {
        edited = true;
    });
};

onMounted(() => {
    const remote: Ref<string> = server.ref;

    watch(remote, (value) => {
        if (value !== code.value && !edited) {
            update(value);
        }
    });

    watch(code, (value: string) => {
        if (edited) {
            edited = false;
            server.ref = value;
        }
    });
});

const update_status = (viewUpdate: ViewUpdate) => {
    const state = viewUpdate.view.state;
    const ranges = state.selection.ranges;
    const doc = state.doc;

    selected.value = ranges.reduce((r, range) => r + range.to - range.from, 0);
    length.value = doc.length;
};
</script>

<template>
    <VueCodemirror
        v-model="code"
        @update="update_status"
        style="height: calc(100vh - 1.5rem - 1px); font-size: 1.1rem"
    />
    <div id="statusbar">{{ length }} 字符 · {{ selected }} 选中</div>
</template>

<style scoped>
#statusbar {
    user-select: none;
    height: 1.5rem;
    line-height: 1.5rem;
    background-color: #f5f5f5;
    color: #777777;
    padding-left: 0.7rem;
    font-size: 0.8rem;
    border-top: 1px solid #ddd;
    font-family: monospace;
}
</style>
