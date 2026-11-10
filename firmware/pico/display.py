class SpeedDisplay:
    """Adapter for a verified TFT driver; no assumed ST7789/ILI controller."""
    def __init__(self, driver):
        self.driver = driver
    def render(self, speed, mph=False):
        self.driver.fill(0)
        self.driver.text('%.1f' % speed, 20, 40, 0xFFFF)
        self.driver.text('mph' if mph else 'km/h', 20, 70, 0x07FF)
        # Some drivers require show(); supply an adapter matching this contract.
        self.driver.show()
