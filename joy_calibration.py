import time
import json
from evdev import InputDevice, categorize, ecodes, list_devices

def find_joystick():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if 'joystick' in device.name.lower() or 'gamepad' in device.name.lower():
            print(f"Using joystick: {device.name} at {device.path}")
            return device
    raise RuntimeError("No joystick found")

def calibrate_joystick():
    joystick = find_joystick()
    axis_data = {}

    print("\n🕹️ Joystick Calibration Started")
    print("Move all joystick axes to their full range.")
    print("Press Ctrl+C when you're done.\n")

    try:
        for event in joystick.read_loop():
            if event.type == ecodes.EV_ABS:
                axis_code = event.code
                axis_name = ecodes.ABS.get(axis_code, f"ABS_{axis_code}")
                value = event.value

                if axis_name not in axis_data:
                    axis_data[axis_name] = {'min': value, 'max': value}
                else:
                    axis_data[axis_name]['min'] = min(axis_data[axis_name]['min'], value)
                    axis_data[axis_name]['max'] = max(axis_data[axis_name]['max'], value)

                axis_data[axis_name]['center'] = (axis_data[axis_name]['min'] + axis_data[axis_name]['max']) // 2

                print(f"\r{axis_name}: min={axis_data[axis_name]['min']} max={axis_data[axis_name]['max']} center={axis_data[axis_name]['center']}", end='')

    except KeyboardInterrupt:
        print("\n\n✅ Calibration Complete!\n")
        print("Calibration Data:")
        for axis, data in axis_data.items():
            print(f"{axis}: min={data['min']}, max={data['max']}, center={data['center']}")

        # Save to file
        with open("joystick_calibration.json", "w") as f:
            json.dump(axis_data, f, indent=4)
        print("\n📁 Calibration data saved to 'joystick_calibration.json'.")

if __name__ == "__main__":
    calibrate_joystick()
