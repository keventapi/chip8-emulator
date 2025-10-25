from pynput import keyboard

class Keyboard:
    def __init__(self):
        self.keys = [0]*16
        self.key_map = {
            '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
            'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
            'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
            'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
        }

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
    
    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def is_pressed(self, index):
        if 0 <= index < 16:
            return self.keys[index] == 1  
        return False

    def on_press(self, key):
        try:
            k = key.char.lower()
            if k in self.key_map:
                self.keys[self.key_map[k]] = 1
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            k = key.char.lower()
            if k in self.key_map:
                self.keys[self.key_map[k]] = 0
        except AttributeError:
            pass
    