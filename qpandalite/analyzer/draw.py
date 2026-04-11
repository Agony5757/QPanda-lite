"""Visualization utilities for quantum measurement results."""

__all__ = ["plot_histogram", "plot_distribution"]

from typing import Dict, List, Union, Tuple
import matplotlib

# Use sans-serif as fallback for Chinese font support
matplotlib.rcParams["font.sans-serif"] = [
    "WenQuanYi Micro Hei",
    "WenQuanYi Zen Hei",
    "Noto Sans CJK SC",
    "SimHei",
    "Arial",
    "sans-serif",
]
matplotlib.rcParams["axes.unicode_minus"] = False

import matplotlib.pyplot as plt
import numpy as np


def plot_histogram(
    measured_result: Union[Dict[str, float], List[float]],
    title: str = "Measurement Result",
    figsize: Tuple[int, int] = (10, 6),
) -> None:
    """Plot a histogram of measurement results.

    Args:
        measured_result: Measurement results in one of two formats:

            - **key-value dict**: Maps outcome strings to probabilities, e.g.
              ``{"00": 0.5, "11": 0.5}``.
            - **list**: Probability vector in computational-basis order, e.g.
              ``[0.5, 0, 0, 0.5]`` for a 2-qubit system.

        title: Plot title. Defaults to ``"Measurement Result"``.
        figsize: Figure size ``(width, height)`` in inches.
            Defaults to ``(10, 6)``.

    Raises:
        ValueError: If the list length does not correspond to a valid number
            of qubits (i.e. is not a power of 2).

    Example:
        >>> from qpandalite.analyzer.draw import plot_histogram
        >>> # Key-value format
        >>> plot_histogram({"00": 0.5, "11": 0.5}, title="Bell State")
        >>> # List format (2 qubits)
        >>> plot_histogram([0.5, 0, 0, 0.5], title="Bell State")
    """
    # Detect input format
    if isinstance(measured_result, dict):
        keys = list(measured_result.keys())
        values = list(measured_result.values())
        # Determine qubit count from key length
        nqubit = len(keys[0]) if keys else 0
        labels = keys
    elif isinstance(measured_result, list):
        n = len(measured_result)
        if n == 0 or (n & (n - 1)) != 0:
            raise ValueError(
                f"List length {n} is not a power of 2 and cannot represent "
                "a valid qubit system."
            )
        nqubit = int(np.log2(n))
        labels = [f"{i:0{nqubit}b}" for i in range(n)]
        values = measured_result
    else:
        raise TypeError(
            "measured_result must be a dict or a list, "
            f"got {type(measured_result).__name__}"
        )

    # Dynamically adjust figure size and tick rotation for many qubits
    if nqubit >= 10:
        figsize = (max(figsize[0], nqubit * 0.4), figsize[1])
        rot = 45
    elif nqubit >= 7:
        figsize = (max(figsize[0], nqubit * 0.6), figsize[1])
        rot = 30
    else:
        rot = 0

    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(labels))
    ax.bar(x, values, color="steelblue", edgecolor="black", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=rot, ha="right" if rot else "center")
    ax.set_xlabel("Measurement Outcome")
    ax.set_ylabel("Probability")
    ax.set_title(title)
    ax.set_ylim(0, max(max(values) * 1.15, 1.05))
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    plt.show()


def plot_distribution(
    measured_result: Union[Dict[str, float], List[float]],
    title: str = "Probability Distribution",
    figsize: Tuple[int, int] = (10, 6),
) -> None:
    """Plot a bar chart of the probability distribution with a
    uniform reference line.

    Args:
        measured_result: Measurement results in one of two formats:

            - **key-value dict**: Maps outcome strings to probabilities, e.g.
              ``{"00": 0.5, "11": 0.5}``.
            - **list**: Probability vector in computational-basis order, e.g.
              ``[0.5, 0, 0, 0.5]`` for a 2-qubit system.

        title: Plot title. Defaults to ``"Probability Distribution"``.
        figsize: Figure size ``(width, height)`` in inches.
            Defaults to ``(10, 6)``.

    Raises:
        ValueError: If the list length does not correspond to a valid number
            of qubits (i.e. is not a power of 2).

    Example:
        >>> from qpandalite.analyzer.draw import plot_distribution
        >>> # Key-value format
        >>> plot_distribution({"00": 0.5, "11": 0.5}, title="Bell State")
        >>> # List format (2 qubits)
        >>> plot_distribution([0.5, 0, 0, 0.5], title="Bell State")
    """
    # Detect input format (same logic as plot_histogram)
    if isinstance(measured_result, dict):
        keys = list(measured_result.keys())
        values = list(measured_result.values())
        nqubit = len(keys[0]) if keys else 0
        labels = keys
    elif isinstance(measured_result, list):
        n = len(measured_result)
        if n == 0 or (n & (n - 1)) != 0:
            raise ValueError(
                f"List length {n} is not a power of 2 and cannot represent "
                "a valid qubit system."
            )
        nqubit = int(np.log2(n))
        labels = [f"{i:0{nqubit}b}" for i in range(n)]
        values = measured_result
    else:
        raise TypeError(
            "measured_result must be a dict or a list, "
            f"got {type(measured_result).__name__}"
        )

    # Dynamically adjust figure size and tick rotation for many qubits
    if nqubit >= 10:
        figsize = (max(figsize[0], nqubit * 0.4), figsize[1])
        rot = 45
    elif nqubit >= 7:
        figsize = (max(figsize[0], nqubit * 0.6), figsize[1])
        rot = 30
    else:
        rot = 0

    n_outcomes = len(labels)
    uniform_prob = 1.0 / n_outcomes

    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(n_outcomes)
    ax.bar(x, values, color="steelblue", edgecolor="black", alpha=0.8, label="Measured")
    ax.axhline(
        uniform_prob,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"Uniform ({uniform_prob:.4f})",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=rot, ha="right" if rot else "center")
    ax.set_xlabel("Measurement Outcome")
    ax.set_ylabel("Probability")
    ax.set_title(title)
    ax.set_ylim(0, max(max(values) * 1.15, uniform_prob * 1.15))
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    plt.show()
