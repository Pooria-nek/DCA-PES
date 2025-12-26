import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ======================================================
# Hyperbolic decline model
# ======================================================
def hyperbolic(t, qi, Di, b):
    return qi / (1 + b * Di * t) ** (1 / b)

# ======================================================
# Fit hyperbolic decline
# ======================================================
def fit_hyperbolic(t, q):
    popt, pcov = curve_fit(
        hyperbolic,
        t,
        q,
        bounds=([0, 0, 0.1], [1e6, 5, 2.0]),
        maxfev=20000
    )
    return popt, np.sqrt(np.diag(pcov))

# ======================================================
# Monte Carlo simulation
# ======================================================
def run_monte_carlo(
    t,
    q,
    n_iterations=3000,
    forecast_months=120,
    uncertainty_scale=1.0
):
    params, sigma = fit_hyperbolic(t, q)

    qi_mu, Di_mu, b_mu = params
    qi_s,  Di_s,  b_s  = sigma

    # Apply uncertainty control
    qi_s *= uncertainty_scale
    Di_s *= uncertainty_scale
    b_s  *= uncertainty_scale

    # Sample parameters
    qi = np.random.normal(qi_mu, qi_s, n_iterations)
    Di = np.random.normal(Di_mu, Di_s, n_iterations)
    b  = np.random.normal(b_mu,  b_s,  n_iterations)

    # Physical constraints
    qi = np.clip(qi, 0, None)
    Di = np.clip(Di, 1e-6, None)
    b  = np.clip(b, 0.1, 2.0)

    t_forecast = np.arange(0, int(max(t)) + forecast_months + 1)

    rates = np.array([
        hyperbolic(t_forecast, qi[i], Di[i], b[i])
        for i in range(n_iterations)
    ])

    return t_forecast, rates, params, sigma

# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":

    # -------------------------
    # Load CSV
    # -------------------------
    df = pd.read_csv("BarnetteShaleTarrant.csv")

    # Parse dates
    df["Time"] = pd.to_datetime(df["Time"])

    # Convert to months since first production
    t0 = df["Time"].min()
    df["t_months"] = (df["Time"] - t0).dt.days / 30.4375

    t = df["t_months"].values
    q = df["Production"].values.astype(float)

    # -------------------------
    # Run Monte Carlo
    # -------------------------
    t_fc, mc_rates, params, sigma = run_monte_carlo(t, q, n_iterations= 10, forecast_months=12, uncertainty_scale= 0.5)

    # -------------------------
    # Percentiles
    # -------------------------
    p0 = np.percentile(mc_rates, 0, axis=0)
    p10 = np.percentile(mc_rates, 10, axis=0)
    p20 = np.percentile(mc_rates, 20, axis=0)
    p30 = np.percentile(mc_rates, 30, axis=0)
    p40 = np.percentile(mc_rates, 40, axis=0)
    p50 = np.percentile(mc_rates, 50, axis=0)
    p60 = np.percentile(mc_rates, 60, axis=0)
    p70 = np.percentile(mc_rates, 70, axis=0)
    p80 = np.percentile(mc_rates, 80, axis=0)
    p90 = np.percentile(mc_rates, 90, axis=0)
    p100 = np.percentile(mc_rates, 100, axis=0)

    # -------------------------
    # Print fit results
    # -------------------------
    print("\n=== Hyperbolic Fit Parameters ===")
    print(f"qi = {params[0]:.2f} ± {sigma[0]:.2f}")
    print(f"Di = {params[1]:.4f} ± {sigma[1]:.4f}")
    print(f"b  = {params[2]:.3f} ± {sigma[2]:.3f}")

    # -------------------------
    # Plot
    # -------------------------
    plt.figure(figsize=(10, 6))

    plt.scatter(t, q, s=20, label="History")
    plt.plot(t_fc, p0, linestyle="--", label="P0")
    plt.plot(t_fc, p10, linestyle="--", label="P10")
    plt.plot(t_fc, p20, linestyle="--", label="P20")
    plt.plot(t_fc, p30, linestyle="--", label="P30")
    plt.plot(t_fc, p40, linestyle="--", label="P40")
    plt.plot(t_fc, p50, linestyle="--", label="P50")
    plt.plot(t_fc, p60, linestyle="--", label="P60")
    plt.plot(t_fc, p70, linestyle="--", label="P70")
    plt.plot(t_fc, p80, linestyle="--", label="P80")
    plt.plot(t_fc, p90, linestyle="--", label="P90")
    plt.plot(t_fc, p100, linestyle="--", label="P100")

    plt.xlabel("Time")
    plt.ylabel("Rate")
    plt.title("Monte Carlo Hyperbolic Decline")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()