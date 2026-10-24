"""Script to extract pixel art from analyst/pixel.txt and generate banner_art.py."""

import re
from pathlib import Path

from PIL import Image


def generate_banner_art() -> None:
    # 1. Parse pixel.txt into RGBA image
    with open("analyst/pixel.txt", encoding="utf-8") as f:
        svg_content = f.read()

    full_img = Image.new("RGBA", (256, 143), (255, 255, 255, 255))
    path_pattern = re.compile(r'<path\s+fill="([^"]+)"\s+d="([^"]+)"')
    rect_pattern = re.compile(r"M(\d+)\s+(\d+)h(-?\d+)v(-?\d+)")

    for match in path_pattern.finditer(svg_content):
        fill_hex = match.group(1).lstrip("#")
        if len(fill_hex) == 6:
            r, g, b = int(fill_hex[0:2], 16), int(fill_hex[2:4], 16), int(fill_hex[4:6], 16)
            color = (r, g, b, 255)
        else:
            continue

        d_data = match.group(2)
        for rect in rect_pattern.finditer(d_data):
            x, y, w, h = (
                int(rect.group(1)),
                int(rect.group(2)),
                int(rect.group(3)),
                int(rect.group(4)),
            )
            if w < 0:
                x += w
                w = abs(w)
            if h < 0:
                y += h
                h = abs(h)
            for px in range(x, x + w):
                for py in range(y, y + h):
                    if 0 <= px < 256 and 0 <= py < 143:
                        full_img.putpixel((px, py), color)

    # 2. Crop the center Cyber-Whale (fedora hat, circuits, belly, tail, fin)
    # The whale is located at x: 85 to 173, y: 29 to 103 (width 88, height 74)
    whale_crop = full_img.crop((85, 29, 173, 103)).convert("RGB")
    whale_crop.save("analyst/whale_pixel_extracted.png")

    # 3. Scale to 24 columns x 20 vertical pixels (10 terminal half-block rows)
    target_w, target_h = 24, 20
    resized = whale_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Dark background detection: blend seamlessly with terminal dark themes
    def is_bg(c: tuple[int, int, int]) -> bool:
        return c[0] < 35 and c[1] < 45 and c[2] < 80

    ansi_rows = []
    for y in range(0, target_h, 2):
        row_cells = []
        for x in range(target_w):
            c1 = resized.getpixel((x, y))
            c2 = resized.getpixel((x, y + 1))
            bg1 = is_bg(c1)
            bg2 = is_bg(c2)
            if bg1 and bg2:
                row_cells.append(" ")
            elif bg1 and not bg2:
                row_cells.append(f"\\x1b[38;2;{c2[0]};{c2[1]};{c2[2]}m▄\\x1b[0m")
            elif not bg1 and bg2:
                row_cells.append(f"\\x1b[38;2;{c1[0]};{c1[1]};{c1[2]}m▀\\x1b[0m")
            else:
                row_cells.append(
                    f"\\x1b[38;2;{c1[0]};{c1[1]};{c1[2]}m\\x1b[48;2;{c2[0]};{c2[1]};{c2[2]}m▀\\x1b[0m"
                )
        ansi_rows.append("".join(row_cells))

    # 4. Generate banner_art.py
    out_path = Path("src/agentic_pentest/presentation/banner_art.py")
    lines = [
        '"""Pre-rendered ANSI Half-Block Mascot Art for Agentic Pentest Terminal UX.',
        "",
        "Extracted directly from analyst/pixel.txt SVG pixel art with 24-bit TrueColor precision.",
        "Zero runtime dependency on Pillow or external image libraries.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from rich.table import Table",
        "from rich.text import Text",
        "",
        "# Pre-rendered 10-row TrueColor half-block cyber-whale (from analyst/pixel.txt)",
        "PIXEL_WHALE_ANSI_ROWS: list[str] = [",
    ]
    for row in ansi_rows:
        lines.append(f'    "{row}",')
    lines.extend(
        [
            "]",
            "",
            "# Ultra-compact 4-line block mascot fallback",
            "COMPACT_WHALE_ICON_ROWS: list[str] = [",
            '    "[bold #6272A4]  ▄██████▄      [/bold #6272A4]",',
            '    "[bold #D97757]▄████[bold #50FA7B]●[/bold #50FA7B]████████▄ █[/bold #D97757]",',
            '    "[bold #D97757]████████████████[/bold #D97757]",',
            '    "[bold #D97757] ▀██▀  ▀████▀ ▀ [/bold #D97757]",',
            "]",
            "",
            "",
            "def render_mascot_table(",
            '    target_url: str = "http://localhost:8888",',
            "    safe_mode: bool = True,",
            '    permission_mode: str = "interactive",',
            "    anonymous_mode: bool = True,",
            "    compact: bool = False,",
            ") -> Table:",
            '    """Render the aligned two-column banner Table with mascot on left and metadata on right."""',
            "    safe_str = 'ON' if safe_mode else 'OFF'",
            "    safe_color = 'green' if safe_mode else 'yellow'",
            "    anon_str = 'ON' if anonymous_mode else 'OFF'",
            "    anon_color = 'green' if anonymous_mode else 'yellow'",
            "",
            "    table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2))",
            "    table.add_column('Icon', justify='left', no_wrap=True)",
            "    table.add_column('Metadata', justify='left')",
            "",
            "    if compact:",
            "        meta_compact = [",
            "            f'[bold white]Agentic Pentest[/bold white] [bold cyan]v0.2.0[/bold cyan] [dim](SE373 Aligned)[/dim]',",
            "            f'[cyan]Target:[/cyan] [bold white]{target_url}[/bold white]  [dim]•[/dim]  [cyan]Safe:[/cyan] [{safe_color}]{safe_str}[/{safe_color}]',",
            "            f'[cyan]Memory:[/cyan] [bold green]MEMORY.md[/bold green] [dim]•[/dim] [cyan]Tier 2:[/cyan] [bold cyan]agent_sessions.db[/bold cyan] [dim](FTS5)[/dim]',",
            "            f'[dim]Commands: [bold white]scan[/bold white], [bold white]race[/bold white], [bold white]graphql[/bold white], [bold white]jwt[/bold white], [bold white]secrets[/bold white] [dim]•[/dim] [bold white]0-10[/bold white] action[/dim]',",
            "        ]",
            "        for icon, meta in zip(COMPACT_WHALE_ICON_ROWS, meta_compact, strict=False):",
            "            table.add_row(icon, meta)",
            "        return table",
            "",
            "    # Rich Pixel Art Mode (10 rows): Exact alignment with 10 lines of metadata",
            "    meta_detailed = [",
            "        f'[bold white]Agentic Pentest[/bold white] [bold cyan]v0.2.0[/bold cyan] [dim](SE373 Aligned)[/dim]',",
            "        f'[cyan]Target:[/cyan] [bold white]{target_url}[/bold white] [dim]•[/dim] [cyan]Safe-Mode:[/cyan] [{safe_color}]{safe_str}[/{safe_color}]',",
            "        f'[cyan]Mode:[/cyan] [bold white]{permission_mode}[/bold white] [dim]•[/dim] [cyan]OpSec Anonymization:[/cyan] [{anon_color}]{anon_str}[/{anon_color}]',",
            "        '[cyan]Memory Tier 1:[/cyan] [bold green]MEMORY.md[/bold green] [dim](<500 tok index)[/dim]',",
            "        '[cyan]Memory Tier 2:[/cyan] [bold cyan]agent_sessions.db[/bold cyan] [dim](FTS5 episodic search)[/dim]',",
            "        '[cyan]Level 5 OS:[/cyan] [bold cyan]Playwright Crawler & Interception Proxy (8090)[/bold cyan]',",
            "        '[cyan]Reflexion Loop:[/cyan] [bold green]ONLINE[/bold green] [dim]•[/dim] [cyan]Zero-FP Oracle:[/cyan] [bold green]VERIFIED[/bold green]',",
            "        '[cyan]MCP Tools:[/cyan] [bold cyan]14 Production Tools Active[/bold cyan]',",
            "        '[dim]Commands: [bold white]scan[/bold white], [bold white]race[/bold white], [bold white]graphql[/bold white], [bold white]jwt[/bold white], [bold white]secrets[/bold white], [bold white]browser[/bold white][/dim]',",
            "        '[dim]Type [bold white]help[/bold white], [bold white]?[/bold white] or [bold white]0-10[/bold white] for fast action [dim]•[/dim] [bold white]Tab[/bold white] to autocomplete[/dim]',",
            "    ]",
            "",
            "    for icon_ansi, meta in zip(PIXEL_WHALE_ANSI_ROWS, meta_detailed, strict=False):",
            "        table.add_row(Text.from_ansi(icon_ansi), meta)",
            "",
            "    return table",
            "",
        ]
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {out_path} with {len(ansi_rows)} TrueColor pixel rows successfully!")


if __name__ == "__main__":
    generate_banner_art()
