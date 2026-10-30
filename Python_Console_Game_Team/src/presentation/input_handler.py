

class InputHandler:
    def __init__(self, renderer):
        self.renderer = renderer

    def get_key(self):
        return self.renderer.get_key()