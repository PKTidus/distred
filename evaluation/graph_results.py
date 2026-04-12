import pandas as pd
import matplotlib.pyplot as plt
import argparse


def load_and_prep(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["Seconds"] = df["Timestamp"] - df["Timestamp"].iloc[0]
    return df


def plot_comparison(file_a, file_b, label_a="LB A", label_b="LB B"):
    df_a = load_and_prep(file_a)
    df_b = load_and_prep(file_b)

    fig, axes = plt.subplots(4, 1, figsize=(14, 18), sharex=False)
    fig.suptitle(f"Load Balancer Comparison: {label_a} vs {label_b}", fontsize=16)

    # Use User Count as X axis for fair comparison (not wall-clock time)
    for df, label, color in [(df_a, label_a, "steelblue"), (df_b, label_b, "tomato")]:
        x = df["User Count"]

        # 1. p50 latency
        if "50%ile (ms)" in df.columns:
            axes[0].plot(x, df["50%ile (ms)"], label=label, color=color)

        # 2. p95 latency
        if "95%ile (ms)" in df.columns:
            axes[1].plot(x, df["95%ile (ms)"], label=label, color=color, linestyle="--")

        # 3. p99 latency
        if "99%ile (ms)" in df.columns:
            axes[2].plot(x, df["99%ile (ms)"], label=label, color=color, linestyle=":")

        # 4. Failure rate
        if "Failures/s" in df.columns and "Requests/s" in df.columns:
            df["Error Rate %"] = (
                df["Failures/s"] / df["Requests/s"].replace(0, float("nan"))
            ) * 100
            axes[3].plot(x, df["Error Rate %"], label=label, color=color)

    titles = [
        "p50 Latency (ms)",
        "p95 Latency (ms)",
        "p99 Latency (ms)",
        "Error Rate (%)",
    ]
    for ax, title in zip(axes, titles):
        ax.set_title(title)
        ax.set_xlabel("Concurrent Users")
        ax.grid(True, alpha=0.4)
        ax.legend()

    plt.tight_layout()
    plt.savefig("lb_comparison.png", dpi=150)
    print("Saved lb_comparison.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_a", default="run_a.csv")
    parser.add_argument("file_b", default="run_b.csv")
    parser.add_argument("label_a", default="LB A")
    parser.add_argument("label_b", default="LB B")
    args = parser.parse_args()
    plot_comparison(args.file_a, args.file_b, args.label_a, args.label_b)
