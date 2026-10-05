"""Practical 4 oven programme and observed temperature.

Run: python3 plot_oven_temperature.py
Requires: numpy, matplotlib (pip install numpy matplotlib).
Optional measured data: --measured measured_temperature.csv
CSV columns: time_min,temperature_C (elapsed time from verified programme start).

Evidence: the controller photographs show 60 C/35 min, 60 C/60 min,
120 C/30 min, 120 C/120 min and ONE pre-start display of 21.09 C at
2026-09-10 11:27:40. The exact start time was not recorded.
Linear ramps and a starting programme temperature of 21.09 C are
explicit reconstruction assumptions, NOT measured temperature history.
"""
from pathlib import Path
import argparse
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OBSERVED_PRESTART_C = 21.09
DURATIONS_MIN = np.array([35.0, 60.0, 30.0, 120.0])
TARGETS_C = np.array([60.0, 60.0, 120.0, 120.0])

def make_plot(output_dir, measured_csv=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    times = np.r_[0.0, np.cumsum(DURATIONS_MIN)]
    temperatures = np.r_[OBSERVED_PRESTART_C, TARGETS_C]
    fig, (obs, ax) = plt.subplots(1, 2, figsize=(10.4, 4.6),
                                gridspec_kw={"width_ratios": [1.1, 4.4]})
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    # Keep the untimed pre-start observation off the programme time axis.
    obs.scatter([0], [OBSERVED_PRESTART_C], color="#C15B17", s=65, zorder=5)
    obs.annotate("21.09 °C", (0, OBSERVED_PRESTART_C), xytext=(0, 18),
                 textcoords="offset points", ha="center", fontsize=11, weight="bold")
    obs.set_xlim(-0.8, 0.8)
    obs.set_title("Observed display", fontsize=11)
    obs.set_ylabel("Temperature (°C)")
    ax.plot(times, temperatures, color="#1E5078", lw=2.3,
            label="Reconstructed programme (assumed linear ramps)")
    ax.scatter(times[1:], temperatures[1:], color="#1E5078", s=23, zorder=4)
    for a, b, label in [(0,35,"Ramp 1\n35 min"),(35,95,"Hold 1\n60 min"),
                         (95,125,"Ramp 2\n30 min"),(125,245,"Hold 2\n120 min")]:
        ax.axvspan(a, b, color="#1E5078", alpha=0.035 if "Ramp" in label else 0.09)
        ax.text((a+b)/2, 137, label, ha="center", va="center", fontsize=9)
    ax.annotate("60 °C", (65,60), xytext=(0,9), textcoords="offset points", ha="center",fontsize=10)
    ax.annotate("120 °C", (185,120), xytext=(0,-19), textcoords="offset points", ha="center",fontsize=10)
    if measured_csv:
        with open(measured_csv, newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        if not rows or not {"time_min", "temperature_C"}.issubset(rows[0]):
            raise ValueError("CSV requires time_min and temperature_C columns and at least one reading.")
        data = np.array([(float(r["time_min"]), float(r["temperature_C"])) for r in rows])
        if not np.isfinite(data).all() or np.any(data[:,0] < 0):
            raise ValueError("Measurements must be finite, with nonnegative elapsed times.")
        data = data[np.argsort(data[:,0])]
        # Markers only: no interpolation of missing measured temperatures.
        ax.scatter(data[:,0], data[:,1], s=24, color="#C15B17", label="Measured oven temperatures", zorder=6)
        ax.set_xlim(-4, max(250, float(data[:,0].max())+5))
    else:
        ax.set_xlim(-4,250)
    ax.set_xticks([0,35,95,125,185,245])
    ax.set_xlabel("Elapsed programme time (min)")
    ax.set_title("Programmed cycle reconstructed from controller settings", fontsize=11)
    for item in (obs,ax):
        item.set_ylim(0,150)
        item.set_yticks([0,30,60,90,120,150])
        item.grid(axis="y", color="#D9D9D9", lw=0.6)
        item.spines[["top","right"]].set_visible(False)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    evidence_note = ("Measured readings are shown as markers without interpolation."
                     if measured_csv else "No measured heating or cooling trace was supplied.")
    fig.text(0.5, 0.015,
             "Assumptions: ramps end at segment targets; programme starts at 21.09 °C. "
             + evidence_note, ha="center", fontsize=8)
    fig.tight_layout(rect=(0,0.07,1,1))
    for ext in ("png","pdf","svg"):
        fig.savefig(output_dir/f"oven_temperature.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    with (output_dir/"oven_programme.csv").open("w", newline="") as handle:
        writer=csv.writer(handle)
        writer.writerow(["segment","duration_min","end_time_min","target_C","interpretation"])
        for i,(duration,end,temp,kind) in enumerate(zip(DURATIONS_MIN,times[1:],TARGETS_C,
                                                     ["assumed linear ramp","hold","assumed linear ramp","hold"]),1):
            writer.writerow([i,duration,end,temp,kind])
    print(f"Total programmed duration: {times[-1]:.0f} min")
    print(f"Assumed ramp rates: {(60-OBSERVED_PRESTART_C)/35:.3f} and {(120-60)/30:.3f} °C/min")
    print(f"Saved plots and programme CSV in {output_dir.resolve()}")

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measured", type=Path, help="Optional real measurements CSV")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent/"report_assets")
    args=parser.parse_args()
    make_plot(args.output_dir,args.measured)
