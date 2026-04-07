# Thermal Printing

> Back to [Receipt Module](index.md) · See also [Templates](templates.md)

## Supported Printers

Any ESC/POS-compatible thermal printer reachable via TCP/IP or USB.

| Connection    | Class            | Status                              |
| ------------- | ---------------- | ----------------------------------- |
| Network (TCP) | `NetworkPrinter` | Supported                           |
| USB           | `USBPrinterStub` | Stub — raises `NotImplementedError` |

Common compatible models: Epson TM-T88, Star TSP100, Bixolon SRP-350, POS-80.

---

## Paper Sizes

| Size | Character Width | Layout Class |
| ---- | --------------- | ------------ |
| 80mm | 48 chars/line   | `Layout80mm` |
| 58mm | 32 chars/line   | `Layout58mm` |

The renderer auto-selects the layout based on the template's `paper_size` field.

---

## Network Printer Setup

### 1. Connect the printer to the network

Assign a static IP (e.g. `192.168.1.100`) via the printer's configuration utility or DHCP reservation.

### 2. Test connectivity

```bash
ping 192.168.1.100
# or
nc -zv 192.168.1.100 9100
```

### 3. Print via API

```bash
curl -X POST /api/v1/pos/receipts/{id}/print/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_ip": "192.168.1.100",
    "port": 9100,
    "paper_width": "80mm",
    "copies": 1,
    "open_drawer": true
  }'
```

### 4. Service-level usage

```python
from apps.pos.receipts.services import (
    ThermalPrintRenderer,
    NetworkPrinter,
)

# Render receipt data to ESC/POS bytes
renderer = ThermalPrintRenderer()
raw_bytes = renderer.render(receipt_data, paper_width="80mm")

# Send to printer
printer = NetworkPrinter(host="192.168.1.100", port=9100)
printer.send(raw_bytes)
```

---

## ESC/POS Command Reference

The `ESCPOSConstants` class provides raw byte sequences:

| Constant                                      | Description                    |
| --------------------------------------------- | ------------------------------ |
| `INIT`                                        | Reset printer to default state |
| `BOLD_ON` / `BOLD_OFF`                        | Toggle bold text               |
| `UNDERLINE_ON` / `UNDERLINE_OFF`              | Toggle underline               |
| `ALIGN_LEFT` / `ALIGN_CENTER` / `ALIGN_RIGHT` | Text alignment                 |
| `CUT_FULL` / `CUT_PARTIAL`                    | Paper cutter commands          |
| `FONT_A` / `FONT_B`                           | Font selection                 |
| `DOUBLE_HEIGHT_ON` / `OFF`                    | Double-height text             |
| `DOUBLE_WIDTH_ON` / `OFF`                     | Double-width text              |
| `FEED_ONE` … `FEED_FIVE`                      | Paper feed (n lines)           |
| `OPEN_DRAWER`                                 | Trigger cash drawer solenoid   |
| `BARCODE_CODE128`                             | Barcode print command          |
| `PAPER_WIDTH_80` / `PAPER_WIDTH_58`           | Width constants (48/32 chars)  |

---

## Cash Drawer Integration

Most thermal printers can trigger an attached cash drawer via the `OPEN_DRAWER` ESC/POS command. Set `open_drawer: true` in the print request to fire the solenoid after printing.

```python
printer_service = ThermalPrinterService()
printer_service.open_drawer()  # Sends OPEN_DRAWER bytes
```

---

## Print Queue

The `PrintQueue` service manages asynchronous print jobs with priority and retry:

```python
from apps.pos.receipts.services import PrintQueue, PrintJob, PrintPriority

queue = PrintQueue()
job = PrintJob(
    receipt_id=receipt.pk,
    data=raw_bytes,
    printer_ip="192.168.1.100",
    priority=PrintPriority.NORMAL,
)
queue.enqueue(job)
```

| Priority | Value | Use Case                   |
| -------- | ----- | -------------------------- |
| `HIGH`   | 1     | Immediate reprint requests |
| `NORMAL` | 5     | Standard sale receipts     |
| `LOW`    | 10    | End-of-day reports         |

---

## Troubleshooting

### Printer not responding

1. Verify network connectivity: `ping <printer_ip>`
2. Check the printer is listening on port 9100: `nc -zv <ip> 9100`
3. Ensure no firewall rules block port 9100
4. Power-cycle the printer

### Garbled characters

- Confirm the printer supports ESC/POS (not ZPL or other protocols)
- Verify the correct paper width is selected (80mm vs 58mm)
- Reset with `ESCPOSConstants.INIT` before each job

### Paper jam

- Open the cover, remove jammed paper, and reload
- Avoid paper below 55gsm weight

### Cash drawer not opening

- Verify the RJ-12 cable is connected from the printer's DK port to the drawer
- Confirm `open_drawer` is `true` in the print request
- Test with the printer's built-in self-test

### Logo not printing

- Logo must be pre-loaded to the printer's NV memory via manufacturer utility
- Ensure `header_logo_url` is set and accessible

### Incorrect layout / truncation

- Check template `paper_size` matches the physical paper width
- 80mm printers use 48 character columns; 58mm use 32
- Long product names are automatically truncated by the layout formatter

### Connection timeout errors

- Default timeout is 5 seconds; increase if network latency is high
- Consider a dedicated VLAN for POS printer traffic
- Check for IP conflicts on the network
