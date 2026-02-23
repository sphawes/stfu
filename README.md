# STFU - ST Flash Utility

STM32s are great little chips, and have many ways of getting firmware onto them. Many have a UART bootloader, some have a USB bootloader (DFU), and all are programmable via SWD. Each method has its own tools and arguments, and it's kind of a mess.

STFU unifies all STM32 flashing tools in a tiny little python script. It's super easy to use:

```
stfu dfu path/to/firmware.bin
```

That's it. You tell it what method, and what firmware file. All detection of UART ports, dfu devices, and SWD programmers (currently just Black Magic Probes) happens automatically.

This tool is intended to be used on MacOS only.

## Installation

1. [Install Homebrew](https://brew.sh/) and [install uv](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) if you haven't already.

2. Install dependencies:

    ```
    brew install dfu-util stm32flash arm-none-eabi-gdb
    ```

3. Install STFU:

    ```
    uv tool install git+https://github.com/sphawes/stfu
    ```

Done! `stfu` is now on your PATH.

## Usage

STFU supports three methods of flashing STM32 chips:

- `dfu` - meant for programming chips that support a dfu interface via USB.
- `uart` - meant for programming chips using a USB <-> UART adapter.
- `swd` - mean for programming chips via SWD port and a Black Magic Probe.

STFU requires one of the three methods as an argument, then the path to the firmware file:

```
stfu dfu path/to/firmware.bin
```

### Arguments

All arguments are optional.

- `--gdb` - explicitly define path to gdb executable on your machine. 
    - Default: `arm-none-eabi-gdb`
    - Example: `stfu swd firmware.elf --gdb path/to/gdb`
- `--bmp` - explicitly define path to BMP programming serial port.
    - Default: Searches via regex
    - Example: `stfu swd firmware.elf --bmp path/to/bmp/port`
- `--uart` - explicitly define path to UART serial port.
    - Default: Searches via regex
    - Example: `stfu uart firmware.bin --uart path/to/uart/port`
- `--enable-power` - tells Black Magic Probe to enable its 3.3v rail, so the probe can power the chip itself.
    - Default: `False`
    - Example: `stfu swd firmware.elf --enable-power`

## Caveats

This tool is incredibly opinionated. It was made explicitly to help with programming the specific STM32 chips used in [Opulo](https://www.opulo.io/) hardware, and thus common settings used for Opulo configurations are hard-coded. Please feel free to fork for your own variants, or make a PR with more optional flags for other configuration options.