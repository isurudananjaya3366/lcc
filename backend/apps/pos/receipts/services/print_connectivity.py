"""
Print connectivity — network (TCP/IP) and USB printer transports.

Tasks 49-50: Network and USB printer support.
"""

import logging
import socket

logger = logging.getLogger(__name__)


class PrinterConnectionError(Exception):
    """Raised when printer connection fails."""


class NetworkPrinter:
    """
    Send raw ESC/POS bytes to a network-connected thermal printer via TCP.

    Usage::

        printer = NetworkPrinter("192.168.1.100", 9100)
        printer.send(raw_bytes)
    """

    DEFAULT_PORT = 9100
    TIMEOUT = 10  # seconds

    def __init__(self, host: str, port: int = DEFAULT_PORT,
                 timeout: int = TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send(self, data: bytes) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                sock.sendall(data)
            logger.info("Sent %d bytes to %s:%d", len(data), self.host, self.port)
            return True
        except (socket.timeout, OSError) as exc:
            logger.error("Network printer error (%s:%d): %s",
                         self.host, self.port, exc)
            raise PrinterConnectionError(
                f"Cannot reach printer at {self.host}:{self.port}"
            ) from exc

    def is_online(self) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                sock.connect((self.host, self.port))
            return True
        except (socket.timeout, OSError):
            return False


class USBPrinterStub:
    """
    Placeholder for USB printer support.

    Actual USB communication requires platform-specific drivers
    (e.g. python-escpos, pyusb). This stub provides the interface
    that a real implementation would follow.
    """

    def __init__(self, vendor_id: int = 0, product_id: int = 0):
        self.vendor_id = vendor_id
        self.product_id = product_id

    def send(self, data: bytes) -> bool:
        logger.warning(
            "USBPrinterStub.send() called — install python-escpos for real USB support"
        )
        raise PrinterConnectionError(
            "USB printing not yet configured. Install python-escpos."
        )

    def is_online(self) -> bool:
        return False
