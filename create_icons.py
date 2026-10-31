

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

icon_folder = Path("static/icons")
icon_folder.mkdir(parents=True, exist_ok=True)

NAVY = "#102A43"
DARK_BLUE = "#173B5E"
BLUE = "#3B82F6"
LIGHT_BLUE = "#93C5FD"
WHITE = "#FFFFFF"

font_path = r"C:\Windows\Fonts\arialbd.ttf"

for size in (192, 512):
    image = Image.new("RGB", (size, size), NAVY)
    draw = ImageDraw.Draw(image)

    # Geometric rounded-square border
    margin = int(size * 0.08)
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=int(size * 0.19),
        fill=DARK_BLUE,
        outline=BLUE,
        width=max(2, int(size * 0.012))
    )

    # Subtle mathematical coordinate grid
    grid_left = int(size * 0.20)
    grid_top = int(size * 0.20)
    grid_right = int(size * 0.80)
    grid_bottom = int(size * 0.72)

    for i in range(5):
        x = grid_left + i * (grid_right - grid_left) // 4
        y = grid_top + i * (grid_bottom - grid_top) // 4

        draw.line(
            (x, grid_top, x, grid_bottom),
            fill="#244B6B",
            width=max(1, int(size * 0.004))
        )
        draw.line(
            (grid_left, y, grid_right, y),
            fill="#244B6B",
            width=max(1, int(size * 0.004))
        )

    # Large white MP monogram
    font = ImageFont.truetype(font_path, int(size * 0.37))
    text = "MP"
    box = draw.textbbox((0, 0), text, font=font)

    text_width = box[2] - box[0]
    text_height = box[3] - box[1]

    x = (size - text_width) / 2 - box[0]
    y = int(size * 0.32) - text_height / 2 - box[1]

    # Dark outline gives the initials stronger definition
    outline_width = max(1, int(size * 0.006))
    draw.text(
        (x, y), text, font=font, fill=WHITE,
        stroke_width=outline_width, stroke_fill=NAVY
    )

    # Rising graph line underneath the monogram
    points = [
        (int(size * 0.25), int(size * 0.75)),
        (int(size * 0.43), int(size * 0.68)),
        (int(size * 0.57), int(size * 0.71)),
        (int(size * 0.76), int(size * 0.58))
    ]

    draw.line(
        points,
        fill=LIGHT_BLUE,
        width=max(2, int(size * 0.018)),
        joint="curve"
    )

    # Blue plotted points
    point_radius = int(size * 0.025)
    for px, py in points:
        draw.ellipse(
            (px - point_radius, py - point_radius,
             px + point_radius, py + point_radius),
            fill=BLUE,
            outline=WHITE,
            width=max(1, int(size * 0.004))
        )

    # Electric-blue finishing bar
    draw.rounded_rectangle(
        (int(size * 0.34), int(size * 0.83),
         int(size * 0.66), int(size * 0.85)),
        radius=max(2, int(size * 0.01)),
        fill=BLUE
    )

    image.save(icon_folder / f"mp-icon-{size}.png")

print("New MuchiPondo mathematics icons created successfully.")
