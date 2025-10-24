import time

class Chip8:
    def __init__(self):
        self.memory = [0]*4096

        #registrador de 8 bits
        self.v = [0]*16

        #registrador de endereço
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
        if self.sp >= 15:
            raise Exception("stack overflow")
        
        self.sp += 1
        self.stack[self.sp] = self.pc+2 #transformar self.pc em parametro depois

    def pop(self):
        if self.sp < 0:
            raise Exception("stack underflow")
        top = self.stack[self.sp]
        self.sp -= 1
        return top

    def load_rom(self, file_name):
        with open(file_name, 'rb') as f:
            rom = f.read()
        for i, byte in enumerate(rom):
            self.memory[0x200+i] = byte
        
    def clear_screen(self):
        pass

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

        if n1 == 0xA:
            self.I = opcode & 0x0FFF
        


        

        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1
        
        self.pc += 2

        print(f"PC: {self.pc - 2:03X}, Opcode: {opcode:04X}")

    def run(self):
        while self.running:
            self.cycle()
            time.sleep(1/500)



rom_test = bytes([0xA2, 0xF0, 0x60, 0x0C])

# salvar num arquivo temporário
with open("test.rom", "wb") as f:
    f.write(rom_test)

chip = Chip8()
chip.load_rom("test.rom")

for _ in range(4):
    chip.cycle()