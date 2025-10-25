import time
import random
from pynput import keyboard
import os


class Chip8:
    def __init__(self):
        self.memory = [0]*4096

        self.v = [0]*16

        self.I = 0

        self.pc = 0x200

        self.stack = [0]*16
        self.sp = -1

        self.delay_timer = 0
        self.sound_timer = 0

        self.display = [[0] * 64 for _ in range(32)]

        self.keys = [0]*16

        self.running = True

    def push(self):
        if self.sp >= len(self.stack):
            raise Exception("stack overflow")
        self.stack[self.sp] = self.pc
        self.sp += 1

    def pop(self):
        if self.sp == 0:
            raise Exception("stack underflow")
        self.sp -= 1
        return self.stack[self.sp]

    def load_rom(self, file_name):
        with open(file_name, 'rb') as f:
            rom = f.read()
        for i, byte in enumerate(rom):
            self.memory[0x200+i] = byte
        
    def clear_screen(self):
        self.display = [[0] * 64 for _ in range(32)]

    def render_display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        for y in range(32):
            linha = ''.join('█' if self.display[y][x] else ' ' for x in range(64))
            print(linha)

    def cycle(self):
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        n1 = (opcode & 0xF000) >> 12
        n2 = (opcode & 0x0F00) >> 8
        n3 = (opcode & 0x00F0) >> 4
        n4 = opcode & 0x000F

        if opcode == 0x00E0:
            self.clear_screen()

        if opcode == 0x00EE:
            self.pc = self.pop()

        if n1 == 0x1:
            self.pc = (opcode & 0x0FFF)
            return

        if n1 == 0x2:
            self.push()
            self.pc = (opcode & 0x0FFF)
            return
            
        if n1 == 0x3:
            x = (opcode & 0x0F00) >> 8
            kk = (opcode & 0x00FF)

            if kk == self.v[x]:
                self.pc += 2

        if n1 == 0x4:
            x = (opcode & 0x0F00) >> 8
            kk = (opcode & 0x00FF)
            if self.v[x] != kk:
                self.pc += 2

        if n1 == 0x5:
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] == self.v[y]:
                self.pc += 2
        
        if n1 == 0x6:
            x = (opcode & 0x0F00) >> 8
            kk = (opcode & 0x00FF)
            self.v[x] = kk

        if n1 == 0x7:
            x = (opcode & 0x0F00) >> 8
            kk = (opcode & 0x00FF)
            self.v[x] = (self.v[x] + kk) & 0xFF

        if n1 == 0x8:
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4

            if n4 == 0x0:
                self.v[x] = self.v[y]

            elif n4 == 0x1:
                self.v[x] = (self.v[x] | self.v[y])

            elif n4 == 0x2:
                self.v[x] = (self.v[x] & self.v[y])

            elif n4 == 0x3:
                self.v[x] = (self.v[x] ^ self.v[y])

            elif n4 == 0x4:
                result = self.v[x] + self.v[y]
                self.v[0xF] = 1 if result > 0xFF else 0  # carry
                self.v[x] = result & 0xFF

            elif n4 == 0x5:
                self.v[0xF] = 1 if self.v[x] >= self.v[y] else 0
                self.v[x] = (self.v[x] - self.v[y]) & 0xFF
            
            elif n4 == 0x6:
                lsb = self.v[x] & 0x1
                self.v[x] >>= 1
                self.v[0xF] = 1 if lsb else 0
            
            elif n4 == 0x7:
                self.v[0xF] = 1 if self.v[y] >= self.v[x] else 0
                self.v[x] = (self.v[y] - self.v[x]) & 0xFF
            
            elif n4 == 0xE:
                msb = (self.v[x] & 0x80) >> 7
                self.v[0xF] = msb
                self.v[x] = (self.v[x] << 1) & 0xFF

        if n1 == 0x9:
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] != self.v[y]:
                self.pc += 2

        if n1 == 0xA:
            self.I = opcode & 0x0FFF
        
        if n1 == 0xB:
            self.pc = ((opcode & 0x0FFF) + self.v[0]) & 0x0FFF 

        if n1 == 0xC:
            x = (opcode & 0x0F00) >> 8
            kk = (opcode & 0x00FF)
            self.v[x] = random.randint(0, 255) & kk 

        if n1 == 0xD:
            self.v[0xF] = 0

            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            n = opcode & 0x000F
            sprite = self.memory[self.I : self.I + n]
            for linha in range(n):
                byte = sprite[linha]
                for bit in range(8):
                    pixel = (byte >> (7-bit)) & 1
                    display_y = (self.v[y] + linha) % 32
                    display_x = (self.v[x] + bit) % 64
                    if pixel == 1:
                        if self.display[display_y][display_x] == 1:
                            self.v[0xF] = 1
                        
                        self.display[display_y][display_x] ^= 1
                    
        if n1 == 0xE:
            x = (opcode & 0x0F00) >> 8
            instruction = (opcode & 0x00FF)
            if instruction == 0x9E:
                key_index = self.v[x] & 0xF
                if self.keys[key_index] == 1:
                    self.pc += 2 

            if instruction == 0xA1:
                if self.keys[self.v[x]] == 0:
                    self.pc += 2

        if n1 == 0xF:
            x = (opcode & 0x0F00) >> 8
            instruction = (opcode & 0x00FF)
            if instruction == 0x07:
                self.v[x] = self.delay_timer
            
            if instruction == 0x0A:
                pressed = False
                for i in range(16):
                    if self.keys[i] == 1:
                        pressed = True
                        self.v[x] = i
                        break
                
                if not pressed:
                    return
            
            if instruction == 0x15:
                self.delay_timer = self.v[x]
            
            if instruction == 0x18:
                self.sound_timer = self.v[x]
            
            if instruction == 0x1E:
                self.I = (self.I + self.v[x]) & 0x0FFF

            if instruction == 0x29:
                self.I = self.v[x] * 5
            
            if instruction == 0x33:
                value = self.v[x]
                self.memory[self.I] = (value // 100)
                self.memory[self.I+1] = (value // 10) % 10
                self.memory[self.I+2] = (value % 10)

            if instruction == 0x55:
                for i in range(x+1):
                    self.memory[self.I+i] = self.v[i]
            
            if instruction == 0x65:
                for i in range(x+1):
                    self.v[i] = self.memory[self.I + i]

        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1
        
        self.pc += 2

    def run(self):
        while self.running:
            for _ in range(150):
                self.cycle()
            self.render_display()
            time.sleep(1/30)

chip = Chip8()


key_map = {
    '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
    'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
    'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
    'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
}

def on_press(key):
    try:
        k = key.char.lower()
        if k in key_map:
            chip.keys[key_map[k]] = 1
    except AttributeError:
        pass

def on_release(key):
    try:
        k = key.char.lower()
        if k in key_map:
            chip.keys[key_map[k]] = 0
    except AttributeError:
        pass

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

chip.load_rom("MISSILE")

chip.run()