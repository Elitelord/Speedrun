// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
//
// Speedrun: consolidated MCAT settings. Talks to the JSON post-handlers
// speedrunGetSettings / speedrunSetSettings (in qt/aqt/mediasrv.py) rather than
// a protobuf RPC, so a new setting needs no .proto/Rust rebuild.

export interface SpeedrunSettings {
    interleave: {
        enabled: boolean;
        weightByWeakness: boolean;
        topicTags: string[];
    };
    review: {
        productionMode: boolean;
        typeInDefault: boolean;
    };
    ai: {
        keyDetected: boolean;
        model: string;
        embedModel: string;
    };
}

async function postJson(method: string, body?: unknown): Promise<Uint8Array> {
    const res = await fetch(`/_anki/${method}`, {
        method: "POST",
        headers: { "Content-Type": "application/binary" },
        body: body === undefined
            ? new Uint8Array()
            : new TextEncoder().encode(JSON.stringify(body)),
    });
    if (!res.ok) {
        throw new Error(`${res.status}: ${await res.text()}`);
    }
    return new Uint8Array(await res.arrayBuffer());
}

export async function getSettings(): Promise<SpeedrunSettings> {
    const bytes = await postJson("speedrunGetSettings");
    return JSON.parse(new TextDecoder().decode(bytes)) as SpeedrunSettings;
}

export async function saveSettings(settings: SpeedrunSettings): Promise<void> {
    await postJson("speedrunSetSettings", settings);
}
