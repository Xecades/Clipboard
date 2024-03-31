import AV from "leancloud-storage";

const className = "Data";
const key = "content";
const objectId = "66082a9b85c7b8245b2ddcf3";

async function get() {
    let query = new AV.Query(className);
    let item = await query.get(objectId);
    return item.toJSON()[key];
}

async function update(data) {
    let item = AV.Object.createWithoutData(className, objectId);
    item.set(key, data);
    await item.save();
}

function init() {
    let env = import.meta.env ?? process.env;
    AV.init({
        appId: env.VITE_APP_ID,
        appKey: env.VITE_APP_KEY,
        serverURL: env.VITE_SERVER_URL,
    });
}

const lc = {
    AV,
    init,
    get,
    update,
};

export default lc;
