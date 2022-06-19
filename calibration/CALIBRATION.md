# Calibration

The PUI AOM-5024L-HD-F-R electret microphone element was selected for OpenRefMic primarily for its very high SNR, but it has poor frequency response flatness compared to most electret microphones. A calibration curve can be applied to correct any frequency response measurements taken with an OpenRefMic, or equalization can be applied to recordings to achieve an effectively flat response from 10Hz to upwards of 20kHz.

<br>

## Calibration files

Calibration files are available in several formats:

- [frequency-response.csv](frequency-response.csv) - Raw frequency response at 94dBSPL (1Pa), calibrated against a B&K 4191 reference microphone, 24 points per octave from 10Hz-40kHz with no smoothing. The ripples at very low and very high frequencies are artefacts of the measurement setup and frequency response calculations, and it is not recommended to actually use this data to correct any measurements or recordings. This data is provided for reference only.

<br>

- [correction-curve.csv](correction-curve.csv) - Amplitude adjustments to apply to measurements taken with an OpenRefMic, 24 points per octave from 10Hz to 25kHz. This curve was derived by modeling the microphone's raw high frequency response with 2nd order filters and inverting the amplitude response of those filters.
    - How you use this correction curve depends on what software you are using it with. You may be able to import it directly, or you may need to interpolate the frequency points to match your measurement points. If your software does not allow importing you may need to export raw measurment data at the same frequency resolution as the correction curve and apply the curve to the output with an external tool (e.g. Excel)
    - For frequency-amplitude measurements like frequency responses and noise sprectra, the correction curve should be added to the raw measurment.
    - For equalization of recordings, you can import the correction curve into any FIR filter (or similar effect) that allows you to use arbitrary EQ curves.

<br>

- [second-order-filters.txt](second-order-filters.txt) - Parameters for filters that you can use to equalize recordings taken with an OpenRefMic. Only two filter stages are needed to correct the frequency response up to 25kHz, a shelving filter to recover frequencies above ~9kHz and a moderate notch to reduce a resonance at 5.5kHz.
  - You can input the filter parameters into any tool that implements 2nd-order IIR filters. The names for these filters vary from tool to tool. They may be labeled "biquad", "scientific filters", "parametric EQ", "analog filters", etc. The exact implementation might be different, so you should verify the filter response is consistent with correction-curve.csv.
  - Direct biquad coefficients are also provided for 44.1lHz, 48kHz, and 96kHz sample rates, calculated from [the RBJ cookbook](http://music.columbia.edu/pipermail/music-dsp/2001-March/041752.html) (the de facto standard for biquad filter calculations)
  - Note that these filters should not be used for recordings at lower sample rates, due to frequency warping effects. Error is minimal at 44.1kHz and higher sample rates, so recordings captured at 8kHz or 16kHz should be upsampled before filtering, then downsampled again.
  - Recordings can be equalized using the command-line audio processing tool [SoX](http://sox.sourceforge.net/).
    ```
    sox <raw recording> <equalized recording> treble 7.5 9300 0.707q equalizer 5500 1.2q -5.5
    ```

<br>

- [sensitivity.txt](sensitivity.txt) - OpenRefMic output level with 1kHz 94dBSPL (1Pa) stimulus, measured from the initial prototype device. The mic capsule sensitivity has a ±3dB tolerance, so individual microphones will vary a bit, but the sensitivity values provided should be close enough for hobbyists to estimate absolute SPL levels. Applications requiring more precise SPL measurements will need to be calibrated against another reference device.

<br>

## Measurements, measurement tools

This section will be expanded in the future, but the summary is that most of the tools used to process and analyze the raw recordings are either open source or custom tools written in MATLAB, based on publicly-available literature.

<!--TODO: describe measurement setup, noise floor measurement, etc. Add file for A-weighting filter taps, sox commands-->