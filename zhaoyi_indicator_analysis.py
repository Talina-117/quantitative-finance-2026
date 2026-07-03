from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path("/Users/talina/Desktop/quantitative-finance")
CSV_PATH = ROOT / "zhaoyi_603986_20250701_20260630_daily.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["trade_date"] = pd.to_datetime(df["trade_date"].astype(str), format="%Y%m%d")
    df = df.sort_values("trade_date").reset_index(drop=True)
    return df


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calculate_macd(close: pd.Series) -> pd.DataFrame:
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return pd.DataFrame(
        {
            "ema12": ema12,
            "ema26": ema26,
            "macd": macd,
            "signal": signal,
            "hist": hist,
        }
    )


def calculate_bollinger(close: pd.Series, window: int = 20, num_std: int = 2) -> pd.DataFrame:
    middle = close.rolling(window=window).mean()
    std = close.rolling(window=window).std(ddof=0)
    upper = middle + num_std * std
    lower = middle - num_std * std
    return pd.DataFrame({"middle": middle, "upper": upper, "lower": lower})


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def plot_rsi(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["trade_date"], df["RSI"], color="#6a3d9a", linewidth=1.5, label="RSI(14)")
    ax.axhline(70, color="red", linestyle="--", linewidth=1, label="Overbought 70")
    ax.axhline(30, color="green", linestyle="--", linewidth=1, label="Oversold 30")
    ax.set_title("GigaDevice 603986.SH RSI")
    ax.set_xlabel("Trade Date")
    ax.set_ylabel("RSI")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    output = ROOT / "zhaoyi_603986_rsi.png"
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def plot_macd(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))
    colors = np.where(df["MACD_HIST"] >= 0, "#d62728", "#2ca02c")
    ax.bar(df["trade_date"], df["MACD_HIST"], color=colors, alpha=0.5, width=2, label="Histogram")
    ax.plot(df["trade_date"], df["MACD"], color="#1f77b4", linewidth=1.5, label="MACD")
    ax.plot(df["trade_date"], df["MACD_SIGNAL"], color="#ff7f0e", linewidth=1.5, label="Signal")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("GigaDevice 603986.SH MACD")
    ax.set_xlabel("Trade Date")
    ax.set_ylabel("Value")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    output = ROOT / "zhaoyi_603986_macd.png"
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def plot_bollinger(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df["trade_date"], df["close"], color="#1f77b4", linewidth=1.4, label="Close")
    ax.plot(df["trade_date"], df["BOLL_MID"], color="#ff7f0e", linewidth=1.2, label="Middle")
    ax.plot(df["trade_date"], df["BOLL_UPPER"], color="#d62728", linewidth=1.1, label="Upper")
    ax.plot(df["trade_date"], df["BOLL_LOWER"], color="#2ca02c", linewidth=1.1, label="Lower")
    ax.fill_between(
        df["trade_date"],
        df["BOLL_UPPER"],
        df["BOLL_LOWER"],
        color="#999999",
        alpha=0.12,
    )
    ax.set_title("GigaDevice 603986.SH Bollinger Bands")
    ax.set_xlabel("Trade Date")
    ax.set_ylabel("Price")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    output = ROOT / "zhaoyi_603986_bollinger.png"
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def plot_obv(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["trade_date"], df["OBV"], color="#8c564b", linewidth=1.5, label="OBV")
    ax.set_title("GigaDevice 603986.SH OBV")
    ax.set_xlabel("Trade Date")
    ax.set_ylabel("OBV")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    output = ROOT / "zhaoyi_603986_obv.png"
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def main() -> None:
    df = load_data()

    df["RSI"] = calculate_rsi(df["close"])

    macd_df = calculate_macd(df["close"])
    df["MACD"] = macd_df["macd"]
    df["MACD_SIGNAL"] = macd_df["signal"]
    df["MACD_HIST"] = macd_df["hist"]

    boll_df = calculate_bollinger(df["close"])
    df["BOLL_MID"] = boll_df["middle"]
    df["BOLL_UPPER"] = boll_df["upper"]
    df["BOLL_LOWER"] = boll_df["lower"]

    df["OBV"] = calculate_obv(df["close"], df["vol"])

    outputs = [
        plot_rsi(df),
        plot_macd(df),
        plot_bollinger(df),
        plot_obv(df),
    ]

    latest = df.iloc[-1]
    print(f"Loaded {len(df)} rows from {CSV_PATH.name}")
    print(f"Latest RSI(14): {latest['RSI']:.4f}")
    print(f"Latest MACD: {latest['MACD']:.4f}")
    print(f"Latest Signal: {latest['MACD_SIGNAL']:.4f}")
    print(f"Latest Histogram: {latest['MACD_HIST']:.4f}")
    print(f"Latest Bollinger Middle: {latest['BOLL_MID']:.4f}")
    print(f"Latest Bollinger Upper: {latest['BOLL_UPPER']:.4f}")
    print(f"Latest Bollinger Lower: {latest['BOLL_LOWER']:.4f}")
    print(f"Latest OBV: {latest['OBV']:.4f}")
    for output in outputs:
        print(f"Saved plot: {output}")


if __name__ == "__main__":
    main()
