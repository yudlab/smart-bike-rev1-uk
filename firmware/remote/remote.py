"""Remote menu domain model. Hardware display, trackball and radio adapters pending."""
class RemoteMenu:
    items = ('Alarm', 'Lock request', 'Auto lock', 'Night mode')
    def __init__(self):
        self.index = 0
    def move(self, direction):
        self.index = (self.index + direction) % len(self.items)
        return self.items[self.index]
    def select(self):
        # UI intent only; authenticated acknowledgement must update real state.
        return {'intent': self.items[self.index], 'status': 'NOT_SENT'}
