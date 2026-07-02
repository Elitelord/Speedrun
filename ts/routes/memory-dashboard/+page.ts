// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
//
// Speedrun: honest MCAT readiness dashboard. Loads the configured MCAT topic
// tags (falling back to defaults) and the three scores — memory, performance,
// and readiness — for the whole collection.
import {
    computeMemoryScore,
    computePerformanceScore,
    computeReadinessScore,
    getInterleaveConfig,
} from "@generated/backend";

import type { PageLoad } from "./$types";

const DEFAULT_TOPICS = ["mcat::biobiochem", "mcat::chemphys", "mcat::psychsoc"];

export const load = (async () => {
    const config = await getInterleaveConfig({});
    const topicTags = config.topicTags.length ? config.topicTags : DEFAULT_TOPICS;
    const req = { search: "", topicTags, topicMinReviews: 0, deckMinReviews: 0 };
    const [memory, performance, readiness] = await Promise.all([
        computeMemoryScore(req),
        computePerformanceScore(req),
        computeReadinessScore(req),
    ]);
    return { memory, performance, readiness };
}) satisfies PageLoad;
