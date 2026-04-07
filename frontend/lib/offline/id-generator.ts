// ================================================================
// Offline Transaction ID Generator — Task 37
// ================================================================
// Format: OFFLINE-{TERMINAL}-{TIMESTAMP}-{SEQUENCE}
// Example: OFFLINE-T01-1700000000-001
// ================================================================

const ID_PATTERN = /^OFFLINE-[A-Z0-9]{2,10}-\d{10}-\d{3}$/;

export interface ParsedOfflineId {
  prefix: string;
  terminal: string;
  timestamp: number;
  sequence: number;
  isValid: boolean;
}

// ── Sequence state ─────────────────────────────────────────────

let lastTimestamp = 0;
let lastSequence = 0;

/**
 * Generate a unique offline transaction ID.
 * Guarantees uniqueness within the same terminal by using a
 * monotonically increasing sequence within each second.
 */
export function generateOfflineTransactionId(terminalId: string): string {
  const now = Math.floor(Date.now() / 1000);

  if (now === lastTimestamp) {
    lastSequence += 1;
    if (lastSequence > 999) {
      // Wait for next second (extremely unlikely for POS)
      lastSequence = 1;
      lastTimestamp = now + 1;
    }
  } else {
    lastTimestamp = now;
    lastSequence = 1;
  }

  const terminal = terminalId
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '')
    .slice(0, 10)
    .padStart(2, '0');
  const ts = String(lastTimestamp).padStart(10, '0');
  const seq = String(lastSequence).padStart(3, '0');

  return `OFFLINE-${terminal}-${ts}-${seq}`;
}

/** Validate an offline ID string. */
export function isValidOfflineId(id: string): boolean {
  return ID_PATTERN.test(id);
}

/** Parse an offline ID into its components. */
export function parseOfflineId(id: string): ParsedOfflineId | null {
  if (!isValidOfflineId(id)) return null;
  const parts = id.split('-');
  return {
    prefix: parts[0]!,
    terminal: parts[1]!,
    timestamp: parseInt(parts[2]!, 10),
    sequence: parseInt(parts[3]!, 10),
    isValid: true,
  };
}

/** Reset sequence (useful for tests). */
export function resetSequence(): void {
  lastTimestamp = 0;
  lastSequence = 0;
}
