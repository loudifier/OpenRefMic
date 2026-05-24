import numpy as np


def lowpass_coeff(freq: float, Q: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    b0 = (1 - np.cos(w0)) / 2
    b1 = 1 - np.cos(w0)
    b2 = (1 - np.cos(w0)) / 2
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def highpass_coeff(freq: float, Q: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    b0 = (1 + np.cos(w0)) / 2
    b1 = -(1 + np.cos(w0))
    b2 = (1 + np.cos(w0)) / 2
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def bandpass_coeff(freq: float, Q: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    b0 = alpha
    b1 = 0
    b2 = -alpha
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def bandpass_skirt_coeff(freq: float, Q: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    b0 = np.sin(w0) / 2
    b1 = 0
    b2 = -np.sin(w0) / 2
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def notch_coeff(freq: float, Q: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    b0 = 1
    b1 = -2 * np.cos(w0)
    b2 = 1
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def lowshelf_coeff(freq: float, Q: float, gain_db: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    A = 10 ** (gain_db / 40)
    beta = np.sqrt(A) / Q
    b0 = A * ((A + 1) - (A - 1) * np.cos(w0) + beta * np.sin(w0))
    b1 = 2 * A * ((A - 1) - (A + 1) * np.cos(w0))
    b2 = A * ((A + 1) - (A - 1) * np.cos(w0) - beta * np.sin(w0))
    a0 = (A + 1) + (A - 1) * np.cos(w0) + beta * np.sin(w0)
    a1 = -2 * ((A - 1) + (A + 1) * np.cos(w0))
    a2 = (A + 1) + (A - 1) * np.cos(w0) - beta * np.sin(w0)
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def highshelf_coeff(freq: float, Q: float, gain_db: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    A = 10 ** (gain_db / 40)
    beta = np.sqrt(A) / Q
    b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + beta * np.sin(w0))
    b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
    b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - beta * np.sin(w0))
    a0 = (A + 1) - (A - 1) * np.cos(w0) + beta * np.sin(w0)
    a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
    a2 = (A + 1) - (A - 1) * np.cos(w0) - beta * np.sin(w0)
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def peaking_coeff(freq: float, Q: float, gain_db: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    A = 10 ** (gain_db / 40)
    b0 = 1 + alpha * A
    b1 = -2 * np.cos(w0)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha / A
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def allpass_coeff(freq: float, Q: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2 * np.pi * freq / fs
    alpha = np.sin(w0) / (2 * Q)
    b0 = 1 - alpha
    b1 = -2 * np.cos(w0)
    b2 = 1 + alpha
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return b, a


def linkwitz_coeff(f0: float, Q0: float, fp: float, Qp: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    fc = (f0 + fp) / 2
    d0i = (2 * np.pi * f0) ** 2
    d1i = (2 * np.pi * f0) / Q0
    d2i = 1.0
    c0i = (2 * np.pi * fp) ** 2
    c1i = (2 * np.pi * fp) / Qp
    c2i = 1.0
    gn = (2 * np.pi * fc) / np.tan(np.pi * fc / fs)
    cci = c0i + gn * c1i + (gn ** 2) * c2i

    b0 = (d0i + gn * d1i + (gn ** 2) * d2i) / cci
    b1 = 2 * (d0i - (gn ** 2) * d2i) / cci
    b2 = (d0i - gn * d1i + (gn ** 2) * d2i) / cci
    a1 = 2 * (c0i - (gn ** 2) * c2i) / cci
    a2 = (c0i - gn * c1i + (gn ** 2) * c2i) / cci

    b = np.array([b0, b1, b2])
    a = np.array([1.0, a1, a2])
    return b, a


FILTER_TYPES = {
    "lowpass": ("freq", "q"),
    "highpass": ("freq", "q"),
    "bandpass": ("freq", "q"),
    "bandpass_skirt": ("freq", "q"),
    "notch": ("freq", "q"),
    "lowshelf": ("freq", "q", "gain"),
    "highshelf": ("freq", "q", "gain"),
    "peaking": ("freq", "q", "gain"),
    "allpass": ("freq", "q"),
    "linkwitz": ("f0", "q0", "fp", "qp"),
    "no_filt": (),
}

COEFF_FUNCTIONS = {
    "lowpass": lowpass_coeff,
    "highpass": highpass_coeff,
    "bandpass": bandpass_coeff,
    "bandpass_skirt": bandpass_skirt_coeff,
    "notch": notch_coeff,
    "lowshelf": lowshelf_coeff,
    "highshelf": highshelf_coeff,
    "peaking": peaking_coeff,
    "allpass": allpass_coeff,
    "linkwitz": linkwitz_coeff,
    "no_filt": None,
}
