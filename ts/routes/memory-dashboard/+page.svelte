<!--
Copyright: Ankitects Pty Ltd and contributors
License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
-->
<script lang="ts">
    import type { PageData } from "./$types";
    import MemoryDashboard from "./MemoryDashboard.svelte";

    export let data: PageData;
</script>

<MemoryDashboard
    memory={data.memory}
    performance={data.performance}
    readiness={data.readiness}
/>
