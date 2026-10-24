"""Parse pixel.txt SVG into exact pixel image."""

import re

from PIL import Image


def parse_pixel_svg() -> None:
    with open("analyst/pixel.txt", encoding="utf-8") as f:
        svg_content = f.read()

    img = Image.new("RGBA", (256, 143), (255, 255, 255, 255))

    path_pattern = re.compile(r'<path\s+fill="([^"]+)"\s+d="([^"]+)"')
    rect_pattern = re.compile(r"M(\d+)\s+(\d+)h(-?\d+)v(-?\d+)")

    count = 0
    for match in path_pattern.finditer(svg_content):
        fill_hex = match.group(1).lstrip("#")
        if len(fill_hex) == 6:
            r, g, b = int(fill_hex[0:2], 16), int(fill_hex[2:4], 16), int(fill_hex[4:6], 16)
            color = (r, g, b, 255)
        else:
            continue

        d_data = match.group(2)
        for rect in rect_pattern.finditer(d_data):
            x = int(rect.group(1))
            y = int(rect.group(2))
            w = int(rect.group(3))
            h = int(rect.group(4))
            if w < 0:
                x += w
                w = abs(w)
            if h < 0:
                y += h
                h = abs(h)
            for px in range(x, x + w):
                for py in range(y, y + h):
                    if 0 <= px < 256 and 0 <= py < 143:
                        img.putpixel((px, py), color)
            count += 1

    print(f"Rendered {count} path rects. Saving analyst/parsed_pixel.png...")
    img.save("analyst/parsed_pixel.png")
    print("Saved analyst/parsed_pixel.png successfully!")


if __name__ == "__main__":
    parse_pixel_svg()
