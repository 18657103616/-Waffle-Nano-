import socket
from pynput import keyboard

NANO_IP = '192.168.43.218'
PORT = 5000

print("正在连接 Waffle Nano...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((NANO_IP, PORT))
    print("已连接！按 ESC 退出")
    print("=" * 40)
    print("按键映射：")
    print("  1 = 抚摸宠物(摇尾巴)")
    print("  2 = 打开菜单/食物")
    print("  3 = 换肤色")
    print("  4 = 睡觉")
    print("  ESC = 退出")
    print("=" * 40)
except Exception as e:
    print("连接失败:", e)
    sock.close()
    exit()

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            char = key.char.encode('utf-8')
            sock.sendall(char)
            print("发送:", key.char)
        elif key == keyboard.Key.esc:
            sock.sendall(b'\x1b')
            print("发送: ESC")
            return False
    except Exception as e:
        print("发送失败:", e)
        return False

def on_release(key):
    pass

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    print("\n程序已停止")
finally:
    sock.close()