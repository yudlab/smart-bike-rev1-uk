# Combined system proposal — 10 November 2026

## 1. Scope and evidence

Use a Raspberry Pi Pico for deterministic local functions: reed wheel sensor,
2-inch SPI display, brake input, handlebar buttons and front/rear lamp logic.
Use the ESP32-S3 for telemetry, GPS, persistent trip summaries, local web UI and
remote communication. Local brake/lighting operation must not wait for Wi-Fi,
GPS or the ESP. Keep an independent usable lighting fallback during development.

The supplied photographs show: RP2040 Pico listing; 2.0 TFT SPI GMT020-02 VER1.1
board with BLK/CS/DC/RST/SDA/SCL/VCC/GND; GOOUUU ESP32-S3-CAM-labelled board;
trackball breakout with directional/button/RGB pins; NEO-6M on GY-GPS6MV2;
E220-900T22D radio modules; salvaged high-power LED/driver and reed sensor;
TrustFire EB02 box labelled 8.4 V output and USB 5 V maximum 2100 mA.
Labels establish identity clues, not verified electrical performance. Screen
controller, exact board variant, lamp ratings and cell protection remain unknown.
The uploaded PDF contains generic product safety text, no circuit or pinout.

Purchased mechanical items include brake/shift cables, housings, cable ends,
chain tool, cassette/freewheel tool, handlebar extension, jumper wires and an
assorted component kit. Inspect suitability: brake housing must be brake-rated;
4 mm versus 5 mm alone does not establish safety or compatibility. Diagnose chain
skipping and restore braking before any riding tests. Electronics do not repair
mechanical drivetrain or brake faults.

## 2. Three nodes and communication

Pico: live speed, units, circumference/magnet calibration, display brightness,
local brake and indicator timing. Amber front/rear signals on the selected side
share one phase (prototype 500 ms on/500 ms off). Brake red overrides rear idle
brightness without suppressing turn signals. Main beam and idle lamps are separate
logical channels; actual wiring depends on inspecting the light assembly.

Bike ESP32-S3: receives Pico telemetry, reads GPS, stores trip summaries, serves
a local dashboard and manages authenticated remote presence. Proposed UART
allocation: UART0 Pico, UART1 GPS, UART2 E220. Use native USB for debugging so the
three UARTs are not consumed by the debug console. Board USB routing, boot logs
on UART0 and GPIO routing must be verified; isolate external equipment during
flashing. Camera/PSRAM/flash reservations may constrain the photographed board.

Remote: second ESP, second E220 if using the long-range link, separate screen,
trackball, protected battery and charging. Trackball up/down moves between Alarm,
Lock, Auto lock and Night mode; centre selects; left/back cancels. Show pending,
acknowledged and failed commands distinctly. RGB LED can indicate link state.
Confirm the trackball's power and output type before using 3.3 V pull-ups.

Phase 1 uses encrypted unicast ESP-NOW for the short-range remote. Match Wi-Fi
channel with the bike access point; use per-device keys and application-level
acknowledgements. Phase 2 adds E220 UART radio after frequency, bandwidth,
transmit power, antenna gain and airtime limits are validated for the UK. E220 is
a radio transceiver, not merely an antenna; its antenna is distinct from GPS and
ESP Wi-Fi antennas. No RF transmission is enabled in this starter.

A captive portal is a convenience page, not an authentication scheme or reliable
presence detector. Phones sleep, switch networks and suspend web tabs. Use a
paired application heartbeat with explicit PARK arming; link loss is advisory
while riding. E220 is not an internet or cellular tracker: remote viewing needs
a reachable paired receiver or a later network uplink.

## 3. Power and interference control

Never put the labelled 8.4 V battery output directly into Pico VSYS, ESP GPIO,
the screen, GPS or a 5 V solenoid. Use fused, reverse-polarity-protected,
appropriately rated regulated rails. The box's 5 V/2.1 A label is not evidence it
can supply simultaneous lamp, radio and solenoid peak demand. Measure each load
and regulator dropout/ripple; add peak currents and margin before choosing supply.
Confirm matching protected cells, charger and battery protection separately.

Partition power into logic and load branches. Return solenoid, siren and lamp
currents directly to the distribution point rather than through MCU ground
wires. Keep low-level sensor wiring away from switching load loops and antennas.
Twist reed signal with ground. Start with an external 4.7–10 kOhm pull-up to 3.3 V,
a series resistor and RC/Schmitt conditioning; values must be checked against
pulse width, cable capacitance and ESD requirements. A possible bench starting
point is 1 kOhm series and 10 nF to ground at the input, then a 3.3 V Schmitt buffer.
This is not a verified schematic. Never clamp a high-energy surge into GPIO rails.

Place 100 nF local bypass capacitors near logic supply pins plus suitable local
bulk capacitance at radio and driver branches. Follow each regulator's stability
requirements; do not add arbitrary capacitors across unknown switch-mode outputs.
Use a logic-level MOSFET specified at the actual 3.3 V gate voltage, gate resistor
and gate pull-down for each suitable DC load. GPIO must never power a coil or
high-current LED. Put a suitably rated flyback diode at the solenoid, cathode to
positive; validate release time, since a diode slows coil release. If release time
requires a TVS/clamp, select it with the MOSFET voltage and coil energy in mind.
Retain or replace the headlamp's proper constant-current driver and heatsink.
Do not assume PWM on its supply is supported. A multi-function lamp may need
isolated button emulation rather than directly switching individual LEDs.

Power loads through secured rated terminals, not solderless breadboard contacts.
The breadboard is for logic and resistor-limited indicator LEDs. Start from a
current-limited bench supply. Later use strain relief, waterproof connectors,
sealed enclosures with appropriate condensation management, and secure mounting.

Interference acceptance test: count false wheel pulses with wheel stationary while
cycling each load and transmitting radio; observe 3.3/5 V rails on an oscilloscope;
log resets, rejected pulses, packet errors and GPS fix loss. Repeat with realistic
cable lengths, low battery and simultaneous loads. Resolve electrical noise before
loosening software filters. A software filter cannot prevent brownouts.

Earlier repository reviewed: yudlab/speedo, default beta-trial. Its speedo.ino has a
300 ms debounce interval, updates tLastRev before rejecting a pulse, and delays the
main loop by 1100 ms. Those observations motivate a non-blocking design and separate
accepted/rejected pulse counters; they do not establish the cause of past interference.
At 2.1 m/revolution, 300 ms limits accepted pulses to roughly 25.2 km/h for one magnet.

## 4. Parking lock and alarm

Never engage a mechanism in a wheel, brake or steering system because a remote
has disconnected. A broken reed cable looks like zero speed. GPS zero is also
insufficient. Design a mechanical parking interlock that physically prevents
engagement while riding, a separate PARK input, independent stillness evidence,
position feedback and a manual release. No software-only guarantee is adequate.

Proposed sequence: explicit parking arm; healthy independent interlocks; loss of
previously authenticated heartbeat for 5 seconds; 10-second visible/audible
warning; recheck all conditions; bounded actuator request. Any movement, sensor
fault, cancelled PARK, reset or returning heartbeat cancels pending actuation.
Never infer lock position from a command. Show LOCKED only from verified feedback.
No pulse duration is chosen until coil current/duty rating and mechanics are known.
The code stops at LOCK_REQUEST_ONLY and has no solenoid driver or bypass flag.

Alarm has explicit arm/disarm and a bounded two-second visual bench test. Physical
siren drivers, motion sensor selection and production alarm escalation are pending.
Use a non-blocking scheduler; keep brake sensing alive during alarms and warnings.

## 5. Breadboard wiring proposal

Pico GPIO numbers, provisional allocation (not physical connector pin numbers):

| Function | GPIO | Note |
|---|---|---|
| UART0 TX / RX | GP0 / GP1 | Cross to ESP RX/TX, common ground, 3.3 V only |
| Reed contact | GP2 | Dry contact to GND with conditioned input |
| Brake input | GP3 | Dry test switch, independent of mechanical brake |
| Left / right | GP4 / GP5 | Local maintained test switches |
| Physical PARK input | GP6 | Reserved; not connected in starter |
| SPI1 SCK / MOSI | GP10 / GP11 | Screen SCL means SPI clock; SDA means MOSI |
| TFT CS / DC / RST | GP9 / GP8 / GP12 | Verify module labels and logic ratings |
| TFT backlight | GP13 | Driver/control only after BLK circuit verified |
| Main / front idle / rear idle | GP14 / GP15 / GP16 | Future external driver inputs |
| Left / right indicator groups | GP17 / GP18 | Future front/rear driver grouping |
| Brake lamp / siren | GP19 / GP20 | Future external drivers |
| Lock request / feedback | GP21 / GP22 | Reserved, no actuator code |
| Independent stillness | Unassigned | Sensor selection and bus still pending |

Test screen separately before combined harness. Do not infer ST7789 from size or
GMT020-02 silkscreen alone. Confirm controller, dimensions, rotation, colour order,
voltage and backlight current. The driver adapter is deliberately unbound.
ESP pins are intentionally not guessed: obtain the exact S3-CAM schematic first.

## 6. Data, debug mode and implementation boundaries

Wheel formula: speed km/h = circumference_mm / magnets_per_rev * 3.6 / period_ms.
Store distance in metric units regardless of display units. Measure tyre rollout
under rider load, over multiple revolutions; average and enter millimetres. Ignore
implausibly close pulses without moving the accepted timestamp. No pulses causes
a display timeout, not a safety assertion of standstill.

Wired prototype protocol: newline JSON at 115200 baud, version, sequence, monotonic
ms, kmh, trip_mm, rejected count and output state. Proposed production transport adds
bounded framing, CRC, resynchronisation, sequence checks, boot/session identity,
heartbeats and explicit acknowledgements. CRC detects corruption, not attackers.
Wireless commands require authenticated encryption, replay prevention, paired
identity and expiry; never accept arbitrary pin numbers or raw actuator writes.

Persistent records belong on the ESP: schema version, trip ID, timestamps with time
validity, distance, duration, max speed, fix age/quality and optional positions.
Use batched writes with checksums and two-slot recovery or a journal; avoid writing
flash per wheel pulse. GPS logging should be opt-in, bounded and exportable; never
commit tracks or keys. The starter does not yet parse NMEA or persist ride statistics.

Production debug mode should require a physical service jumper, stationary parked
bike, authenticated local session and a short timeout. Individual lamp/siren tests
must be bounded; test-all must sequence channels rather than energise every load
at once. Lock interlocks remain mandatory. The supplied web app is simulation only,
with fault injection and JSON session export; no endpoint can drive GPIO.

## 7. Build stages and acceptance

1. Restore brakes and investigate chain wear, indexing, stiff links, cassette wear
   and freehub symptoms. Check housing and cable compatibility before fitting.
2. On USB power, prove Pico reed sensing and calibration. Verify 100 wheel turns
   match expected distance, bounce is rejected and stopped display times out.
3. Identify TFT and integrate its driver. Stress refresh while counting pulses.
4. Inspect lamp assembly; measure voltage/current and establish isolated controls.
   Test each external driver with a dummy load first; then actual lamps off-bike.
5. Integrate UART framing, GPS parser and durable records; test malformed frames,
   stale fixes, MCU resets and power loss mid-save. Prove local lights survive ESP loss.
6. Pair encrypted short-range remote, screen and trackball. Test acknowledgements,
   retries, duplicate commands, wrong peers and phone sleep behaviour.
7. Validate E220 UK parameters and antenna matching before RF tests. Measure airtime
   including retries and acknowledgements; rate-limit accordingly.
8. Prototype parking mechanics away from the bicycle. Prove independent interlocks,
   manual release and position feedback. No moving-wheel actuation tests with a rider.
9. Replace breadboard with soldered secured construction; repeat interference,
   vibration and weather tests before considering road use.

## 8. Sources and open decisions

Manufacturer / regulator references, checked 10 November 2026:
- Raspberry Pi Pico documentation: https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html
- Espressif ESP32-S3 datasheet: https://documentation.espressif.com/esp32_s3_datasheet_en.pdf
- ESP-NOW reference: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/network/esp_now.html
- Ebyte E220-900T22D manual: https://www.ebyte.com/Uploadfiles/Files/2021-7-6/202176188184448.pdf
- Ofcom short-range devices: https://www.ofcom.org.uk/spectrum/radio-equipment/short-range-devices
- Ofcom IR2030: https://www.ofcom.org.uk/siteassets/resources/documents/spectrum/interface-requirements/ir-2030.pdf
- Earlier project: https://github.com/yudlab/speedo/tree/beta-trial

UK radio compliance depends on the exact permitted sub-band, emission bandwidth,
antenna-adjusted radiated power and channel-access/duty-cycle rules. Do not assume
factory 900/915 MHz or full 22 dBm settings are allowed. Exact E220 settings remain
a design gate; no blanket legality claim is made here. Road lighting compliance
also needs review against the final lamps and installation, not the concept image.

Need before hardware integration: exact TFT driver; ESP board schematic; lamp supply
and pinout; solenoid rating and mechanism; remote screen and second ESP availability;
battery cell/protection details; measured wheel circumference. These unknowns do
not prevent the simulation or breadboard input demo from being used now.
