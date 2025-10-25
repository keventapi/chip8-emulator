import os

class Display:
    def __init__(self):
        self.display = [[0] * 64 for _ in range(32)]
    
    def clear_screen(self):
        self.display = [[0] * 64 for _ in range(32)]

    def render_display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        for y in range(32):
            linha = ''.join('█' if self.display[y][x] else ' ' for x in range(64))
            print(linha)

    def draw_sprite(self, n, sprite, x_pos, y_pos):
        collision = 0
        for linha in range(n):
                byte = sprite[linha]
                for bit in range(8):
                    pixel = (byte >> (7-bit)) & 1
                    display_y = (y_pos + linha) % 32
                    display_x = (x_pos + bit) % 64
                    if pixel == 1:
                        if self.display[display_y][display_x] == 1:
                            collision = 1
                        self.display[display_y][display_x] ^= 1
        return collision