"""
CashDrawerService — manages cash drawer open/close commands.

Supports ESC/POS compatible cash drawers connected to POS terminals.
Gateway for hardware-specific commands is a placeholder until
actual hardware integration is implemented.
"""

import logging

logger = logging.getLogger(__name__)

# ESC/POS cash drawer kick command (pin 2)
DRAWER_OPEN_COMMAND = b"\x1b\x70\x00\x19\xfa"


class CashDrawerService:
    """Service for triggering cash drawer open commands."""

    @staticmethod
    def open_drawer(terminal) -> bool:
        """
        Send open command to the cash drawer.

        Returns True if the command was sent successfully.
        Checks terminal configuration before sending.
        """
        if not getattr(terminal, "cash_drawer_enabled", False):
            logger.debug("Cash drawer disabled for terminal %s", terminal.code)
            return False

        try:
            logger.info(
                "Cash drawer open triggered for terminal %s", terminal.code
            )
            # Hardware integration placeholder
            # In production, this would send DRAWER_OPEN_COMMAND
            # to the configured printer/drawer port
            return True
        except Exception:
            logger.exception(
                "Failed to open cash drawer for terminal %s", terminal.code
            )
            return False

    @staticmethod
    def should_auto_open(terminal) -> bool:
        """Check if auto-open is enabled for this terminal."""
        return (
            getattr(terminal, "cash_drawer_enabled", False)
            and getattr(terminal, "cash_drawer_auto_open", False)
        )

    @classmethod
    def open_on_cash_payment(cls, terminal) -> bool:
        """Open drawer after cash payment if auto-open is enabled."""
        if cls.should_auto_open(terminal):
            return cls.open_drawer(terminal)
        return False

    @staticmethod
    def manual_open_drawer(terminal, user) -> bool:
        """Manually open the cash drawer (requires explicit user action)."""
        if not getattr(terminal, "cash_drawer_enabled", False):
            return False

        logger.info(
            "Manual cash drawer open by user %s on terminal %s",
            user,
            terminal.code,
        )
        # Hardware integration placeholder
        return True
