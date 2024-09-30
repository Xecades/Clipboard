import AV from "leancloud-storage/live-query";
import { ref, type Ref } from "vue";

const className = "Data";
const key = "content";
const objectId = "66082a9b85c7b8245b2ddcf3";

class Server {
    private _ref?: Ref<string>;

    constructor() {
        AV.init({
            appId: import.meta.env.VITE_APP_ID,
            appKey: import.meta.env.VITE_APP_KEY,
            serverURL: import.meta.env.VITE_SERVER_URL,
        });
    }

    get ref(): Ref<string> {
        if (this._ref === undefined) {
            this._ref = ref("");

            const query = new AV.Query(className);

            query.subscribe().then((live) => {
                live.on("update", (updated) => {
                    this._ref!.value = updated!.get(key);
                });
            });

            query.get(objectId).then((item) => {
                this._ref!.value = item.get(key);
            });
        }

        return this._ref;
    }

    set ref(value: string) {
        let item = AV.Object.createWithoutData(className, objectId);
        item.set(key, value);
        item.save();
    }
}

export const server = new Server();
