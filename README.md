# OpenRefMic

[![Static Badge](https://img.shields.io/badge/open_source-hardware-0099B0?logo=opensourcehardware)](https://oshwa.org/)

OpenRefMic is an open hardware design for a reference microphone that fits in the popular 1/2" reference microphone form factor, works with consumer microphone interfaces, and meets or exceeds the performance of professional reference microphones at a vastly reduced total system cost.

![OpenRefMic](img/mic-header-photo.jpg)

<br>

## OpenRefMic v2

OpenRefMic version 2 significantly improves the usability of the mic, with integrated frequency response correction, improved PCB layout, and a simpler and more robust mechanical design.

![v2 improvements](img/v2-improvements.jpg)

<br>

## Critical specs, typical performance

- Frequency Response: 10Hz-20kHz
    - ±1dB from 10Hz 2.5kHz
    - +4-7dB 10Hz-20kHz raw capsule response
    - ±2dB 10Hz-20kHz with integrated EQ filter
- Noise Floor: 17dBA
- Acoustic Overload Point: 118dBSPL
- Sensitivity: 100mV/Pa
- Dimensions: 12.7x92mm
- Parts cost: $50 (not including 3D printed parts)
- Interface: mini-XLR, 48V phantom power

![normalized frequency response](img/normalized-response.png)

![noise floor spectrum](img/noise-spectrum-comparison.png)

<br>

### 1/2" microphone comparison

| Mic             | Interface                   | Frequency Response (20-20k)   | Noise Floor | AOP      | Price               |
|-----------------|-----------------------------|-------------------------------|-------------|----------|---------------------|
| OpenRefMic      | 48V phantom power, mini XLR | +3/-7dB (±2dB with EQ)        | 17dBA       | 118dBSPL | Typically <$60      |
| Dayton EMM-6    | 15-48V phantom power, XLR   | ±2dB                          | 36dBA       | 127dBSPL | $60                 |
| MiniDSP U-MIK 2 | USB-C                       | Not specified (likely ±2dB)   | 20dBA       | 125dBSPL | $195 + import       |
| PCB 376A32      | 12-48V phantom power, XLR   | ±2dB                          | 15.5dBA     | 137dBSPL | $1,445              |
| B&K 4191        | 200V Lemo                   | <±1dB                         | 20dBA       | 162dBSPL | Ask for price ($$$) |
| GRAS 46AE       | CCP BNC                     | ±2dB                          | 17dBA       | 138dBSPL | Ask for price ($$$) |

<br>

## Project Overview
The core of the OpenRefMic design is a preamplifier that biases an electret microphone from 48V phantom power, buffers the microphone signal, applies a frequency response correction filter, and to sends the signal to a standard microphone interface. The circuit was designed for the [PUI AOM-5024L-HD-F-R](https://puiaudio.com/file/specs-AOM-5024L-HD-F-R.pdf) low noise microphone capsule, and has been built and tested with that part, but should work with most other electret mics. The schematic and PCB layout were designed in KiCAD and are available in the [Preamplifier section](preamplifier/PREAMPLIFIER.md) of the project, along with the [BOM for all electrical and mechanical parts](Bill_of_materials.csv).

<br>

OpenRefMic construction is simple, consisting of a 3D printed housing, the PCB, mic capsule, screw/nut, and optionally an O-ring and dab of UV cure glue. CAD in Fusion360 and STEP formats are in the [Assembly section](assembly/ASSEMBLY.md), along with STLs for the printed parts and a step-by-step construction guide.

<br>

The noise performance of the complete OpenRefMic prototype far exceeds that of comparably-priced measurement microphones, with a flat frequency response suitable as a reference microphone for measuring speakers, distortion, noise emissions, and capturing field recordings. Raw measurement data, compensation curves, and recommendations for applying calibrations to measurements and recordings are in the [Calibration section](calibration/CALIBRATION.md).

<br>

## Project Goals

### Low noise

This is the most important factor of the OpenRefMic project, and all of the other performance metrics and goals are considered "nice to have". While there are several popular affordable measurement microphones on the market (like the Dayton EMM-6), their noise performance ranges from mediocre to poor. Even professional reference microphones tend to prioritize frequency response flatness over noise performance, and very low noise reference microphones are prohibitively expensive for the hobbyist or self-funded experimenter. The video below is an example of the dramatic difference in noise performance between OpenRefMic and the Dayton EMM-6.

[field recording noise comparison](https://user-images.githubusercontent.com/23405416/175431344-0c36cc5d-fb55-48f4-8029-bcf0d835c0a0.mp4)

Low noise is obviously helpful for applications like field recordings or measuring low-level noise emissions, but one area where microphone noise floor is often overlooked is in speaker distortion measurements. Increasing the stimulus and analysis window or moving the microphone closer to the speaker can help resolve lower distortion levels, but those options may not always be feasible for the given speaker or test setup. The graph below is an example of the differences that you might see between distortion measurements with a typical budget measurement mic with a ~34dBA noise floor and an OpenRefMic with ~18dBA noise floor.

![distortion measurement with OpenRefMic vs EMM-6](img/distortion-comparison.png)

<br>

### Flat, omnidirectional frequency response

A reference microphone should have a frequency response that is flat or characterized well enough that it can be understood how measurements and recordings relate to absolute physical constants. Some aberrations in the off-axis response is expected, particularly at very high frequencies, but the design of the housing, porting, and front grille should minimize directional effects as much as possible. In cases where a flat frequency response is not achievable, the response should be characterized and a process should be defined to apply reciprocal filters to correct recordings.

The microphone element in OpenRefMic has a very low noise floor, but it does not have a flat frequency response. See the calibration page for a compensation curve and filter settings to correct measurements and recordings. 

<br>

### Compatibility with "prosumer" audio interfaces

Professional reference microphones typically require interfaces that are uncommon outside of labratory settings. IEPE current loops over BNC cables on the more affordable end of the spectrum and 200V polarization supplied via LEMO connectors at the other end, where the cable itself is often over $500. The pro audio world has instead standardized on balanced signals and phantom powering over cheap XLR cables, and OpenRefMic is designed to achieve high performance with these affordable interfaces.

<br>

### Low cost

Compatibility with consumer-grade microphone interfaces eliminates the prohibitive costs of an IEPE or LEMO interface, but the parts availability and BOM cost of the microphone itself should be comparable to that of measurement microphones that target the DIY speaker building market. The parts needed to build an OpenRefMic are cheap and, with the low prices of desktop 3D printers and PCB fabrication services, many builders will be able to make their own OpenRefMic for less than they would spend on a budget measurement microphone.

<br>

### 1/2" form factor

Many measurement microphones fit a 1/2" cylindrical form factor, or at least have a long probe end with a 1/2" diameter, which helps maintain omnidirectional frequency response up to several kilohertz. Phantom powering necessitates relatively large capacitors, but the OpenRefMic PCB just barely fits within a 1/2" cross-section. Using a mini-XLR connector, the overall microphone dimensions are 12.7x92mm, almost identical to a reference microphone from B&K or GRAS.

Note that the front grille diameter for OpenRefMic v2 is 13.2mm, which is the de facto standard for professional reference microphones. The slightly increased diameter allows enough space to include an O-ring to seal the mic capsule, threads to actually attach the grille to the mic body, and is wide enough to properly seal to a standard 1/2" pistonphone calibrator.

Specialized shapes for specific applications are left up to individual builders, but please share your design if you would like to add additional form factors to the project.

<br>

### Further goals

- The initial design is based around the PUI AOM-5024L-HD-F-R electret microphone capsule, but designs for additional capsules that trade noise performance for frequency response flatness will be added in the future. The preamplifier as-shown should work with a wide variety of electret mics, and component values can be adjusted for optimal performance or compatibility with analog MEMS mics.
- OpenRefMic prototypes have had normalized frequency respone within ±2dB up to 20kHz, which is typical for commercial measurement microphones. However, absolute sensitivity varies by up to ±3dB, which could introduce significant error in SPL measurements. Professional measurement microphones are calibrated in the field with a pistonphone, a device that you insert the microphone tip into, which generates a tone with a precise frequency and sound pressure level that is consistent for a given sealed air volume. If you have any ideas for a device that could replicate this functionality, or otherwise accurately generate or measure a sound pressure level in order to calibrate an OpenRefMic, please reach out.
