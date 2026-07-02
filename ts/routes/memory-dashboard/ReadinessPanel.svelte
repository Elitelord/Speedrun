<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

Speedrun: the projected MCAT readiness panel. Shows a total on the real 472–528
scale with a likely range and the % of topics covered, plus a per-section
projection on 118–132. It refuses to project a score until there are enough
graded reviews AND at least half the topics have been studied — an honest score
that says when it doesn't know.
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
</script>

<section class="group">
    <h2>Readiness</h2>
    <p class="subtitle">
        Projected MCAT score on the real 472–528 scale, with a likely range and how much
        of the exam you've covered.
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
                · Confidence: {confidence()} · {pct(readiness.coverage)} of topics studied
            </div>
        {:else}
            <div class="giveup">No readiness score yet</div>
            <div class="detail">
                Needs ≥200 graded reviews <em>and</em>
                ≥50% of topics studied. Currently {readiness.overall?.gradedReviews ??
                    0} graded reviews · {pct(readiness.coverage)} covered.
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
