<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

Speedrun: consolidated MCAT settings — Study (interleaving / weakness weighting /
topic tags), Review (free-text grading + apply-to-any-card), and a read-only AI
status. Everything the Tools menu used to scatter, in one place.
-->
<script lang="ts">
    import { type SpeedrunSettings, saveSettings } from "./lib";

    export let settings: SpeedrunSettings;

    // Local editable copy; topic tags edited as newline/comma-separated text.
    let interleaveEnabled = settings.interleave.enabled;
    let weightByWeakness = settings.interleave.weightByWeakness;
    let topicTagsText = settings.interleave.topicTags.join("\n");
    let productionMode = settings.review.productionMode;
    let typeInDefault = settings.review.typeInDefault;

    let saving = false;
    let savedAt: string | null = null;
    let error: string | null = null;

    function parseTags(text: string): string[] {
        return text
            .split(/[\n,]/)
            .map((t) => t.trim())
            .filter((t) => t.length > 0);
    }

    async function save(): Promise<void> {
        saving = true;
        error = null;
        savedAt = null;
        try {
            const next: SpeedrunSettings = {
                interleave: {
                    enabled: interleaveEnabled,
                    weightByWeakness,
                    topicTags: parseTags(topicTagsText),
                },
                review: { productionMode, typeInDefault },
                ai: settings.ai,
            };
            await saveSettings(next);
            settings = next;
            savedAt = "Saved";
        } catch (err) {
            error = String(err);
        } finally {
            saving = false;
        }
    }
</script>

<div class="settings">
    <h1>MCAT Settings</h1>

    <section>
        <h2>Study</h2>
        <label class="row switch">
            <input type="checkbox" bind:checked={interleaveEnabled} />
            <span>
                <strong>Interleave topics</strong>
                <small>
                    Round-robin cards across your MCAT topics instead of one at a time.
                </small>
            </span>
        </label>
        <label class="row switch" class:disabled={!interleaveEnabled}>
            <input
                type="checkbox"
                bind:checked={weightByWeakness}
                disabled={!interleaveEnabled}
            />
            <span>
                <strong>Weight by weakness</strong>
                <small>Show weaker topics more often (based on measured recall).</small>
            </span>
        </label>
        <div class="row column">
            <strong>Topic tags</strong>
            <small>One tag per line. These define your MCAT sections.</small>
            <textarea rows="3" bind:value={topicTagsText}></textarea>
        </div>
    </section>

    <section>
        <h2>Review</h2>
        <label class="row switch">
            <input type="checkbox" bind:checked={productionMode} />
            <span>
                <strong>Free-text grading</strong>
                <small>
                    Type your answer and have it graded, instead of flipping a
                    flashcard.
                </small>
            </span>
        </label>
        <label class="row switch" class:disabled={!productionMode}>
            <input
                type="checkbox"
                bind:checked={typeInDefault}
                disabled={!productionMode}
            />
            <span>
                <strong>Apply to every card</strong>
                <small>
                    Use free-text grading on any card with a back field — no need to
                    change the notetype.
                </small>
            </span>
        </label>
    </section>

    <section>
        <h2>AI</h2>
        <div class="row status">
            <span>API key</span>
            <span class="badge" class:ok={settings.ai.keyDetected}>
                {settings.ai.keyDetected ? "detected" : "not detected"}
            </span>
        </div>
        <div class="row status">
            <span>Chat model</span>
            <code>{settings.ai.model}</code>
        </div>
        <div class="row status">
            <span>Embedding model</span>
            <code>{settings.ai.embedModel}</code>
        </div>
        {#if !settings.ai.keyDetected}
            <p class="hint">
                Free-text grading falls back to self-grading until an
                <code>OPENAI_API_KEY</code>
                is set in the repo-root
                <code>.env</code>
                .
            </p>
        {/if}
    </section>

    <div class="actions">
        <button class="save" on:click={save} disabled={saving}>
            {saving ? "Saving…" : "Save"}
        </button>
        {#if savedAt}<span class="ok-text">{savedAt}</span>{/if}
        {#if error}<span class="err-text">{error}</span>{/if}
    </div>
</div>

<style lang="scss">
    .settings {
        max-width: 640px;
        margin: 0 auto;
        padding: 1.25em 1.5em 2em;
    }

    h1 {
        font-size: 1.5em;
        margin-bottom: 0.5em;
    }

    section {
        margin-bottom: 1.75em;
    }

    h2 {
        font-size: 1.05em;
        margin-bottom: 0.6em;
        padding-bottom: 0.25em;
        border-bottom: 1px solid var(--border);
    }

    .row {
        padding: 0.5em 0;
    }

    .switch {
        display: flex;
        align-items: flex-start;
        gap: 0.7em;
        cursor: pointer;

        input {
            margin-top: 0.2em;
            flex-shrink: 0;
        }

        &.disabled {
            opacity: 0.5;
            cursor: default;
        }
    }

    .column {
        display: flex;
        flex-direction: column;
        gap: 0.3em;
    }

    strong {
        display: block;
    }

    small {
        color: var(--fg-subtle);
        font-size: 0.85em;
    }

    textarea {
        width: 100%;
        font-family: inherit;
        background: var(--canvas-inset, var(--canvas));
        color: inherit;
        border: 1px solid var(--border);
        border-radius: var(--border-radius, 5px);
        padding: 0.4em 0.6em;
        resize: vertical;
    }

    .status {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border);
    }

    .badge {
        font-size: 0.85em;
        padding: 0.1em 0.6em;
        border-radius: 999px;
        background: hsl(0, 72%, 51%);
        color: white;

        &.ok {
            background: hsl(145, 63%, 42%);
        }
    }

    .hint {
        color: var(--fg-subtle);
        font-size: 0.85em;
        margin-top: 0.6em;
    }

    code {
        background: var(--canvas-inset, var(--canvas));
        padding: 0.05em 0.35em;
        border-radius: 4px;
    }

    .actions {
        display: flex;
        align-items: center;
        gap: 1em;
        margin-top: 1em;
    }

    .save {
        padding: 0.5em 1.4em;
        border: none;
        border-radius: var(--border-radius, 5px);
        background: var(--fg-link);
        color: white;
        cursor: pointer;

        &:disabled {
            opacity: 0.6;
            cursor: default;
        }
    }

    .ok-text {
        color: hsl(145, 63%, 42%);
    }

    .err-text {
        color: hsl(0, 72%, 51%);
        font-size: 0.85em;
    }
</style>
