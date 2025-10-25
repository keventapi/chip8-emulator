from chip8.memory import Memory
from chip8.display import Display
from chip8.keyboard import Keyboard
from chip8.cpu import Chip8
import loader



def start():
    game = loader.choose_game()

    memory = Memory()
    display = Display()
    keyboard = Keyboard()

    chip = Chip8(memory, display, keyboard)
    chip.keyboard.start()
    chip.memory.load_rom(game)
    chip.run()


if __name__ == "__main__":
    start()