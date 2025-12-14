# -*- coding: utf-8 -*-
"""
License: AGPL-3.0

This module generates a stacked bar chart showing the total number of years
of electricity demand data available per continent, broken down by measurement
frequency (5-min, 10-min, 15-min, 30-min, 60-min). The figure is saved to
a specified directory.
"""

import os
import matplotlib.pyplot as plt
from typing import Dict


def plot_frequency_coverage(
    frequency_data: Dict[str, Dict[str, int]], figure_directory: str
) -> None:
    """
    Generates and saves a stacked bar chart of years available per frequency by continent.

    Parameters
    ----------
    frequency_data : dict
        Dictionary mapping continents to dictionaries of {frequency: years}.
        Example:
        {
            "Africa": {"60-min": 19},
            "Asia": {"5-min": 4, "10-min": 6, "15-min": 3, "30-min": 32, "60-min": 51},
        }
    figure_directory : str
        Directory where the figure will be saved as 'frequency_coverage_by_continent.png'.
    """
    continents = list(frequency_data.keys())
    frequencies = ["5-min", "10-min", "15-min", "30-min", "60-min"]  # fixed order
    colors = ["#fdbe11", "#f7523a", "#da0e82", "#8a267f", "#676bbd"]

    # Prepare matrix: rows=continents, columns=frequencies
    years_matrix = [
        [frequency_data[cont].get(freq, 0) for freq in frequencies]
        for cont in continents
    ]

    plt.figure(figsize=(10, 7))
    x = range(len(continents))
    width = 0.4

    # Plot stacked bars
    bottoms = [0] * len(continents)
    for i, freq in enumerate(frequencies):
        values = [row[i] for row in years_matrix]
        plt.bar(x, values, width, bottom=bottoms, color=colors[i], label=freq)
        # Update bottoms for next stack
        bottoms = [sum(pair) for pair in zip(bottoms, values)]

    # Labels, title, legend
    plt.xticks(x, continents, rotation=45, fontsize=11, fontweight="bold")
    plt.ylabel("Total Number of Years Available", fontsize=12, fontweight="bold")
    plt.title(
        "Electricity Demand Data by Continent and Frequency",
        fontsize=14,
        fontweight="bold",
    )
    plt.legend(title="Frequency", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    # Ensure directory exists
    os.makedirs(figure_directory, exist_ok=True)

    # Save figure
    fig_path = os.path.join(figure_directory, "frequency_coverage_by_continent.png")
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Figure saved at: {fig_path}")


# ------------------------
# Run as standalone script
# ------------------------
if __name__ == "__main__":
    figure_dir = "figures"
    frequency_dict = {
        "Africa": {"60-min": 19},
        "Asia": {"5-min": 4, "10-min": 6, "15-min": 3, "30-min": 32, "60-min": 51},
        "Europe": {"15-min": 91, "30-min": 44, "60-min": 278},
        "North America": {"5-min": 5, "10-min": 2, "15-min": 14, "60-min": 58},
        "South America": {"30-min": 29, "60-min": 88},
        "Oceania": {"5-min": 5, "30-min": 44},
    }
    plot_frequency_coverage(frequency_dict, figure_dir)
