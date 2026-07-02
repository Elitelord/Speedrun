<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

Speedrun: the projected MCAT readiness panel. The total (472–528) is the sum of
the four sections (each 118–132): studied sections use their projection, and
unstudied sections (including CARS, which has no flashcard topic yet) contribute
a neutral mid-section prior spanning the full section range — so the total's
range honestly widens with every section you haven't covered. It refuses to
project a total until at least half the four sections have been studied.
-->
<script lang="ts">
    import type {
        ReadinessScore,
        ReadinessScoreResponse,
    } from "@generated/anki/scheduler_pb";

    export let readiness: ReadinessScoreResponse;

    function pct(fraction: number): string {
        return `${Math.round(fraction * 100)}%`;
    }

    function title(label: string): string {
        return label ? (label.split("::").pop() ?? label) : "Overall";
    }

    // Confidence from the overall band width (narrower = more confident).
    function confidence(): string {
        const o = readiness.overall;
        if (!o) {
            return "low";
        }
        const width = o.rangeHigh - o.rangeLow;
        if (width < 0.12) {
            return "high";
        } else if (width < 0.24) {
            return "medium";
        }
        return "low";
    }

    function sectionShown(t: ReadinessScore): boolean {
        return !!t.mastery && t.mastery.shown && t.mastery.cardsWithState > 0;
    }

    // Coverage is reported as sections studied out of the four MCAT sections.
    const MCAT_SECTIONS = 4;
    function sectionsCovered(): number {
        return Math.round(readiness.coverage * MCAT_SECTIONS);
    }
</script>

<section class="group">
    <h2>Readiness</h2>
    <p class="subtitle">
        Projected MCAT total on the real 472–528 scale — the sum of the four sections,
        with a likely range that widens for sections you haven't studied yet.
    </p>

    <div class="readiness" class:shown={readiness.shown}>
        {#if readiness.shown}
            <div class="projected">
                <span class="big">{Math.round(readiness.scaledEstimate)}</span>
                <span class="scalemax">/ 528</span>
            </div>
            <div class="detail">
                Likely range {Math.round(readiness.scaledLow)}–{Math.round(
                    readiness.scaledHigh,
                )}
                · Confidence: {confidence()} · {sectionsCovered()}/{MCAT_SECTIONS} sections
                studied
            </div>
            {#if sectionsCovered() < MCAT_SECTIONS}
                <div class="detail note">
                    Includes a wide-uncertainty estimate for the {MCAT_SECTIONS -
                        sectionsCovered()} section{MCAT_SECTIONS - sectionsCovered() ===
                    1
                        ? ""
                        : "s"} you haven't studied yet.
                </div>
            {/if}
        {:else}
            <div class="giveup">No readiness score yet</div>
            <div class="detail">
                Needs ≥50% of the four MCAT sections studied. Currently {sectionsCovered()}/{MCAT_SECTIONS}
                sections · {pct(readiness.coverage)} covered.
            </div>
        {/if}
    </div>

    <div class="sections">
        {#each readiness.topics as t (t.mastery?.label)}
            <div class="section">
                <span class="label">{title(t.mastery?.label ?? "")}</span>
                {#if sectionShown(t)}
                    <span class="score">
                        {Math.round(t.scaledEstimate)}
                        <span class="range">
                            ({Math.round(t.scaledLow)}–{Math.round(t.scaledHigh)})
                        </span>
                    </span>
                {:else}
                    <span class="giveup small">not enough data</span>
                {/if}
            </div>
        {/each}
        <div class="section cars">
            <span class="label">CARS</span>
            <span class="giveup small">
                not yet available — coming with the CARS module
            </span>
        </div>
    </div>
</section>

<style lang="scss">
    .group {
        margin-bottom: 2em;
    }

    h2 {
        margin-bottom: 0.1em;
    }

    .subtitle {
        color: var(--fg-subtle);
        margin-bottom: 1em;
        font-size: 0.9em;
    }

    .readiness {
        border: 2px solid var(--border);
        border-radius: var(--border-radius, 5px);
        padding: 1em;
        margin-bottom: 0.75em;

        &.shown {
            border-color: var(--fg-link);
        }
    }

    .projected {
        display: flex;
        align-items: baseline;
        gap: 0.3em;
    }

    .big {
        font-size: 2.6em;
        line-height: 1;
        font-variant-numeric: tabular-nums;
        font-weight: bold;
    }

    .scalemax {
        color: var(--fg-subtle);
    }

    .detail {
        color: var(--fg-subtle);
        font-size: 0.9em;
        margin-top: 0.35em;

        &.note {
            font-style: italic;
            font-size: 0.82em;
        }
    }

    .giveup {
        font-style: italic;
        color: var(--fg-subtle);
        font-size: 1.2em;

        &.small {
            font-size: 0.85em;
        }
    }

    .sections {
        display: flex;
        flex-direction: column;
        gap: 0.25em;
    }

    .section {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 0.4em 1em;
        border: 1px solid var(--border);
        border-radius: var(--border-radius, 5px);
    }

    .label {
        font-weight: bold;
        text-transform: capitalize;
    }

    .score {
        font-variant-numeric: tabular-nums;
        font-size: 1.1em;
    }

    .range {
        color: var(--fg-subtle);
        font-size: 0.8em;
    }
</style>
