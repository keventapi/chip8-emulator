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
        self.sp = 0

        self.delay_timer = 0
        self.sound_timer = 0

        self.display = [[0] * 64 for _ in range(32)]

        self.keys = [0]*16

        self.running = True


    def load_rom(self, file_name):
        with open(file_name, 'rb') as f:
            rom = f.read()
        for i, byte in enumerate(rom):
            self.memory[0x200+i] = byte
        

    def cycle(self):
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        n1 = (opcode & 0xF000) >> 12
        n2 = (opcode & 0x0F00) >> 8
        n3 = (opcode & 0x00F0) >> 4
        n4 = opcode & 0x000F

        self.pc += 2

        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1
        
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