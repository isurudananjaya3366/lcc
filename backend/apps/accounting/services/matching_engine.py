"""
Matching engine service for bank reconciliation.

Provides automatic and suggestion-based matching of bank statement
lines to journal entries using configurable rules with exact,
fuzzy, and reference-based matching strategies.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q

from apps.accounting.models.enums import JournalEntryStatus, MatchStatus

logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Matches bank statement lines to posted journal entries.

    Matching strategies (evaluated in order):
        1. Reference match  – exact reference/check number
        2. Exact match      – exact amount + same date
        3. Fuzzy match      – tolerance on amount and date range

    Usage::

        engine = MatchingEngine(bank_account)
        stats = engine.auto_match_batch(statement_id=stmt.id)
        suggestions = engine.suggest_matches(line, max_suggestions=5)
    """

    def __init__(self, bank_account):
        self.bank_account = bank_account
        self.gl_account = bank_account.gl_account

    # ── Internal helpers ───────────────────────────────────────────

    def _get_applicable_rules(self):
        """Return active matching rules in priority order."""
        from apps.accounting.models.matching_rule import MatchingRule

        return (
            MatchingRule.objects.filter(is_active=True)
            .filter(Q(bank_account=self.bank_account) | Q(bank_account__isnull=True))
            .order_by("priority")
        )

    def _get_unmatched_lines(self, statement_id=None):
        """Return unmatched statement lines for the bank account."""
        from apps.accounting.models.statement_line import StatementLine

        qs = StatementLine.objects.filter(
            statement__bank_account=self.bank_account,
            match_status=MatchStatus.UNMATCHED,
        )
        if statement_id:
            qs = qs.filter(statement_id=statement_id)
        return qs.order_by("transaction_date", "line_number")

    def _get_candidate_entries(self):
        """Return posted journal entries touching the GL account."""
        from apps.accounting.models.journal_entry import JournalEntry

        return JournalEntry.objects.filter(
            entry_status=JournalEntryStatus.POSTED,
            lines__account=self.gl_account,
        ).distinct().exclude(
            matched_statement_lines__isnull=False,
        ).order_by("entry_date")

    def _line_net_amount(self, statement_line):
        """Signed net amount of a statement line (credit - debit)."""
        return statement_line.credit_amount - statement_line.debit_amount

    def _entry_gl_amount(self, entry):
        """
        Signed amount the entry posts to the GL account.

        Positive = debit to GL account, negative = credit.
        """
        from apps.accounting.models.journal_line import JournalEntryLine

        lines = JournalEntryLine.objects.filter(
            journal_entry=entry,
            account=self.gl_account,
        )
        total = Decimal("0.00")
        for line in lines:
            total += line.debit_amount - line.credit_amount
        return total

    @staticmethod
    def _check_amount_match(stmt_amount, entry_amount, tolerance):
        return abs(stmt_amount - entry_amount) <= tolerance

    @staticmethod
    def _check_date_match(stmt_date, entry_date, date_range_days):
        return abs((stmt_date - entry_date).days) <= date_range_days

    def _check_description_match(self, description, compiled_pattern):
        if compiled_pattern is None:
            return True
        return bool(compiled_pattern.search(description or ""))

    def _calculate_match_score(self, stmt_amount, entry_amount,
                               stmt_date, entry_date,
                               description, compiled_pattern,
                               amount_tolerance, date_range_days):
        """Calculate 0.0–1.0 match quality score."""
        # Amount score (50% weight)
        amt_diff = abs(stmt_amount - entry_amount)
        denom = amount_tolerance if amount_tolerance > 0 else Decimal("0.01")
        amount_score = max(Decimal("0"), Decimal("1") - amt_diff / denom)

        # Date score (30% weight)
        day_diff = abs((stmt_date - entry_date).days)
        date_denom = date_range_days if date_range_days > 0 else 1
        date_score = max(0.0, 1.0 - day_diff / date_denom)

        # Description score (20% weight)
        desc_score = 1.0 if self._check_description_match(
            description, compiled_pattern
        ) else 0.5

        return float(amount_score) * 0.5 + date_score * 0.3 + desc_score * 0.2

    def _apply_match(self, statement_line, entry):
        """Set the match link and status on statement line."""
        statement_line.matched_entry = entry
        statement_line.match_status = MatchStatus.MATCHED
        statement_line.save(update_fields=["matched_entry", "match_status", "updated_at"])

    # ── Matching strategies ────────────────────────────────────────

    @transaction.atomic
    def match_exact(self, statement_line):
        """
        Exact match: identical amount and same date.

        Returns matched JournalEntry or None.
        """
        if statement_line.match_status != MatchStatus.UNMATCHED:
            return None

        stmt_amount = self._line_net_amount(statement_line)
        rules = self._get_applicable_rules().filter(
            amount_tolerance=0,
            date_range_days=0,
        )

        candidates = self._get_candidate_entries().filter(
            entry_date=statement_line.transaction_date,
        )

        for entry in candidates:
            entry_amount = self._entry_gl_amount(entry)
            if stmt_amount != entry_amount:
                continue

            # Apply rule description filters
            matched_rule = False
            for rule in rules:
                pattern = rule.get_compiled_pattern()
                if not self._check_description_match(entry.description, pattern):
                    continue
                matched_rule = True
                break

            if not rules.exists() or matched_rule:
                self._apply_match(statement_line, entry)
                return entry

        return None

    @transaction.atomic
    def match_fuzzy(self, statement_line):
        """
        Fuzzy match: amount within tolerance, date within range.

        Returns best-scoring JournalEntry or None.
        """
        if statement_line.match_status != MatchStatus.UNMATCHED:
            return None

        stmt_amount = self._line_net_amount(statement_line)
        rules = self._get_applicable_rules().filter(
            Q(amount_tolerance__gt=0) | Q(date_range_days__gt=0),
        )

        best_match = None
        best_score = 0.5  # minimum threshold

        for rule in rules:
            tolerance = rule.amount_tolerance
            date_range = rule.date_range_days

            min_date = statement_line.transaction_date - timedelta(days=date_range)
            max_date = statement_line.transaction_date + timedelta(days=date_range)

            candidates = self._get_candidate_entries().filter(
                entry_date__range=[min_date, max_date],
            )

            pattern = rule.get_compiled_pattern()

            for entry in candidates:
                entry_amount = self._entry_gl_amount(entry)
                if not self._check_amount_match(stmt_amount, entry_amount, tolerance):
                    continue
                if not self._check_description_match(entry.description, pattern):
                    continue

                score = self._calculate_match_score(
                    stmt_amount, entry_amount,
                    statement_line.transaction_date, entry.entry_date,
                    entry.description, pattern,
                    tolerance, date_range,
                )
                if score > best_score:
                    best_score = score
                    best_match = entry

            if best_match:
                break  # first rule with a match wins

        if best_match:
            self._apply_match(statement_line, best_match)
            logger.info(
                "Fuzzy match: line %s → entry %s (score: %.2f)",
                statement_line.pk, best_match.pk, best_score,
            )
            return best_match

        return None

    @transaction.atomic
    def match_by_reference(self, statement_line):
        """
        Reference match: exact reference/check number.

        Returns matched JournalEntry or None.
        """
        if statement_line.match_status != MatchStatus.UNMATCHED:
            return None
        if not statement_line.reference:
            return None

        ref = statement_line.reference.strip()
        rules = self._get_applicable_rules().filter(match_reference=True)
        if not rules.exists():
            return None

        candidates = self._get_candidate_entries().filter(
            Q(reference__iexact=ref) | Q(description__icontains=ref),
        )

        stmt_amount = self._line_net_amount(statement_line)

        for rule in rules:
            for entry in candidates:
                entry_amount = self._entry_gl_amount(entry)
                if not self._check_amount_match(
                    stmt_amount, entry_amount, rule.amount_tolerance
                ):
                    continue
                date_range = rule.date_range_days or 7
                if not self._check_date_match(
                    statement_line.transaction_date, entry.entry_date, date_range
                ):
                    continue

                self._apply_match(statement_line, entry)
                logger.info(
                    "Reference match: line %s → entry %s (ref: %s)",
                    statement_line.pk, entry.pk, ref,
                )
                return entry

        return None

    # ── Batch processing ───────────────────────────────────────────

    @transaction.atomic
    def auto_match_batch(self, statement_id=None):
        """
        Run all matching strategies on unmatched lines.

        Returns a statistics dict with counts and match rate.
        """
        from django.utils import timezone

        start_time = timezone.now()
        stats = {
            "total_lines": 0,
            "matched_total": 0,
            "matched_exact": 0,
            "matched_fuzzy": 0,
            "matched_reference": 0,
            "unmatched": 0,
            "errors": [],
            "status": "success",
        }

        lines = list(self._get_unmatched_lines(statement_id))
        stats["total_lines"] = len(lines)

        for line in lines:
            try:
                # Strategy 1: Reference match
                if self.match_by_reference(line):
                    stats["matched_reference"] += 1
                    stats["matched_total"] += 1
                    continue

                line.refresh_from_db()
                if line.match_status != MatchStatus.UNMATCHED:
                    stats["matched_total"] += 1
                    continue

                # Strategy 2: Exact match
                if self.match_exact(line):
                    stats["matched_exact"] += 1
                    stats["matched_total"] += 1
                    continue

                line.refresh_from_db()
                if line.match_status != MatchStatus.UNMATCHED:
                    stats["matched_total"] += 1
                    continue

                # Strategy 3: Fuzzy match
                if self.match_fuzzy(line):
                    stats["matched_fuzzy"] += 1
                    stats["matched_total"] += 1
                    continue

                stats["unmatched"] += 1

            except Exception as e:
                stats["errors"].append({
                    "line_id": str(line.pk),
                    "description": (line.description or "")[:100],
                    "error": str(e),
                })
                stats["status"] = "partial"
                logger.error("Error matching line %s: %s", line.pk, e)

        end_time = timezone.now()
        stats["match_rate"] = (
            (stats["matched_total"] / stats["total_lines"] * 100)
            if stats["total_lines"] > 0
            else 0.0
        )
        stats["processing_time"] = (end_time - start_time).total_seconds()

        logger.info(
            "Batch auto-match: %d/%d matched (%.1f%%) in %.2fs",
            stats["matched_total"],
            stats["total_lines"],
            stats["match_rate"],
            stats["processing_time"],
        )

        return stats

    # ── Suggestions ────────────────────────────────────────────────

    def suggest_matches(self, statement_line, max_suggestions=5):
        """
        Generate ranked match suggestions for manual review.

        Returns list of suggestion dicts sorted by score descending.
        """
        max_suggestions = min(max(int(max_suggestions), 1), 10)
        stmt_amount = self._line_net_amount(statement_line)

        # Broad tolerance: 5% of amount or 100 LKR, whichever is larger
        amount_tolerance = max(
            abs(stmt_amount) * Decimal("0.05"),
            Decimal("100.00"),
        )
        date_range_days = 14

        min_date = statement_line.transaction_date - timedelta(days=date_range_days)
        max_date = statement_line.transaction_date + timedelta(days=date_range_days)

        candidates = self._get_candidate_entries().filter(
            entry_date__range=[min_date, max_date],
        )

        suggestions = []
        for entry in candidates:
            entry_amount = self._entry_gl_amount(entry)
            if not self._check_amount_match(stmt_amount, entry_amount, amount_tolerance):
                continue

            score = self._calculate_match_score(
                stmt_amount, entry_amount,
                statement_line.transaction_date, entry.entry_date,
                entry.description, None,
                amount_tolerance, date_range_days,
            )
            if score < 0.1:
                continue

            # Quality tier
            if score >= 0.80:
                quality, confidence = "excellent", "High"
            elif score >= 0.60:
                quality, confidence = "good", "Medium-High"
            elif score >= 0.40:
                quality, confidence = "fair", "Medium"
            else:
                quality, confidence = "poor", "Low"

            amount_diff = float(entry_amount - stmt_amount)
            amount_diff_pct = (
                (amount_diff / float(stmt_amount)) * 100
                if stmt_amount != 0 else 0.0
            )
            date_diff = abs(
                (entry.entry_date - statement_line.transaction_date).days
            )

            # Build explanation
            parts = []
            if abs(amount_diff) < 1:
                parts.append("Exact amount")
            else:
                parts.append(
                    f"Amount differs by {abs(amount_diff):.2f} "
                    f"({abs(amount_diff_pct):.1f}%)"
                )
            if date_diff == 0:
                parts.append("exact date")
            else:
                parts.append(f"date differs by {date_diff} day(s)")

            # Flags
            flags = []
            if abs(amount_diff) > 100:
                flags.append("Large amount difference")
            if date_diff > 7:
                flags.append("Significant date offset")

            recommendations = {
                "excellent": "Strongly recommend matching",
                "good": "Good candidate, review details",
                "fair": "Possible match, verify carefully",
                "poor": "Unlikely match, consider alternatives",
            }

            suggestions.append({
                "journal_entry": entry,
                "match_score": round(score, 4),
                "quality": quality,
                "confidence": confidence,
                "metrics": {
                    "amount_difference": round(amount_diff, 2),
                    "amount_difference_percent": round(amount_diff_pct, 1),
                    "date_difference_days": date_diff,
                },
                "explanation": ", ".join(parts),
                "recommendation": recommendations[quality],
                "flags": flags,
            })

        suggestions.sort(key=lambda s: s["match_score"], reverse=True)
        return suggestions[:max_suggestions]
