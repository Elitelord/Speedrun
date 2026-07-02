<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

Speedrun: a reusable "honest score" panel. Renders an overall row plus a row per
MCAT topic, each a point estimate (0..1) with an uncertainty range; below the
give-up threshold it refuses to show a number rather than guess. Shared by the
Memory and Performance sections of the readiness dashboard.
-->
<script lang="ts">
    import type {
        MemoryScore,
        MemoryScoreResponse,
    } from "@generated/anki/scheduler_pb";

    export let heading: string;
    export let subtitle: string;
    export let score: MemoryScoreResponse;

    $: rows = [score.overall, ...score.topics].filter(
        (s): s is MemoryScore => s !== undefined,
    );

    function pct(fraction: number): string {
        return `${Math.round(fraction * 100)}%`;
    }

    function bandHalfWidth(s: MemoryScore): string {
        return `±${Math.round(((s.rangeHigh - s.rangeLow) / 2) * 100)}%`;
    }

    function lastUpdated(secs: bigint): string {
        const n = Number(secs);
        return n ? new Date(n * 1000).toLocaleDateString() : "never reviewed";
    }

    function title(label: string): string {
        // Overall score has an empty label; topics are tags like mcat::chemphys.
        return label ? (label.split("::").pop() ?? label) : "Overall";
    }

    // A number is only trustworthy if we have both enough graded reviews
    // (give-up rule) and at least one card with an FSRS memory state.
    function hasEstimate(s: MemoryScore): boolean {
        return s.shown && s.cardsWithState > 0;
    }

    // Colour by strength, so weaker topics stand out at a glance.
    function strengthColor(estimate: number): string {
        if (estimate >= 0.85) {
            return "hsl(145, 63%, 42%)";
        } else if (estimate >= 0.65) {
            return "hsl(38, 92%, 50%)";
        }
        return "hsl(0, 72%, 51%)";
    }
</script>

<section class="group">
    <h2>{heading}</h2>
    <p class="subtitle">{subtitle}</p>

    {#each rows as s (s.label)}
        <div class="score" class:overall={!s.label}>
            <div class="header">
                <span class="label">{title(s.label)}</span>
                {#if hasEstimate(s)}
                    <span class="estimate">
                        {pct(s.estimate)}
                        <span class="band">{bandHalfWidth(s)}</span>
                    </span>
                {:else}
                    <span class="giveup">Not enough data yet</span>
                {/if}
            </div>

            {#if hasEstimate(s)}
                <div class="bar" title="range {pct(s.rangeLow)}–{pct(s.rangeHigh)}">
                    <div
                        class="fill"
                        style:width={pct(s.estimate)}
                        style:background={strengthColor(s.estimate)}
                    ></div>
                    <div
                        class="band-region"
                        style:left={pct(s.rangeLow)}
                        style:width={pct(s.rangeHigh - s.rangeLow)}
                    ></div>
                </div>
                <div class="meta">
                    range {pct(s.rangeLow)}–{pct(s.rangeHigh)} · {s.gradedReviews}
                    graded reviews · updated {lastUpdated(s.lastReviewSecs)}
                </div>
            {:else}
                <div class="bar empty"></div>
                <div class="meta">
                    {#if s.cardsWithState === 0 && s.gradedReviews > 0}
                        no FSRS memory data yet ({s.cardCount} cards) — enable FSRS and
                        keep reviewing
                    {:else}
                        {s.gradedReviews} graded reviews so far · {s.cardCount} cards — keep
                        reviewing to unlock a score
                    {/if}
                </div>
            {/if}
        </div>
    {/each}
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

    .score {
        border: 1px solid var(--border);
        border-radius: var(--border-radius, 5px);
        padding: 0.75em 1em;
        margin-bottom: 0.75em;

        &.overall {
            border-color: var(--fg-link);
            border-width: 2px;
        }
    }

    .header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 0.5em;
    }

    .label {
        font-weight: bold;
        text-transform: capitalize;
    }

    .estimate {
        font-size: 1.6em;
        line-height: 1.2;
        font-variant-numeric: tabular-nums;
    }

    .band {
        font-size: 0.6em;
        color: var(--fg-subtle);
    }

    .giveup {
        color: var(--fg-subtle);
        font-style: italic;
    }

    .bar {
        position: relative;
        height: 0.6em;
        margin: 0.5em 0 0.4em;
        border-radius: 999px;
        background: var(--canvas-inset, var(--border));
        overflow: hidden;

        &.empty {
            border: 1px dashed var(--border);
            background: transparent;
        }
    }

    .fill {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        border-radius: 999px;
    }

    .band-region {
        position: absolute;
        top: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            45deg,
            rgba(0, 0, 0, 0.18),
            rgba(0, 0, 0, 0.18) 3px,
            transparent 3px,
            transparent 6px
        );
    }

    .meta {
        font-size: 0.85em;
        color: var(--fg-subtle);
        margin-top: 0.25em;
    }
</style>
