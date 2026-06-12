import board
import busio
import displayio
import adafruit_ssd1306

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import Pins
from kmk.modules.layers import LayersModule
from kmk.modules.encoder import EncoderHandler

keyboard = KMKKeyboard()

keyboard.matrix = Pins([board.D0, board.D1, board.D2], value_when_pressed=False)

layers = LayersModule()
keyboard.modules.append(layers)

encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)

displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

def update_display(line1, line2="12:00 | OK"):
    display.fill(0)
    display.text(line1, 0, 4, 1)
    display.text(line2, 0, 20, 1)
    display.show()

encoder_handler.pins = ((board.D3, board.D4, False),)

encoder_handler.map = (
    ((KC.VOLU, KC.VOLD),),
    ((KC.WH_U, KC.WH_D),),
    ((KC.UP, KC.DOWN),),
    ((KC.TO(0), KC.TO(0)),), 
)

keyboard.keymap = [
    [KC.MUTE, KC.MPRV, KC.MNXT],
    [KC.LSHIFT(KC.F), KC.S, KC.E],
    [KC.LCTRL(KC.Z), KC.LCTRL(KC.X), KC.LCTRL(KC.V)],
    [KC.NO, KC.NO, KC.NO],
]

import digitalio
enc_button = digitalio.DigitalInOut(board.D5)
enc_button.direction = digitalio.Direction.INPUT
enc_button.pull = digitalio.Pull.UP

last_btn_state = True
current_mode = 0
selected_layer = 0
layer_names = ["1. MULTIMEDIA", "2. FUSION 360", "3. PROD (TXT)"]

update_display(layer_names[0])

def handle_encoder_click():
    global last_btn_state, current_mode, selected_layer
    
    btn_state = enc_button.value
    if not btn_state and last_btn_state:
        import time
        time.sleep(0.04)
        
        if current_mode == 0:
            current_mode = 1
            selected_layer = layers.current_layer
            layers.activate_layer(3)
            update_display("[SELECIONAR]", f"-> {layer_names[selected_layer]}")
        else:
            current_mode = 0
            layers.deactivate_layer(3)
            layers.go_to_layer(selected_layer)
            update_display(layer_names[selected_layer])
            
        last_btn_state = False
    elif btn_state:
        last_btn_state = True

enc_a = digitalio.DigitalInOut(board.D3)
enc_b = digitalio.DigitalInOut(board.D4)
enc_a.direction = digitalio.Direction.INPUT
enc_a.pull = digitalio.Pull.UP
enc_b.direction = digitalio.Direction.INPUT
enc_b.pull = digitalio.Pull.UP
last_a = enc_a.value

def handle_encoder_rotation():
    global last_a, selected_layer
    if current_mode == 1:
        state_a = enc_a.value
        if state_a != last_a and state_a == 0:
            if enc_b.value != state_a:
                selected_layer = (selected_layer + 1) % 3
            else:
                selected_layer = (selected_layer - 1) % 3
            update_display("[SELECIONAR]", f"-> {layer_names[selected_layer]}")
            import time
            time.sleep(0.08)
        last_a = state_a

def macro_loop():
    handle_encoder_click()
    handle_encoder_rotation()

keyboard.before_matrix_report.append(macro_loop)

if __name__ == '__main__':
    keyboard.go()