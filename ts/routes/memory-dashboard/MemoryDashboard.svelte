<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

Speedrun: the honest MCAT readiness dashboard. Shows three separate scores —
Memory, Performance and Readiness — never one blended number. Each carries a
range and a give-up rule so it says when it doesn't know.
-->
<script lang="ts">
    import type {
        MemoryScoreResponse,
        ReadinessScoreResponse,
    } from "@generated/anki/scheduler_pb";

    import Col from "$lib/components/Col.svelte";
    import Container from "$lib/components/Container.svelte";

    import ReadinessPanel from "./ReadinessPanel.svelte";
    import ScoreGroup from "./ScoreGroup.svelte";

    export let memory: MemoryScoreResponse;
    export let performance: MemoryScoreResponse;
    export let readiness: ReadinessScoreResponse;
</script>

<Container --gutter-block="1rem" --gutter-inline="2px" breakpoint="sm">
    <Col --col-justify="center">
        <div class="dashboard">
            <h1>MCAT Readiness</h1>
            <p class="intro">
                Three honest scores, each with its own uncertainty range. We never
                blend them into one number, and we refuse to show a score until
                there's enough of your review data to trust it.
            </p>

            <ScoreGroup
                heading="Memory"
                subtitle="Predicted recall right now — how well you'd remember each section's cards."
                score={memory}
            />

            <ScoreGroup
                heading="Performance"
                subtitle="Predicted accuracy on exam-style questions — recall discounted by how hard the material is."
                score={performance}
            />

            <ReadinessPanel {readiness} />
        </div>
    </Col>
</Container>

<style lang="scss">
    .dashboard {
        margin-top: 1.5em;
        max-width: 34em;
        font-size: var(--font-size);
    }

    .intro {
        color: var(--fg-subtle);
        margin-bottom: 1.5em;
    }
</style>
