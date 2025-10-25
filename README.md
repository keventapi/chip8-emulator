# Emulador CHIP-8 em Python

> Para usar, instale o `pynput` com:
>
> ```bash
> pip install pynput
> ```

---

## Classe `Chip8`

### Construtor `__init__`

- Reserva uma lista para simular a memória de 4 KB presente no CHIP-8.
- Reserva 16 registradores (`V0` a `VF`), chamados de `V`.
- Define um ponteiro de memória chamado `I`.
- Seta o `PC` (program counter) em `0x200`, que é onde os programas começam a ser lidos.
- Cria a pilha de chamadas, chamada de `stack`.
- Seta o ponteiro da pilha (`SP`), que aponta para a posição onde o próximo elemento será adicionado.
- Inicializa os timers:
  - `delay_timer` — usado como flag para sincronização em jogos ou programas.
  - `sound_timer` — usado para som ou alertas temporizados.
- Inicializa a lista de teclas (`keys`) para checar se estão pressionadas (0 = não pressionada, 1 = pressionada).
- Define o estado do emulador (`running`) como ligado.
- Carrega as fontes (sprites dos números) na memória.

---

### Métodos `push` e `pop`

- **`push(value)`**  
  Adiciona um valor na pilha:
  - Incrementa o ponteiro da pilha (`SP`).
  - Armazena o valor no topo da pilha.
  - Levanta exceção em caso de *stack overflow*.

- **`pop()`**  
  Remove e retorna o último elemento da pilha:
  - Decrementa o ponteiro da pilha (`SP`).
  - Levanta exceção em caso de *stack underflow*.

---

### Método `load_rom(file_name)`

- Lê a ROM e armazena na memória a partir do endereço `0x200`.

---

### Método `clear_screen()`

- Reseta todos os pixels da tela para `0`.

---

### Método `log_opcode(opcode)`

- Serve para debug, mostrando o opcode atual e registradores, se necessário.

---

### Método `render_display()`

- Converte os pixels `1` em blocos preenchidos (`█`) e os `0` em espaços.
- Limpa a tela do terminal a cada chamada para simular atualização gráfica.

---

### Método `cycle()`

Responsável por interpretar os **opcodes** do CHIP-8.  
Cada instrução ocupa 2 bytes. O opcode é formado por:

```python
opcode = (memory[PC] << 8) | memory[PC + 1]
```

Os nibbles do opcode são extraídos para facilitar a leitura:

```python
n1 = (opcode & 0xF000) >> 12
n2 = (opcode & 0x0F00) >> 8
n3 = (opcode & 0x00F0) >> 4
n4 = opcode & 0x000F
```

#### Principais instruções implementadas:

| Opcode | Nome / Função | Descrição |
|--------|---------------|-----------|
| `00E0` | CLS | Limpa o display. |
| `00EE` | RET | Retorna de uma sub-rotina. PC recebe o valor do topo da pilha e decrementa SP. |
| `1nnn` | JP addr | Salta para o endereço `nnn`. |
| `2nnn` | CALL addr | Chama sub-rotina em `nnn`. Salva PC na pilha antes de saltar. |
| `3xkk` | SE Vx, byte | Pula a próxima instrução se `Vx == kk`. |
| `4xkk` | SNE Vx, byte | Pula a próxima instrução se `Vx != kk`. |
| `5xy0` | SE Vx, Vy | Pula a próxima instrução se `Vx == Vy`. |
| `6xkk` | LD Vx, byte | Define `Vx = kk`. |
| `7xkk` | ADD Vx, byte | Adiciona `kk` a `Vx`. |
| `8xy0` | LD Vx, Vy | Define `Vx = Vy`. |
| `8xy1` | OR Vx, Vy | `Vx = Vx OR Vy` (bitwise). |
| `8xy2` | AND Vx, Vy | `Vx = Vx AND Vy` (bitwise). |
| `8xy3` | XOR Vx, Vy | `Vx = Vx XOR Vy` (bitwise). |
| `8xy4` | ADD Vx, Vy | Soma `Vx + Vy`, define `VF = carry`. |
| `8xy5` | SUB Vx, Vy | Subtrai `Vy` de `Vx`, define `VF = NOT borrow`. |
| `8xy6` | SHR Vx {, Vy} | Shift-right `Vx` em 1, define `VF` com LSB antes do shift. |
| `8xy7` | SUBN Vx, Vy | Subtrai `Vx` de `Vy`, define `VF = NOT borrow`. |
| `8xyE` | SHL Vx {, Vy} | Shift-left `Vx` em 1, define `VF` com MSB antes do shift. |
| `9xy0` | SNE Vx, Vy | Pula a próxima instrução se `Vx != Vy`. |
| `Annn` | LD I, addr | Define `I = nnn`. |
| `Bnnn` | JP V0, addr | Salta para `nnn + V0`. |
| `Cxkk` | RND Vx, byte | `Vx = random byte AND kk`. |
| `Dxyn` | DRW Vx, Vy, nibble | Desenha sprite de `n` bytes em `(Vx, Vy)`. Define `VF` se houver colisão. |
| `Ex9E` | SKP Vx | Pula próxima instrução se tecla `Vx` estiver pressionada. |
| `ExA1` | SKNP Vx | Pula próxima instrução se tecla `Vx` **não** estiver pressionada. |
| `Fx07` | LD Vx, DT | Define `Vx = delay_timer`. |
| `Fx0A` | LD Vx, K | Espera tecla ser pressionada e armazena o valor em `Vx`. |
| `Fx15` | LD DT, Vx | Define `delay_timer = Vx`. |
| `Fx18` | LD ST, Vx | Define `sound_timer = Vx`. |
| `Fx1E` | ADD I, Vx | Adiciona `Vx` a `I`. |
| `Fx29` | LD F, Vx | Define `I` como endereço do sprite de dígito hexadecimal de `Vx`. |
| `Fx33` | LD B, Vx | Armazena representação BCD de `Vx` em `I, I+1, I+2`. |
| `Fx55` | LD [I], Vx | Armazena registradores `V0` até `Vx` na memória a partir de `I`. |
| `Fx65` | LD Vx, [I] | Lê registradores `V0` até `Vx` da memória a partir de `I`. |

> Nota: o incremento do `PC` em `+2` é feito no final de cada ciclo, exceto para instruções de salto (`JP`, `CALL`) ou espera (`LD Vx, K`).

---

### Método `run()`

- Executa o ciclo do emulador indefinidamente enquanto `running = True`.
- Cada frame processa 10 ciclos de instrução.
- Renderiza a tela a 60 Hz.
- Decrementa `delay_timer` e `sound_timer` a 60 Hz.
- Adiciona um `sleep(1/60)`


Referencia utilizada: [Chip-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#0.0).
