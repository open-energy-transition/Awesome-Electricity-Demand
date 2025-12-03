# -*- coding: utf-8 -*-
"""
License: AGPL-3.0

This module generates a grouped bar chart showing the coverage of electricity
demand data by continent, including Data Availability, Population Coverage,
and Land Coverage. The figure is saved directly to a specified directory.
"""

import os
import matplotlib.pyplot as plt
from typing import Dict, List


def plot_continent_coverage(
    coverage_data: Dict[str, List[float]], figure_directory: str
) -> None:
    """
    Generates and saves a grouped bar chart for Data, Population, and Land
    coverage by continent.

    Parameters
    ----------
    coverage_data : dict
        Dictionary containing coverage data:
        - 'continents': List of continent names.
        - 'data': List of data availability percentages.
        - 'population': List of population coverage percentages.
        - 'land': List of land coverage percentages.
    figure_directory : str
        Directory where the figure will be saved as 'coverage_by_continent.png'.
    """
    continents = coverage_data["continents"]
    data_availability = coverage_data["data"]
    population_coverage = coverage_data["population"]
    land_coverage = coverage_data["land"]

    plt.figure(figsize=(12, 6))
    x = range(len(continents))
    width = 0.25
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    bars1 = plt.bar(
        [p - width for p in x],
        data_availability,
        width,
        label="Countries",
        color=colors[0],
    )
    bars2 = plt.bar(x, population_coverage, width, label="Population", color=colors[1])
    bars3 = plt.bar(
        [p + width for p in x],
        land_coverage,
        width,
        label="Land",
        color=colors[2],
    )

    # Add percentage labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color="black",
            )

    plt.xticks(x, continents, rotation=45, fontsize=11, fontweight="bold")
    plt.ylabel("Coverage (%)", fontsize=12, fontweight="bold")
    plt.title(
        "Country, Population, and Land Coverage by Continent",
        fontsize=14,
        fontweight="bold",
    )
    plt.legend(fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    # Ensure directory exists
    os.makedirs(figure_directory, exist_ok=True)

    # Save the figure
    fig_path = os.path.join(figure_directory, "coverage_by_continent.png")
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Figure saved at: {fig_path}")


# ------------------------
# Run as standalone script
# ------------------------
figure_dir = "figures"  # adjust this if needed
coverage_data = {
    "continents": [
        "Africa",
        "Asia",
        "Europe",
        "North America",
        "South America",
        "Oceania",
    ],
    "data": [5.6, 26.5, 84.4, 20.8, 50.0, 13.3],
    "population": [22.59, 77.28, 98.33, 85.92, 84.50, 68.33],
    "land": [15.34, 32.84, 94.80, 97.12, 82.93, 93.73],
}
plot_continent_coverage(coverage_data, figure_dir)
