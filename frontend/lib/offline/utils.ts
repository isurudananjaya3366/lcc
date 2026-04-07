// ================================================================
// Timestamp & Time Utilities — Task 28
// ================================================================
// Helpers for ISO-8601 timestamp manipulation used across
// the offline caching layer.
// ================================================================

/** Return the current UTC time as ISO-8601 string. */
export function getCurrentTimestamp(): string {
  return new Date().toISOString();
}

/** Parse an ISO-8601 string into a Date. */
export function parseTimestamp(isoString: string): Date {
  return new Date(isoString);
}

/** True if ts1 is strictly newer than ts2. */
export function isTimestampNewer(ts1: string, ts2: string): boolean {
  return new Date(ts1).getTime() > new Date(ts2).getTime();
}

/** True if the timestamp is older than the given duration (ms). */
export function isOlderThan(timestamp: string, durationMs: number): boolean {
  return Date.now() - new Date(timestamp).getTime() > durationMs;
}

/** Duration between two timestamps in milliseconds. */
export function getDuration(startTime: string, endTime: string): number {
  return new Date(endTime).getTime() - new Date(startTime).getTime();
}

/** Human-friendly duration string, e.g. "2m 15s". */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const seconds = Math.floor(ms / 1000) % 60;
  const minutes = Math.floor(ms / 60000) % 60;
  const hours = Math.floor(ms / 3600000);

  const parts: string[] = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (seconds > 0 || parts.length === 0) parts.push(`${seconds}s`);
  return parts.join(' ');
}

/** Stored offset (ms) between local clock and server clock. */
let serverTimeOffset = 0;

export function setServerTimeOffset(offset: number): void {
  serverTimeOffset = offset;
}

export function getServerTimeOffset(): number {
  return serverTimeOffset;
}

/** Adjust a local Date to approximate server time using the offset. */
export function adjustForServerTime(localTime: Date): Date {
  return new Date(localTime.getTime() + serverTimeOffset);
}
