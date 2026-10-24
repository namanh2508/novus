"""Script to extract and export high-fidelity logo assets from analyst/icon.png."""

from collections import deque
from pathlib import Path

from PIL import Image


def flood_fill_corners(img: Image.Image, tolerance: int = 25) -> Image.Image:
    """Flood fill from four outer corners to transparently remove rounded outer whitespace

    while keeping internal white elements (e.g. whale belly, teeth, circuits) intact.
    """
    rgba = img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()
    if pixels is None:
        return rgba

    # Seed from outer corners
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    visited = set()
    queue = deque()

    bg_ref = pixels[0, 0][:3]

    for cx, cy in corners:
        queue.append((cx, cy))
        visited.add((cx, cy))

    def color_match(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> bool:
        return (
            abs(c1[0] - c2[0]) <= tolerance
            and abs(c1[1] - c2[1]) <= tolerance
            and abs(c1[2] - c2[2]) <= tolerance
        )

    while queue:
        x, y = queue.popleft()
        current_rgba = pixels[x, y]
        # Set alpha to 0
        pixels[x, y] = (current_rgba[0], current_rgba[1], current_rgba[2], 0)

        for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                n_color = pixels[nx, ny][:3]
                if color_match(n_color, bg_ref):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return rgba


def process_assets() -> None:
    src_path = Path("analyst/icon.png")
    if not src_path.exists():
        print(f"Source file {src_path} not found.")
        return

    img = Image.open(src_path)
    # Center large detailed variant coordinates
    # X: 824 to 1928, Y: 160 to 1320
    crop_box = (824, 160, 1928, 1320)
    cropped = img.crop(crop_box)

    # Flood fill outer background to transparent
    transparent_logo = flood_fill_corners(cropped, tolerance=30)

    out_dir = Path("docs/assets")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. High-Res 1024x1024
    logo_1024 = transparent_logo.resize((1024, 1024), Image.Resampling.LANCZOS)
    logo_1024.save(out_dir / "logo.png", "PNG")
    print(f"Saved {out_dir / 'logo.png'}")

    # 2. 512x512
    logo_512 = transparent_logo.resize((512, 512), Image.Resampling.LANCZOS)
    logo_512.save(out_dir / "logo_512.png", "PNG")
    print(f"Saved {out_dir / 'logo_512.png'}")

    # 3. 256x256
    logo_256 = transparent_logo.resize((256, 256), Image.Resampling.LANCZOS)
    logo_256.save(out_dir / "logo_256.png", "PNG")
    print(f"Saved {out_dir / 'logo_256.png'}")

    # 4. Multi-size Windows ICO (256, 128, 64, 48, 32, 16)
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    transparent_logo.save(out_dir / "logo.ico", format="ICO", sizes=icon_sizes)
    print(f"Saved {out_dir / 'logo.ico'}")

    # 5. Avatar (Left circular variant: X: 48 to 692, Y: 48 to 720)
    crop_avatar = img.crop((48, 48, 692, 720))
    avatar_trans = flood_fill_corners(crop_avatar, tolerance=30)
    avatar_512 = avatar_trans.resize((512, 512), Image.Resampling.LANCZOS)
    avatar_512.save(out_dir / "avatar.png", "PNG")
    print(f"Saved {out_dir / 'avatar.png'}")


if __name__ == "__main__":
    process_assets()
