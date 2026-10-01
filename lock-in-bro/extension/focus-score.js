// Returns an integer from 0–100 for manual and automatic session endings.
// Saved as summary.focusScore locally and FocusSession.focus_score in Flask.
function computeFocusScore(sessionSummary) {
  const {completed, plannedMinutes, actualMinutes, blockedCount} = sessionSummary || {};
  // Invalid or negative numbers count as zero; numeric strings are not accepted.
  const nonnegative = value => Number.isFinite(value) ? Math.max(0, value) : 0;
  const planned = nonnegative(plannedMinutes);
  const actual = nonnegative(actualMinutes);
  const attempts = nonnegative(blockedCount);

  let score = 100;
  score -= 5 * attempts;

  // An invalid/zero plan has no meaningful percentage, so skip its time penalty.
  if (planned > 0 && actual < planned) {
    const percentMissed = (planned - actual) / planned;
    score -= 30 * percentMissed;
  }
  if (completed !== true) score -= 10;

  return Math.round(Math.max(0, Math.min(100, score)));
}
