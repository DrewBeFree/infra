#!/usr/bin/env python3
import subprocess
import time
import sys
import signal

# GPU Temperature thresholds to fan percentage mapping
# (GPU temp C, fan percentage hex)
THRESHOLDS = [
    (50, 0x1e),  # Under 50C -> 30%
    (65, 0x28),  # 50-65C   -> 40%
    (75, 0x37),  # 65-75C   -> 55%
    (82, 0x4b),  # 75-82C   -> 75%
    (100, 0x64), # Above 82C -> 100%
]

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}\nExit code: {e.returncode}\nStderr: {e.stderr}", file=sys.stderr)
        return None

def restore_idrac_control():
    print("Restoring iDRAC automatic fan control...")
    run_cmd("ipmitool raw 0x30 0x30 0x01 0x00")

def set_manual_fan_speed(pct):
    print(f"Setting fans to manual control at {pct}% speed...")
    # Enable manual control
    run_cmd("ipmitool raw 0x30 0x30 0x01 0x01")
    # Set speed
    run_cmd(f"ipmitool raw 0x30 0x30 0x02 0xff {hex(pct)}")

def get_gpu_temp():
    out = run_cmd("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits")
    if out and out.isdigit():
        return int(out)
    return None

def get_cpu_temp():
    # Read the coretemp sensor if present
    max_temp = 30
    try:
        # Scan system thermal zones
        import glob
        for path in glob.glob("/sys/class/thermal/thermal_zone*/temp"):
            with open(path, "r") as f:
                temp = int(f.read().strip()) / 1000
                if temp > max_temp:
                    max_temp = temp
    except Exception as e:
        print(f"Error reading CPU temp: {e}", file=sys.stderr)
    return int(max_temp)

def handle_exit(signum, frame):
    print(f"Received signal {signum}. Cleaning up...")
    restore_idrac_control()
    sys.exit(0)

def main():
    # Register exit handlers
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    # Disable Third-Party PCIe card cooling override first (so manual speed works)
    print("Disabling Dell third-party PCIe card cooling override...")
    run_cmd("ipmitool raw 0x30 0xce 0x00 0x16 0x05 0x00 0x00 0x00 0x05 0x00 0x01 0x00 0x00")

    current_pct = None

    try:
        while True:
            gpu_temp = get_gpu_temp()
            cpu_temp = get_cpu_temp()

            if gpu_temp is None:
                print("Warning: Could not read GPU temperature! Restoring safety default.", file=sys.stderr)
                restore_idrac_control()
                current_pct = None
                time.sleep(30)
                continue

            # Find the target fan speed based on highest temperature (GPU or CPU)
            max_temp = max(gpu_temp, cpu_temp)
            target_pct = THRESHOLDS[-1][1]  # Default to max safety
            for temp_limit, pct in THRESHOLDS:
                if max_temp <= temp_limit:
                    target_pct = pct
                    break

            if target_pct != current_pct:
                set_manual_fan_speed(target_pct)
                current_pct = target_pct

            print(f"Status: GPU Temp: {gpu_temp}C, CPU Temp: {cpu_temp}C, Fan Speed: {current_pct}%")
            time.sleep(15)

    except Exception as e:
        print(f"Exception in main loop: {e}", file=sys.stderr)
    finally:
        restore_idrac_control()

if __name__ == "__main__":
    main()
