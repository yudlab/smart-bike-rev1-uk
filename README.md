# Yudlab Smart Bike · rev 1 UK

Breadboard-first design and object-oriented starter code. **Prototype, not road-ready firmware.**

## Project scope: pedal bicycle only

This is a **human-powered bicycle**. There is no motor, throttle, propulsion control, motor controller or electric-assist system. Electronics are limited to instrumentation, lighting, alerts, GPS/statistics and a handheld remote. Reuse the existing wheel reed switch and headlamp after electrical inspection. The 5 V solenoid is a **parking-lock research item only**, not connected to a wheel or brake in the starter firmware. The mechanical brakes always remain independent of the electronics.

**Current priority:** breadboard logic and SVG/web simulation. No new PDF generation is required for this phase; the previously committed proposal remains reference material only.

## Try the animated lab

No npm installation needed. From the repository directory:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory web
```

Open http://127.0.0.1:8080. On Windows use `py` if `python3` is unavailable.
The SVG bike changes lights, colours and display brightness. Exercise indicators,
brakes, wheel pulses, bounce, calibration, km/h/mph, alarm, remote loss, parking
interlocks and remote menu navigation. Export simulation records as JSON.
The app sends **no hardware commands**. Reload resets the session.

## What's implemented

| Component | Current status |
|---|---|
| Web lab | Runnable local simulation, animated editable SVG, all requested feature controls |
| Pico domain classes | Wheel calibration/speed/trip/filter, lighting, bounded alarm and parking request policy |
| Pico main | MicroPython reed/buttons input demo, UART telemetry; no load outputs |
| 2-inch screen | Driver adapter contract only; controller/resolution not yet confirmed |
| ESP gateway | Arduino USB serial scaffold; GPS/radio/storage integration pending |
| Remote | Portable Python menu model; board, screen and trackball adapters pending |
| Solenoid | No energising path in this release; mechanical parking interlock required |
| Proposal | `docs/Yudlab-Smart-Bike-Proposal.pdf`, source design notes and build script |

Do not wire loads to GPIO or breadboard power rails. Follow `docs/design.md`.
The existing ESP32-S3 board is allocated to the bike; another ESP is required for
an independent handheld remote unless already owned. The normal Pico has no Wi-Fi.

## Pico bench input test

Install official MicroPython for the original RP2040 Pico. Copy
`firmware/pico/core.py` and `main.py` to its filesystem. With power off, connect
reed GP2–GND, brake test switch GP3–GND, left GP4–GND, right GP5–GND.
Use clean dry contacts only; these are **GPIO numbers**, not physical pin numbers.
For long wires add the documented input protection. UART0 TX=GP0, RX=GP1,
115200 baud, 3.3 V TTL; cross TX/RX to a verified 3.3 V USB UART and share ground.
Never attach RS-232 voltage levels. Initial calibration is an example 2100 mm.
The script emits newline JSON four times per second; it accepts no commands.

The input loop uses 1 ms polling for the breadboard. It is not a guaranteed
high-speed pulse acquisition system once a blocking display driver is added:
move acquisition to a bounded IRQ/ring buffer or PIO before integration.
`display.py` is deliberately not imported by main.py until the screen is identified.

## Tests

Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
node --test tests/model.test.cjs
```

These verify domain logic on a desktop, not physical hardware, radio compliance,
Arduino compilation or a MicroPython flash. Firmware scaffolds require integration.

## Next hardware decisions

Confirm TFT controller/resolution and backlight circuit; exact ESP32-S3 board
schematic; headlamp/combination-light voltage, current and switching arrangement;
solenoid normal state/current/duty rating and a mechanism physically unable to
engage a moving wheel; remote display; battery cell protection and capacity.

No purchase screenshots, private locations, credentials or original photos are
committed. The concept illustration is an AI-generated visual, not a wiring guide.
