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
| Web lab | Runnable SVG simulation plus separate live USB diagnostics and timed indicator test panel |
| Pico domain classes | Wheel calibration/speed/trip/filter, lighting, bounded alarm and parking request policy |
| Pico main | MicroPython reed/buttons input demo, UART + USB telemetry, bounded optional GP17/18 bench LED tests |
| 2-inch screen | Driver adapter contract only; controller/resolution not yet confirmed |
| ESP gateway | Arduino USB serial scaffold; GPS/radio/storage integration pending |
| Remote | Portable Python menu model; board, screen and trackball adapters pending |
| Solenoid | No energising path in this release; mechanical parking interlock required |
| Proposal | `docs/Yudlab-Smart-Bike-Proposal.pdf`, source design notes and build script |

Do not wire loads to GPIO or breadboard power rails. Follow `docs/design.md`.
The existing ESP32-S3 board is allocated to the bike; another ESP is required for
an independent handheld remote unless already owned. The normal Pico has no Wi-Fi.

## Live laptop diagnostics (USB + Wi-Fi)

The original static Python web server remains useful for simulation only. For **real Pico USB serial diagnostics**, install the bridge dependency and start the new server:

```sh
python3 -m pip install pyserial
python3 diagnostic_server.py --port COM5 --host 127.0.0.1
```

Replace `COM5` with the Pico USB serial port (Windows Device Manager; on Linux often `/dev/ttyACM0`). On Ubuntu, use `python3 diagnostic_server.py --port /dev/ttyACM0`. Close Thonny or other programs using that port before starting. Flash the updated `firmware/pico/core.py` and `firmware/pico/main.py` first, then allow the Pico to reboot.

The server prints a random **diagnostic token**. Open `http://localhost:8080`, enter that token in **Live Bench Diagnostics** and click **Connect dashboard**. The browser refreshes telemetry twice a second; the Pico sends telemetry approximately four times per second. View wheel speed, trip distance, rejected reed pulses, GPIO input states, logical light states, command errors and serial acknowledgements.

**Remote viewing on your own trusted Wi-Fi:** use `--host 0.0.0.0` and visit `http://LAPTOP_LAN_IP:8080` from another device. Keep this port restricted to your private LAN by firewall. HTTP and the token are **not encrypted**; do not expose the service to the internet, guest networks, port forwarding or an untrusted Wi-Fi. For access outside the private LAN use a suitably authenticated encrypted tunnel. The browser stores the token only for that tab session.

The **Left**, **Right** and **Hazard** buttons send an explicit 10-second test. The countdown is enforced **on the Pico**, even if the laptop or web connection fails. **Stop test** cancels it. This does not operate the real bicycle's lamps yet. For safe breadboard output trials, connect **only resistor-limited low-current test LEDs** to GP17 and GP18 and set `BENCH_LED_OUTPUTS=True` in `firmware/pico/main.py`. Never connect solenoids, sirens, headlamps, bare coils or other high-current hardware directly to a Pico pin. Physical indicator switches continue to work independently and can override the apparent off state when held. No brake, lock, siren or other actuator command is supported by the remote diagnostic endpoint.

The Python bridge is intentionally minimal: standard-library HTTP plus `pyserial`. It has a bounded JSON command allowlist, recent event buffer and serial reconnection attempts. This phase has not been validated against the actual Pico hardware.

## Pico bench input test

Install official MicroPython for the original RP2040 Pico. Copy
`firmware/pico/core.py` and `main.py` to its filesystem. With power off, connect
reed GP2–GND, brake test switch GP3–GND, left GP4–GND, right GP5–GND.
Use clean dry contacts only; these are **GPIO numbers**, not physical pin numbers.
For long wires add the documented input protection. UART0 TX=GP0, RX=GP1,
115200 baud, 3.3 V TTL; cross TX/RX to a verified 3.3 V USB UART and share ground.
Never attach RS-232 voltage levels. Initial calibration is an example 2100 mm.
The script emits newline JSON four times per second over USB and UART0; USB additionally accepts only the bounded indicator bench-test and stop commands described above.

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
