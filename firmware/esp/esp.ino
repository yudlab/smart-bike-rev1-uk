/* ESP32-S3 Arduino scaffold. USB serial diagnostic only until board pins verified.
   Never connects radios or actuators implicitly. No secrets or GPS tracks in git. */
#include <Arduino.h>
class TelemetryBuffer {
  String line;
  unsigned long received = 0;
  bool discarding = false;
public:
  void ingest(Stream &input) {
    while (input.available()) {
      char c = input.read();
      if (discarding) { if (c == '\n') discarding = false; continue; }
      if (c == '\n') {
        // Draft transport inspection only: not trusted commands or parsed stats.
        Serial.print("RX (unvalidated): "); Serial.println(line);
        line = ""; received++;
      } else if (line.length() < 512) line += c;
      else { line = ""; discarding = true; Serial.println("Frame overflow; discarded"); }
    }
  }
  unsigned long count() const { return received; }
};
class BikeGateway {
  TelemetryBuffer telemetry;
public:
  void begin() { Serial.begin(115200); }
  void update() { telemetry.ingest(Serial); }
};
BikeGateway bike;
void setup() { bike.begin(); }
void loop() { bike.update(); delay(1); }
