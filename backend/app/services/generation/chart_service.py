"""Chart generation service."""

import io
import json
from typing import Dict, Any, List, Optional

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from app.config import settings


class ChartService:
    """Service for generating data visualization charts."""

    # Default brand colors
    DEFAULT_COLORS = [
        "#1a4a6e",  # Primary blue
        "#b8860b",  # Secondary gold
        "#2980b9",  # Tertiary blue
        "#27ae60",  # Success green
        "#e74c3c",  # Alert red
        "#9b59b6",  # Purple
        "#f39c12",  # Orange
        "#1abc9c",  # Teal
    ]

    def __init__(self):
        self.colors = self.DEFAULT_COLORS

    async def generate_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        style: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Generate a chart image.

        Args:
            chart_type: Type of chart ('bar', 'line', 'pie', 'donut', 'horizontal_bar').
            data: Chart data with 'labels' and 'values' keys.
            style: Style options (colors, fonts, etc.).

        Returns:
            Chart image as PNG bytes.
        """
        style = style or {}
        colors = style.get("colors", self.colors)
        title = style.get("title", "")
        figsize = style.get("figsize", (10, 6))
        font_size = style.get("font_size", 12)

        labels = data.get("labels", [])
        values = data.get("values", [])

        if not labels or not values:
            # Return a placeholder if no data
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=font_size)
            ax.axis("off")
        else:
            fig, ax = plt.subplots(figsize=figsize)

            if chart_type == "bar":
                bars = ax.bar(labels, values, color=colors[:len(values)])
                ax.set_ylabel(style.get("y_label", "Value"))
                # Add value labels on bars
                for bar, val in zip(bars, values):
                    height = bar.get_height()
                    ax.annotate(
                        f"{val}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=font_size - 2,
                    )

            elif chart_type == "horizontal_bar":
                y_pos = np.arange(len(labels))
                bars = ax.barh(y_pos, values, color=colors[:len(values)])
                ax.set_yticks(y_pos)
                ax.set_yticklabels(labels)
                ax.set_xlabel(style.get("x_label", "Value"))
                # Add value labels
                for bar, val in zip(bars, values):
                    width = bar.get_width()
                    ax.annotate(
                        f"{val}",
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0),
                        textcoords="offset points",
                        ha="left",
                        va="center",
                        fontsize=font_size - 2,
                    )

            elif chart_type == "line":
                ax.plot(labels, values, marker="o", color=colors[0], linewidth=2, markersize=8)
                ax.fill_between(labels, values, alpha=0.3, color=colors[0])
                ax.set_ylabel(style.get("y_label", "Value"))
                ax.grid(True, alpha=0.3)

            elif chart_type == "pie":
                wedges, texts, autotexts = ax.pie(
                    values,
                    labels=labels,
                    colors=colors[:len(values)],
                    autopct="%1.1f%%",
                    startangle=90,
                )
                for autotext in autotexts:
                    autotext.set_fontsize(font_size - 2)

            elif chart_type == "donut":
                wedges, texts, autotexts = ax.pie(
                    values,
                    labels=labels,
                    colors=colors[:len(values)],
                    autopct="%1.1f%%",
                    startangle=90,
                    pctdistance=0.75,
                )
                # Draw center circle for donut effect
                center_circle = plt.Circle((0, 0), 0.50, fc="white")
                ax.add_patch(center_circle)
                for autotext in autotexts:
                    autotext.set_fontsize(font_size - 2)

            else:
                # Default to bar chart
                ax.bar(labels, values, color=colors[:len(values)])

            if title:
                ax.set_title(title, fontsize=font_size + 2, fontweight="bold", pad=20)

        # Adjust layout
        plt.tight_layout()

        # Save to bytes
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
        buf.seek(0)
        plt.close(fig)

        return buf.getvalue()

    async def suggest_visualizations(
        self,
        statistics: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Suggest appropriate visualizations for statistics.

        Args:
            statistics: List of statistics.

        Returns:
            Suggested visualization configurations.
        """
        suggestions = []

        # Group statistics by category
        categories = {}
        for stat in statistics:
            cat = stat.get("category", "general")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(stat)

        # Generate suggestions based on data characteristics
        for category, stats in categories.items():
            if len(stats) >= 3:
                # Multiple stats - good for comparison charts
                numeric_values = []
                labels = []
                for stat in stats[:6]:  # Limit to 6 for readability
                    value = stat.get("value", "")
                    # Try to extract numeric value
                    try:
                        if "%" in str(value):
                            num_val = float(str(value).replace("%", "").replace(",", ""))
                        elif "$" in str(value):
                            num_val = float(str(value).replace("$", "").replace(",", ""))
                        else:
                            num_val = float(str(value).replace(",", ""))
                        numeric_values.append(num_val)
                        labels.append(stat.get("context", "")[:30])
                    except (ValueError, TypeError):
                        continue

                if len(numeric_values) >= 2:
                    suggestions.append({
                        "type": "horizontal_bar",
                        "title": f"{category.title()} Comparison",
                        "data": {
                            "labels": labels,
                            "values": numeric_values,
                        },
                        "description": f"Compare {len(numeric_values)} {category} metrics",
                        "priority": "high" if len(numeric_values) >= 4 else "medium",
                    })

            # Single impactful stat - good for callout
            for stat in stats:
                if stat.get("highlight_worthy"):
                    suggestions.append({
                        "type": "callout",
                        "title": "Key Statistic",
                        "data": stat,
                        "description": "Highlight this important metric",
                        "priority": "high",
                    })
                    break  # Only one callout per category

        # If we have percentage data, suggest a pie chart
        percentage_stats = [
            s for s in statistics
            if "%" in str(s.get("value", ""))
        ]
        if len(percentage_stats) >= 2:
            labels = []
            values = []
            for stat in percentage_stats[:5]:
                try:
                    val = float(str(stat["value"]).replace("%", ""))
                    values.append(val)
                    labels.append(stat.get("context", "")[:20])
                except (ValueError, TypeError):
                    continue

            if values and sum(values) <= 100:
                suggestions.append({
                    "type": "pie",
                    "title": "Distribution",
                    "data": {"labels": labels, "values": values},
                    "description": "Show percentage distribution",
                    "priority": "medium",
                })

        return suggestions
