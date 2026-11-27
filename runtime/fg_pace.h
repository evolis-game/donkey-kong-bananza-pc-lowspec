// Pacing arithmetic of the frame generation (vk_framegen.c), kept free of Vulkan and of clocks so a test can drive it with
// a synthetic one. Times are nanoseconds. From Hookshot gpu/vk/vk_framegen.cpp (display_main: the interval average and
// the 100 ms rule), https://github.com/NotRexed/Hookshot @ fab8cb37641714bd839ae83c2a7bc582bedc4d70, GPL-3.0.
#pragma once
#include <stdint.h>

#define FG_HITCH_NS 250000000ll   // a gap between two jobs over 250 ms is a hitch: no made frame, the history starts again

// Whether the gap since the previous job is a hitch (loading, a pause): nothing to blend across it.
static inline int fg_pace_hitch(int64_t gap) { return gap > FG_HITCH_NS; }

// The game's frame interval, an exponential average of the gaps between jobs: I = (7 I + clamp(gap, 4 ms, 150 ms)) / 8,
// and the first gap as it is. interval 0 means none yet; call it only with a gap that is not a hitch.
static inline int64_t fg_pace_interval(int64_t interval, int64_t gap) {
    int64_t g = gap < 4000000 ? 4000000 : gap > 150000000 ? 150000000 : gap;
    return interval ? (interval * 7 + g) / 8 : g;
}

// When step i (1..mult-1) or real frame (step == mult) is due after the first made frame went out at made_at.
static inline int64_t fg_pace_due_step(int64_t made_at, int64_t interval, int step, int mult) {
    return made_at + (interval * step) / (mult > 0 ? mult : 2);
}

// When the game's own frame is due once the made frame went out at made_at (2x convenience helper).
static inline int64_t fg_pace_due(int64_t made_at, int64_t interval) { return made_at + interval / 2; }

// Whether the display is too slow for mult-x (2x or 3x) frame generation.
static inline int fg_pace_over_refresh_mult(int64_t interval, double refresh_hz, int mult) {
    if (interval <= 0) return 0;
    if (refresh_hz <= 0) refresh_hz = 60.0;
    return ((double)mult * 1e9) / (double)interval > refresh_hz * 1.35;
}

static inline int fg_pace_over_refresh(int64_t interval, double refresh_hz) {
    return fg_pace_over_refresh_mult(interval, refresh_hz, 2);
}
