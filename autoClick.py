from pynput import keyboard
import pyautogui

def autoClick():
    pyautogui.click(800,800)

def on_press(key):
    try:
        print('Alphanumeric key pressed: {0} '.format(
            key.char))
    except AttributeError:
        print('special key pressed: {0}'.format(
            key))

def on_release(key):
    print('Key released: {0}'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False
    elif key == keyboard.Key.enter:
        print('autoClick!')
        autoClick()



# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()