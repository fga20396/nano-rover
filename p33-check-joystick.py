
from evdev import InputDevice, list_devices

for dev_path in list_devices():
    dev = InputDevice(dev_path)
    print(f"Device: {dev.name}")
    for code in dev.capabilities().get(3, []):  # 3 = EV_ABS
        print(f"  Axis: {code}"
