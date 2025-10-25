import time
import random

class Chip8:
    def __init__(self, memory, display, keyboard, debug=False):
        self.debug = debug

        self.memory = memory

        #registradores (varia de 0x0 ate 0xF)
        self.v = [0]*16

        #pointeiro para acesso da memoria
        self.I = 0

        #onde se começa a ler os comandos escritos antes disso é espaço reservado do proprio chip
        self.pc = 0x200

        #pilha de chamadas e ponteiro da pilha para controle
        self.stack = [0]*16
        self.sp = -1

        self.delay_timer = 0
        self.sound_timer = 0

        self.display = display

        self.keyboard = keyboard

        self.running = True

    def push(self, value):
        """
        coloca na pilha o parametro value para ser chamado de volta outro momento
        """
        if self.sp >= len(self.stack) - 1:
            raise Exception("stack overflow")
        self.sp += 1
        self.stack[self.sp] = value

    def pop(self):
        """
        tira o ultimo item adicionado na pilha e 
        retorna ele, depois decrementa o ponteiro para onde esta a pilha no momento atual
        """
        if self.sp < 0:
            raise Exception("stack underflow")
        value = self.stack[self.sp]
        self.sp -= 1
        return value

    def log_opcode(self, opcode):
        """
        Adiciona o opcode atual e o PC (Program Counter) 
        ao final do arquivo 'opcode_log.txt'.
        """
        # Formata o opcode e o PC em hexadecimal para melhor leitura
        pc_hex = f"{self.pc - 2:04X}"  # PC - 2 porque ele já foi incrementado no fetch
        opcode_hex = f"{opcode:04X}"
        
        log_entry = f"PC: {pc_hex} | Opcode: {opcode_hex}\n"

        # Abre o arquivo em modo 'a' (append) e adiciona a linha
        try:
            with open("opcode_log.txt", "a") as f:
                f.write(log_entry)
        except Exception as e:
            # Em caso de erro (permissão, etc.), exibe na tela para debug
            print(f"Erro ao escrever no log: {e}")

    def is_waiting_input(self, x):
        for i in range(16):
            if self.keyboard.is_pressed(i):
                self.v[x] = i
                return False
        return True

    def cycle(self):        
        # Cada instrução (opcode) do CHIP-8 ocupa 2 bytes.
        # Aqui unimos o byte mais significativo (self.memory[pc]) e o menos significativo (self.memory[pc + 1])
        # em um único valor de 16 bits, usando deslocamento de bits e OR bit a bit.

        opcode = (self.memory.read(self.pc) << 8) | self.memory.read(self.pc+1)

        #aqui são separados em nibbles que são unidades menores para leitura
        n1 = (opcode & 0xF000) >> 12
        n2 = (opcode & 0x0F00) >> 8
        n3 = (opcode & 0x00F0) >> 4
        n4 = opcode & 0x000F

        #debug
        if self.debug:
            self.log_opcode(opcode)

        #implementação das instruções
        if opcode == 0x00E0:
            self.display.clear_screen()

        if opcode == 0x00EE:
            self.pc = self.pop()
            return
        
        if n1 == 0x1:
            self.pc = (opcode & 0x0FFF)
            return

        if n1 == 0x2:
            self.push(self.pc+2) #salva na stack a proxima instrução
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
                self.v[0xF] = 1 if result > 0xFF else 0
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
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            n = opcode & 0x000F

            sprite = self.memory.read_in_range(self.I, n)

            self.v[0xF] = self.display.draw_sprite(n, sprite, self.v[x], self.v[y])
                    
        if n1 == 0xE:
            x = (opcode & 0x0F00) >> 8
            instruction = (opcode & 0x00FF)
            key_index = self.v[x] & 0xF

            if instruction == 0x9E:
                if self.keyboard.is_pressed(key_index):
                    self.pc += 2 

            elif instruction == 0xA1:
                if not self.keyboard.is_pressed(key_index):
                    self.pc += 2

        if n1 == 0xF:
            x = (opcode & 0x0F00) >> 8
            instruction = (opcode & 0x00FF)

            if instruction == 0x07:
                self.v[x] = self.delay_timer
            
            if instruction == 0x0A:
                if self.is_waiting_input(x):
                    return #evita o avanço do program counter mantendo na instrução atual 
                
            
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
                self.memory.write((value // 100), self.I)
                self.memory.write((value//10) % 10, self.I+1)
                self.memory.write((value%10), self.I+2)

            if instruction == 0x55:
                for i in range(x+1):
                    self.memory.write(self.v[i], self.I+i)
            
            if instruction == 0x65:
                for i in range(x+1):
                    self.v[i] = self.memory.read(self.I+i)

        self.pc += 2

    def decrement_delay(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1

    def run(self):
        while self.running:
            #ticker para ler instruções
            for _ in range(10):
                self.cycle()

            self.display.render_display()

            self.decrement_delay()

            time.sleep(1/60)