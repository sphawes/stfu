#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path

def has_gdb_on_path(gdb) -> bool:

    try:
        gdb_version = subprocess.check_output([gdb, "--version"], text=True).strip()
    except subprocess.CalledProcessError:
        raise Exception("Your gdb installation appears to be broken. Install on macOS with 'brew install arm-none-eabi-gdb'.")
    return True

def has_dfu_util_on_path() -> bool:

    try:
        gdb_version = subprocess.check_output(["dfu-util", "--version"], text=True).strip()
    except subprocess.CalledProcessError:
        raise Exception("Your dfu-util installation appears to be broken. Install on macOS with 'brew install dfu-util'.")
    return True

def has_st32flash_on_path() -> bool:

    try:
        gdb_version = subprocess.check_output(["stm32flash"], text=True).strip()
    except subprocess.CalledProcessError:
        raise Exception("Your stm32flash installation appears to be broken. Install on macOS with 'brew install stm32flash'.")
    return True


def find_bmp() -> Path:
    candidates = [
        *Path("/dev/serial/by-id/").glob(
            "usb-Black_Sphere_Technologies_Black_Magic_Probe_*-if00"
        ),
        *Path("/dev/").glob("cu.usbmodem*1"),
    ]

    if not candidates:
        raise RuntimeError("unable to find to black magic probe")

    return candidates[0]

def find_uart() -> Path:
    candidates = [
        *Path("/dev/").glob("cu.usbserial*"),
    ]

    if not candidates:
        raise RuntimeError("unable to find uart serial port")

    return candidates[0]


def flash_via_gdb(gdb, bmp, firmware, enable_power):
    # accepts .elf files only
    if firmware.suffix != ".elf":
        raise ValueError("firmware must be a .elf file")

    bmp = bmp or find_bmp()

    cmd = [
        f"{gdb}",
        "-nx",
        "--batch",
        "--ex",
        f"target extended-remote {bmp}",
        "--ex",
        "monitor tpwr enable" if enable_power else "monitor tpwr disable",
    ]
    if enable_power:
        cmd += ["--ex", "shell sleep 0.1"]
    cmd += [
        "--ex",
        "monitor swdp_scan",
        "--ex",
        "attach 1",
        "--ex",
        "load",
        "--ex",
        "compare-sections",
        "--ex",
        "kill",
        f"{firmware}",
    ]

    print(f"--bmp: {bmp}")
    print(f"--gdb: {gdb}")
    print(f"--enable-power: {enable_power}")

    print("Running GDB: ", " ".join(cmd))
    print()

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print()
        print("############################")
        print("Programming failed!")
    except FileNotFoundError:
        print()
        print("############################")
        print("arm-none-eabi-gdb not found, either set PATH or specify --gdb.")
    else:
        print()
        print("############################")
        print("Programming complete!")

def flash_via_dfu(firmware):
    # accepts .bin files only
    if firmware.suffix != ".bin":
        raise ValueError("firmware must be a .bin file")

    cmd = [
        "dfu-util",
        "-s",
        "0x08000000",
        "-a",
        "0",
        "-D",
        f"{firmware}"
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print()
        print("############################")
        print("Programming failed!")
    except FileNotFoundError:
        print()
        print("############################")
        print("dfu-util not found or bad firmware path")
    else:
        print()
        print("############################")
        print("Programming complete!")

    
    
def flash_via_uart(firmware, uart):
    # accepts .bin files only
    if firmware.suffix != ".bin":
        raise ValueError("firmware must be a .bin file")

    uart = uart or find_uart()

    cmd = [
        "stm32flash",
        "-w",
        f"{firmware}",
        "-b",
        "115200",
        "-v",
        "-g",
        "0x0",
        f"{uart}"
    ]

    print(f"- uart: {uart}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print()
        print("############################")
        print("Programming failed!")
    except FileNotFoundError:
        print()
        print("############################")
        print("stm32flash not found or bad firmware path")
    else:
        print()
        print("############################")
        print("Programming complete!")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("method")
    parser.add_argument("firmware", type=Path)
    parser.add_argument("--gdb", type=Path, default="arm-none-eabi-gdb")
    parser.add_argument("--bmp", type=Path, default=None)
    parser.add_argument("--uart", type=Path, default=None)
    parser.add_argument("--enable-power", action="store_true", default=False)

    args = parser.parse_args()

    print("-- STFU: ST Flash Utility --")

    print(f"method: {args.method}")
    print(f"firmware: {args.firmware}")

    print("----------------------------")

    if args.method == "swd":
        if has_gdb_on_path(args.gdb):
            flash_via_gdb(args.gdb, args.bmp, args.firmware, args.enable_power)
            
    elif args.method == "dfu":
        if has_dfu_util_on_path():
            flash_via_dfu(args.firmware)

    elif args.method == "uart":
        if has_st32flash_on_path():
            flash_via_uart(args.firmware, args.uart)

if __name__ == "__main__":
    main()
