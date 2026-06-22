import argparse
import sys
import time
from pathlib import Path
from random import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.fft import fft, fftfreq
from scipy.optimize import differential_evolution, minimize

from biquad import COEFF_FUNCTIONS, FILTER_TYPES


def load_csv_response(path: str) -> tuple[np.ndarray, np.ndarray]:
    with open(path, "r") as f:
        lines = f.readlines()

    start = 1
    for i in range(len(lines)):
        parts = lines[i].strip().split(",")
        try:
            float(parts[0])
            float(parts[1])
            start = i
            break
        except (ValueError, IndexError):
            continue

    freqs = []
    mags = []
    for line in lines[start:]:
        parts = line.strip().split(",")
        if len(parts) >= 2:
            try:
                freqs.append(float(parts[0]))
                mags.append(float(parts[1]))
            except ValueError:
                continue
    return np.array(freqs), np.array(mags)


def save_csv_response(path: str, freqs: np.ndarray, mags: np.ndarray) -> None:
    with open(path, "w") as f:
        f.write("frequency,magnitude_db\n")
        for fr, mg in zip(freqs, mags):
            f.write(f"{fr},{mg}\n")


class FilterSpec:
    def __init__(self, config: dict, topology: str):
        self.type = config["type"]
        if self.type not in FILTER_TYPES:
            raise ValueError(f"Unknown filter type: {self.type}. Supported: {list(FILTER_TYPES.keys())}")
        self.param_names = FILTER_TYPES[self.type]
        self.params = {}
        for name in self.param_names:
            if name not in config:
                raise ValueError(f"Filter '{self.type}' requires parameter '{name}'")
            p = config[name]
            initial = float(p["initial"])
            if "min" in p:
                lo = float(p["min"])
            else:
                lo = initial / 2
            if "max" in p:
                hi = float(p["max"])
            else:
                hi = initial * 2
            if lo > hi:
                lo, hi = hi, lo
            self.params[name] = {
                "initial": initial,
                "fixed": bool(p.get("fixed", False)),
                "min": lo,
                "max": hi,
            }

        self.topology = topology

        if topology == "parallel":
            if "mix_gain" not in config:
                raise ValueError(f"Parallel topology filter '{self.type}' requires 'mix_gain'")
            mg = config["mix_gain"]
            self.mix_gain = {
                "initial": float(mg["initial"]),
                "fixed": bool(mg.get("fixed", False)),
                "min": float(mg.get("min", -20)),
                "max": float(mg.get("max", 20)),
            }
        else:
            self.mix_gain = None

    def get_optimizable(self) -> list[dict]:
        result = []
        for name in self.param_names:
            if not self.params[name]["fixed"]:
                result.append({"filter_index": id(self), "param": name, **self.params[name]})
        if self.mix_gain is not None and not self.mix_gain["fixed"]:
            result.append({"filter_index": id(self), "param": "mix_gain", **self.mix_gain})
        return result

    def get_coefficients(self, values: dict, fs: float) -> tuple[np.ndarray, np.ndarray, float]:
        fn = COEFF_FUNCTIONS[self.type]
        if fn is None:
            b = np.array([1.0, 0.0, 0.0])
            a = np.array([1.0, 0.0, 0.0])
        else:
            kwargs = {}
            for name in self.param_names:
                if name in values:
                    kwargs[name] = values[name]
                else:
                    kwargs[name] = self.params[name]["initial"]
            if self.type == "linkwitz":
                b, a = fn(kwargs["f0"], kwargs["q0"], kwargs["fp"], kwargs["qp"], fs)
            elif "gain" in self.param_names:
                b, a = fn(kwargs["freq"], kwargs["q"], kwargs["gain"], fs)
            else:
                b, a = fn(kwargs["freq"], kwargs["q"], fs)
        if self.mix_gain is not None:
            gain = values.get("mix_gain", self.mix_gain["initial"])
        else:
            gain = 1.0
        return b, a, gain


class FilterBank:
    def __init__(self, specs: list[FilterSpec], fs: float, topology: str = "parallel", global_gain_config: dict | None = None):
        self.specs = specs
        self.fs = fs
        self.topology = topology
        self.optimizable = []
        for spec in specs:
            self.optimizable.extend(spec.get_optimizable())

        self._global_gain_default = 0.0
        if global_gain_config:
            self._global_gain_default = float(global_gain_config.get("initial", 0))
            if not global_gain_config.get("fixed", False):
                self.optimizable.append({
                    "filter_index": "__global__",
                    "param": "global_gain",
                    "initial": self._global_gain_default,
                    "min": float(global_gain_config.get("min", -20)),
                    "max": float(global_gain_config.get("max", 20)),
                })

        self._bounds = [(p["min"], p["max"]) for p in self.optimizable]

    @property
    def bounds(self):
        return self._bounds

    def decode_params(self, flat: np.ndarray) -> list[dict]:
        values_per_filter: dict[int, dict] = {}
        for i, p in enumerate(self.optimizable):
            fid = p["filter_index"]
            if fid not in values_per_filter:
                values_per_filter[fid] = {}
            values_per_filter[fid][p["param"]] = flat[i]
        return values_per_filter

    def frequency_response(self, flat: np.ndarray, freqs: np.ndarray) -> np.ndarray:
        values_per_filter = self.decode_params(flat)

        if self.topology == "series":
            total = np.ones_like(freqs, dtype=complex)
            for spec in self.specs:
                fid = id(spec)
                vals = values_per_filter.get(fid, {})
                b, a, gain = spec.get_coefficients(vals, self.fs)
                H = self._single_filter_response(b, a, freqs, self.fs)
                total *= H * gain
        else:
            total = np.zeros_like(freqs, dtype=complex)
            for spec in self.specs:
                fid = id(spec)
                vals = values_per_filter.get(fid, {})
                b, a, gain = spec.get_coefficients(vals, self.fs)
                H = self._single_filter_response(b, a, freqs, self.fs)
                total += H * gain

        response_db = 20 * np.log10(np.maximum(np.abs(total), 1e-12))

        global_gain_db = self._global_gain_default
        gg = values_per_filter.get("__global__", {})
        global_gain_db = gg.get("global_gain", global_gain_db)
        response_db += global_gain_db

        return response_db

    @staticmethod
    def _single_filter_response(b: np.ndarray, a: np.ndarray, freqs: np.ndarray, fs: float) -> np.ndarray:
        w = 2 * np.pi * freqs / fs
        z = np.exp(-1j * w)
        num = b[0] + b[1] * z + b[2] * z**2
        den = a[0] + a[1] * z + a[2] * z**2
        return num / den

    def loss(self, flat: np.ndarray, target_freqs: np.ndarray, target_mags: np.ndarray) -> float:
        response = self.frequency_response(flat, target_freqs)
        return float(np.sum(np.abs(target_mags - response)))


def optimize_adaptive_mc(
    bank: FilterBank,
    target_freqs: np.ndarray,
    target_mags: np.ndarray,
    iterations: int,
    initial_drift: float,
    patience: int,
    log_interval: int = 1000,
) -> np.ndarray:
    n_params = len(bank.optimizable)
    if n_params == 0:
        print("No optimizable parameters.")
        return np.array([])

    current = np.array([p["initial"] for p in bank.optimizable])
    current_loss = bank.loss(current, target_freqs, target_mags)
    best = current.copy()
    best_loss = current_loss

    drift = initial_drift
    patience_counter = 0
    temperature = 1.0
    accepted = 0
    total = 0

    start = time.time()
    print(f"Starting adaptive MC optimization ({iterations} iters, {n_params} params)")
    print(f"Initial loss: {best_loss:.4f}")

    for i in range(1, iterations + 1):
        temperature = max(1e-6, 1.0 - i / iterations)
        drift = initial_drift * (0.01 + 0.99 * temperature)

        proposed = current.copy()
        for j in range(n_params):
            lo, hi = bank.bounds[j]
            span = (hi - lo) * drift
            perturbation = (random() * 2 - 1) * span
            proposed[j] = np.clip(proposed[j] + perturbation, lo, hi)

        proposed_loss = bank.loss(proposed, target_freqs, target_mags)
        delta = proposed_loss - current_loss
        total += 1

        if proposed_loss < current_loss:
            current = proposed.copy()
            current_loss = proposed_loss
            accepted += 1
        elif random() < np.exp(-delta / (temperature * 0.01 + 1e-8)):
            current = proposed.copy()
            current_loss = proposed_loss
            accepted += 1

        if current_loss < best_loss:
            best = current.copy()
            best_loss = current_loss
            patience_counter = 0
        else:
            patience_counter += 1

        if i % log_interval == 0 or i == iterations:
            elapsed = time.time() - start
            eta = elapsed / i * (iterations - i)
            print(
                f"  iter {i}/{iterations} | loss: {current_loss:.4f} | "
                f"best: {best_loss:.4f} | drift: {drift:.4f} | "
                f"accept: {accepted}/{total} | ETA: {eta:.0f}s"
            )

        if patience_counter >= patience:
            print(f"  Early stop at iter {i} (patience {patience} exceeded)")
            break

    print(f"Optimization complete. Final best loss: {best_loss:.4f}")
    return best


def optimize_scipy(
    bank: FilterBank,
    target_freqs: np.ndarray,
    target_mags: np.ndarray,
    method: str = "differential_evolution",
    log_interval: int = 1000,
) -> np.ndarray:
    n_params = len(bank.optimizable)
    if n_params == 0:
        print("No optimizable parameters.")
        return np.array([])

    callback_data = {"nfev": 0, "best": None, "best_loss": np.inf}

    def callback(xk, convergence=None):
        callback_data["nfev"] += 1
        loss = bank.loss(xk, target_freqs, target_mags)
        if loss < callback_data["best_loss"]:
            callback_data["best_loss"] = loss
            callback_data["best"] = xk.copy()
        if callback_data["nfev"] % log_interval == 0:
            print(f"  fev {callback_data['nfev']} | best loss: {callback_data['best_loss']:.4f}")

    print(f"Starting scipy optimization (method={method}, {n_params} params)")

    if method == "differential_evolution":
        result = differential_evolution(
            bank.loss,
            bounds=bank.bounds,
            args=(target_freqs, target_mags),
            callback=callback,
            polish=True,
            maxiter=2000,
            seed=42,
        )
        print(f"  {result.message}")
        return result.x
    else:
        x0 = np.array([p["initial"] for p in bank.optimizable])
        result = minimize(
            bank.loss,
            x0,
            args=(target_freqs, target_mags),
            method=method,
            bounds=bank.bounds,
            callback=callback,
        )
        print(f"  {result.message}")
        return result.x


def save_results(
    path: str,
    bank: FilterBank,
    best_params: np.ndarray,
    target_freqs: np.ndarray,
    initial_response: np.ndarray,
    opt_response: np.ndarray,
) -> None:
    values_per_filter = bank.decode_params(best_params)

    with open(path, "w") as f:
        f.write("filter_index,type,parameter,initial_value,optimized_value\n")
        for spec in bank.specs:
            fid = id(spec)
            vals = values_per_filter.get(fid, {})
            for name in spec.param_names:
                init = spec.params[name]["initial"]
                opt = vals.get(name, init)
                f.write(f"{fid},{spec.type},{name},{init},{opt}\n")
            if spec.mix_gain is not None:
                init = spec.mix_gain["initial"]
                opt = vals.get("mix_gain", init)
                f.write(f"{fid},{spec.type},mix_gain,{init},{opt}\n")

        gg_init = bank._global_gain_default
        gg_vals = values_per_filter.get("__global__", {})
        gg_opt = gg_vals.get("global_gain", gg_init)
        f.write(f"__global__,global_gain,global_gain,{gg_init},{gg_opt}\n")

        f.write("\nfrequency,initial_db,optimized_db\n")
        for fr, init, opt in zip(target_freqs, initial_response, opt_response):
            f.write(f"{fr},{init},{opt}\n")

    print(f"Results saved to {path}")


def save_plot(
    path: str,
    target_freqs: np.ndarray,
    target_mags: np.ndarray,
    init_freqs: np.ndarray,
    init_mags: np.ndarray,
    opt_freqs: np.ndarray,
    opt_mags: np.ndarray,
) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(target_freqs, target_mags, label="Target", linewidth=1.5)
    plt.plot(init_freqs, init_mags, label="Initial", linewidth=1.5, alpha=0.6, linestyle="--")
    plt.plot(opt_freqs, opt_mags, label="Optimized", linewidth=1.5, alpha=0.8)
    plt.xscale("log")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.title("Filter Optimization Result")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {path}")


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Biquad filter optimization")
    parser.add_argument("config", type=str, help="Path to YAML config file")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path (overrides config)")
    parser.add_argument("--plot", type=str, default=None, help="Output plot PNG path")
    args = parser.parse_args()

    config = load_config(args.config)
    fs = config["sample_rate"]
    output_path = args.output or config.get("output_csv", "optimized_results.csv")
    plot_path = args.plot or config.get("output_plot")

    opt_config = config.get("optimization", {})
    method = opt_config.get("method", "adaptive_mc")
    iterations = opt_config.get("iterations", 100000)
    initial_drift = opt_config.get("initial_drift", 0.01)
    patience = opt_config.get("early_stop_patience", 5000)
    scipy_method = opt_config.get("scipy_method", "differential_evolution")

    topology = config.get("topology", "series")
    if topology not in ("series", "parallel"):
        print(f"Unknown topology: {topology}. Must be 'series' or 'parallel'")
        sys.exit(1)

    target_freqs, target_mags = load_csv_response(config["target_csv"])

    nyquist_cutoff = 0.9 * fs / 2
    mask = target_freqs <= nyquist_cutoff
    target_freqs = target_freqs[mask]
    target_mags = target_mags[mask]
    print(f"Using {len(target_freqs)} frequency points up to {nyquist_cutoff:.0f} Hz (0.9 × Nyquist)")

    input_mags = np.zeros_like(target_freqs)
    if "input_csv" in config:
        input_freqs, input_mags_raw = load_csv_response(config["input_csv"])
        input_mags = np.interp(target_freqs, input_freqs, input_mags_raw)
        print(f"Loaded input response from {config['input_csv']}")
        target_mags = target_mags - input_mags

    global_gain_config = config.get("global_gain")
    specs = [FilterSpec(fc, topology) for fc in config["filters"]]
    bank = FilterBank(specs, fs, topology, global_gain_config)

    if method == "adaptive_mc":
        best = optimize_adaptive_mc(bank, target_freqs, target_mags, iterations, initial_drift, patience)
    elif method == "scipy":
        best = optimize_scipy(bank, target_freqs, target_mags, scipy_method)
    else:
        print(f"Unknown optimization method: {method}")
        sys.exit(1)

    opt_filter_response = bank.frequency_response(best, target_freqs)
    initial_params = np.array([p["initial"] for p in bank.optimizable])
    initial_filter_response = bank.frequency_response(initial_params, target_freqs)

    initial_total = initial_filter_response + input_mags
    opt_total = opt_filter_response + input_mags

    initial_loss = float(np.sum(np.abs(target_mags - initial_filter_response)))
    final_loss = float(np.sum(np.abs(target_mags - opt_filter_response)))
    print(f"\nInitial loss: {initial_loss:.4f} -> Final loss: {final_loss:.4f}")

    save_results(output_path, bank, best, target_freqs, initial_total, opt_total)

    if plot_path:
        save_plot(plot_path, target_freqs, target_mags + input_mags, target_freqs, initial_total, target_freqs, opt_total)

    print("\nOptimized parameters:")
    values = bank.decode_params(best)
    for spec in specs:
        vals = values.get(id(spec), {})
        print(f"\n  {spec.type}:")
        for name in spec.param_names:
            init = spec.params[name]["initial"]
            opt = vals.get(name, init)
            fixed_str = " [fixed]" if spec.params[name]["fixed"] else ""
            print(f"    {name}: {init:.6f} -> {opt:.6f}{fixed_str}")
        if spec.mix_gain is not None:
            init = spec.mix_gain["initial"]
            opt = vals.get("mix_gain", init)
            fixed_str = " [fixed]" if spec.mix_gain["fixed"] else ""
            print(f"    mix_gain: {init:.6f} -> {opt:.6f}{fixed_str}")

    if global_gain_config is not None:
        gg_init = bank._global_gain_default
        gg_vals = values.get("__global__", {})
        gg_opt = gg_vals.get("global_gain", gg_init)
        gg_fixed = global_gain_config.get("fixed", False)
        fixed_str = " [fixed]" if gg_fixed else ""
        print(f"\n  global_gain: {gg_init:.6f} -> {gg_opt:.6f}{fixed_str}")


if __name__ == "__main__":
    main()
