<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

Speedrun: the honest memory-score dashboard. Each score is a point estimate of
FSRS predicted recall paired with an uncertainty range; when there aren't enough
graded reviews (the give-up rule), it refuses to show a number rather than guess.
-->
<script lang="ts">
    import type {
        MemoryScore,
        MemoryScoreResponse,
    } from "@generated/anki/scheduler_pb";

    import Col from "$lib/components/Col.svelte";
    import Container from "$lib/components/Container.svelte";

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
</script>

<Container --gutter-block="1rem" --gutter-inline="2px" breakpoint="sm">
    <Col --col-justify="center">
        <div class="dashboard">
            <h1>Memory</h1>
            <p class="subtitle">
                Predicted recall with an honest uncertainty range. No score is shown
                until there are enough graded reviews to trust it.
            </p>

            {#each rows as s (s.label)}
                <div class="score" class:overall={!s.label}>
                    <div class="label">{title(s.label)}</div>

                    {#if hasEstimate(s)}
                        <div class="estimate">
                            {pct(s.estimate)}
                            <span class="band">({bandHalfWidth(s)})</span>
                        </div>
                        <div class="range">
                            range {pct(s.rangeLow)}–{pct(s.rangeHigh)}
                        </div>
                        <div class="meta">
                            {s.gradedReviews} graded reviews · updated {lastUpdated(
                                s.lastReviewSecs,
                            )}
                        </div>
                    {:else}
                        <div class="giveup">Not enough data yet</div>
                        <div class="meta">
                            {#if s.cardsWithState === 0 && s.gradedReviews > 0}
                                no FSRS memory data ({s.cardCount} cards)
                            {:else}
                                {s.gradedReviews} graded reviews so far · {s.cardCount}
                                cards
                            {/if}
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    </Col>
</Container>

<style lang="scss">
    .dashboard {
        margin-top: 1.5em;
        max-width: 34em;
        font-size: var(--font-size);
    }

    .subtitle {
        color: var(--fg-subtle);
        margin-bottom: 1.5em;
    }

    .score {
        border: 1px solid var(--border);
        border-radius: var(--border-radius, 5px);
        padding: 0.75em 1em;
        margin-bottom: 0.75em;

        &.overall {
            border-color: var(--fg-link);
        }
    }

    .label {
        font-weight: bold;
        text-transform: capitalize;
    }

    .estimate {
        font-size: 1.8em;
        line-height: 1.2;
    }

    .band {
        font-size: 0.6em;
        color: var(--fg-subtle);
    }

    .range {
        color: var(--fg-subtle);
    }

    .giveup {
        font-size: 1.2em;
        color: var(--fg-subtle);
        font-style: italic;
    }

    .meta {
        font-size: 0.85em;
        color: var(--fg-subtle);
        margin-top: 0.25em;
    }
</style>
