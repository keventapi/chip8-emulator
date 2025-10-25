class Memory:
    def __init__(self):
        self.memory = [0]*4096

        self._load_fontset()
    
    def _load_fontset(self):
        """Carrega o conjunto de fontes CHIP-8 na memória a partir do endereço 0x000."""
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        
        for i, byte in enumerate(fontset):
            self.memory[i] = byte

    def write(self, value, address):
        """Escreve um byte (value) no endereço de memória especificado."""
        if not 0 <= address < len(self.memory):
            raise IndexError(f"Endereço {address:#04x} fora da faixa da memória.")
        self.memory[address] = value & 0xFF

    def read(self, address):
        """pega da memoria atraves do endereço de memoria passado como parametro"""
        if not 0 <= address < len(self.memory):
            raise IndexError(f"Endereço {address:#04x} fora da faixa da memória.")
        return self.memory[address]

    def read_in_range(self, I, n):
        """pega valor da memoria de I ate I+n"""
        return self.memory[I : I+n]

    def load_rom(self, file_name: str, starting: int = 0x200):
        """Carrega uma ROM binária na memória a partir do endereço padrão 0x200."""
        with open(file_name, "rb") as f:
            rom = f.read()

        end = starting + len(rom)
        if end > len(self.memory):
            raise MemoryError("ROM excede o limite da memória disponível.")

        self.memory[starting:end] = rom