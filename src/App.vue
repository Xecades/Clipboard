<script setup>
import { onMounted, ref, watch } from "vue";
import lc from "./assets/leancloud";

const code = ref("");
const selected = ref(0);
const length = ref(0);
const delay = 1000;

let lock = false;
let edited = false;
let unwatch = () => {};

const update_code = (v) => {
    unwatch();
    code.value = v;
    unwatch = watch(code, () => { edited = true; });
};

const sync = async () => {
    if (lock) {
        console.log("Locked, skip clock cycle.");
        return;
    }
    lock = true;
    if (edited) {
        console.log("Update to cloud.");
        edited = false;
        await lc.update(code.value);
    } else {
        console.log("Sync from cloud.");
        const v = await lc.get();
        if (v !== code.value)
            update_code(v);
    }
    lock = false;
};

onMounted(async () => {
    update_code(await lc.get());
    setInterval(sync, delay);
});

const update_status = (payload) => {
    const state = payload.view.state;
    const ranges = state.selection.ranges;
    const doc = state.doc;

    selected.value = ranges.reduce((r, range) => r + range.to - range.from, 0);
    length.value = doc.length;
};
</script>

<template>
    <VueCodemirror v-model="code" @update="update_status" style="height: calc(100vh - 1.5rem - 1px); font-size: 1.1rem" />
    <div id="statusbar">
        {{ length }} 字符 · {{ selected }} 选中
    </div>
</template>

<style scoped>
#statusbar {
    user-select: none;
    height: 1.5rem;
    line-height: 1.5rem;
    background-color: #f5f5f5;
    color: #777777;
    padding-left: .7rem;
    font-size: .8rem;
    border-top: 1px solid #ddd;
    font-family: monospace;
}
</style>