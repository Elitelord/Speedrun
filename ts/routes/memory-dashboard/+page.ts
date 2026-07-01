// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
//
// Speedrun: honest memory-score dashboard. Loads the configured MCAT topic tags
// (falling back to defaults) and the per-topic + overall memory score.
import { computeMemoryScore, getInterleaveConfig } from "@generated/backend";

import type { PageLoad } from "./$types";

const DEFAULT_TOPICS = ["mcat::biobiochem", "mcat::chemphys", "mcat::psychsoc"];

export const load = (async () => {
    const config = await getInterleaveConfig({});
    const topicTags = config.topicTags.length ? config.topicTags : DEFAULT_TOPICS;
    const score = await computeMemoryScore({
        search: "",
        topicTags,
        topicMinReviews: 0,
        deckMinReviews: 0,
    });
    return { score };
}) satisfies PageLoad;
