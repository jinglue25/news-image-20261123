from pathlib import Path
import hashlib

from PIL import Image, ImageDraw, ImageFont


PAPER = '#f8f4ec'
INK = '#191919'
RED = '#b3261e'
TEAL = '#2e6f6a'
image = Image.new('RGB', (1024, 1024), PAPER)
draw = ImageDraw.Draw(image)
blocks = []


def font(size, bold=False):
    suffix = 'Bold' if bold else ''
    return ImageFont.truetype(
        f'/usr/share/fonts/truetype/noto/NotoSans-Condensed{suffix}.ttf', size)


def wrap(text, f, width):
    lines = []
    line = ''
    for word in text.split():
        candidate = f'{line} {word}' if line else word
        bounds = draw.textbbox((0, 0), candidate, font=f)
        if bounds[2] - bounds[0] <= width:
            line = candidate
        else:
            assert line, f'Word too wide: {word}'
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def textblock(name, text, box, size, bold=False, color=INK,
              leading=None, center=False):
    f = font(size, bold)
    x0, y0, x1, y1 = box
    leading = leading if leading is not None else size + 4
    lines = wrap(text, f, x1 - x0)
    measured = []
    end = y0
    for index, line in enumerate(lines):
        left, top, right, bottom = draw.textbbox((0, 0), line, font=f)
        width = right - left
        x = x0 + ((x1 - x0 - width) / 2 if center else 0)
        y = y0 + index * leading
        position = (x - left, y - top)
        bounds = draw.textbbox(position, line, font=f)
        assert x0 <= bounds[0] <= bounds[2] <= x1, (name, line, bounds, box)
        assert y0 <= bounds[1] <= bounds[3] <= y1, (name, line, bounds, box)
        draw.text(position, line, font=f, fill=color)
        measured.append(bounds)
        end = bounds[3]
    blocks.append((name, box, measured))
    return end


def spaced(text, box):
    f = font(17, True)
    x0, y0, x1, y1 = box
    widths = [draw.textbbox((0, 0), char, font=f)[2] -
              draw.textbbox((0, 0), char, font=f)[0] for char in text]
    tracking = (x1 - x0 - sum(widths)) / max(1, len(text) - 1)
    assert tracking >= 0
    x = float(x0)
    measured = []
    for char, width in zip(text, widths):
        left, top, _, _ = draw.textbbox((0, 0), char, font=f)
        position = (x - left, y0 - top)
        bounds = draw.textbbox(position, char, font=f)
        assert bounds[0] >= x0 and bounds[2] <= x1 + 0.001
        assert bounds[1] >= y0 and bounds[3] <= y1
        draw.text(position, char, font=f, fill=INK)
        measured.append(bounds)
        x += width + tracking
    blocks.append(('subline', box, measured))


def icon(kind, x, y, s):
    def points(coords):
        return [(x + a * s, y + b * s) for a, b in coords]

    def line(coords, width=3):
        draw.line(points(coords), fill=TEAL, width=width, joint='curve')

    def ellipse(bounds, width=3):
        a, b, c, d = bounds
        draw.ellipse((x + a * s, y + b * s, x + c * s, y + d * s),
                     outline=TEAL, width=width)

    if kind == 'globe':
        ellipse((0.06, 0.06, 0.94, 0.94), 4)
        ellipse((0.29, 0.06, 0.71, 0.94), 3)
        line([(0.06, 0.5), (0.94, 0.5)])
        line([(0.14, 0.26), (0.86, 0.26)])
        line([(0.14, 0.74), (0.86, 0.74)])
    elif kind == 'ship':
        draw.polygon(points([(0.06, 0.56), (0.94, 0.56), (0.77, 0.79),
                             (0.24, 0.79)]), outline=TEAL, width=3)
        line([(0.48, 0.12), (0.48, 0.56)])
        line([(0.28, 0.54), (0.28, 0.35), (0.71, 0.35), (0.71, 0.54)])
        line([(0.48, 0.14), (0.75, 0.25), (0.48, 0.25)])
        line([(0.04, 0.9), (0.2, 0.85), (0.36, 0.9), (0.52, 0.85),
              (0.68, 0.9), (0.84, 0.85), (0.98, 0.9)], 2)
    elif kind == 'building':
        line([(0.15, 0.92), (0.15, 0.08), (0.85, 0.08), (0.85, 0.59),
              (0.71, 0.65), (0.78, 0.76), (0.65, 0.84), (0.69, 0.92),
              (0.15, 0.92)])
        for row in range(4):
            for col in range(3):
                if row == 3 and col == 2:
                    continue
                a = 0.27 + col * 0.19
                b = 0.21 + row * 0.17
                line([(a, b), (a + 0.07, b)], 4)
        line([(0.06, 0.95), (0.94, 0.95)], 2)
    elif kind == 'satellite':
        draw.polygon(points([(0.38, 0.36), (0.62, 0.36), (0.62, 0.65),
                             (0.38, 0.65)]), outline=TEAL, width=3)
        for a, b in [(0.04, 0.31), (0.69, 0.96)]:
            line([(a, 0.4), (b, 0.4), (b, 0.62), (a, 0.62), (a, 0.4)], 2)
            line([((a + b) / 2, 0.4), ((a + b) / 2, 0.62)], 2)
        line([(0.5, 0.36), (0.61, 0.19)])
        ellipse((0.59, 0.13, 0.68, 0.22), 2)
        draw.arc((x + 0.08 * s, y + 0.05 * s, x + 0.92 * s, y + 0.94 * s),
                 25, 155, fill=TEAL, width=2)
    elif kind == 'chart':
        line([(0.1, 0.1), (0.1, 0.9), (0.94, 0.9)], 2)
        line([(0.2, 0.24), (0.38, 0.41), (0.52, 0.31), (0.69, 0.61),
              (0.79, 0.54), (0.94, 0.78)])
        line([(0.76, 0.72), (0.94, 0.78), (0.94, 0.59)])
    else:
        raise ValueError(f'Unknown icon: {kind}')


textblock('masthead', 'MONDAY 23 NOVEMBER 2026', (30, 30, 994, 88),
          64, bold=True, center=True)
draw.rectangle((32, 106, 992, 111), fill=RED)
spaced('FIVE STORIES FROM AROUND THE WORLD', (32, 122, 992, 150))
textblock('lead kicker', 'CLIMATE · ANTALYA, TURKEY',
          (36, 173, 790, 194), 16, bold=True, color=RED)
lead_end = textblock(
    'lead headline', 'COP31 ends with no deal — first failure since Copenhagen',
    (36, 205, 810, 292), 36, bold=True, leading=42)
textblock(
    'lead body',
    'The UN climate summit closed in Antalya on Monday, two days late, with no deal adopted — a first since Copenhagen in 2009. The EU rejected a final text that dropped any mention of moving away from fossil fuels.',
    (36, lead_end + 14, 810, 388), 19, leading=26)
icon('globe', 839, 211, 143)
draw.line((32, 405, 992, 405), fill=INK, width=2)

draw.line((512, 424, 512, 965), fill='#c5bdb0', width=1)
draw.line((32, 691, 992, 691), fill='#c5bdb0', width=1)
stories = [
    (36, 427, 'WAR · BENGHAZI, LIBYA',
     'Ukraine sinks Russian corvette off Libya',
     "President Zelenskyy said on Monday that seven Ukrainian naval drones sank the corvette Merkury off Libya and hit the arms carrier Angara — Kyiv's war reaching the Mediterranean.",
     'ship'),
    (536, 427, 'WAR · KYIV REGION, UKRAINE',
     'Russian strikes kill at least 14 near Kyiv',
     'Overnight Russian strikes killed at least 14 people in the Kyiv region. In Dymer, 11 died in a five-storey apartment block; a boy of seven and a woman of 79 were pulled alive from the rubble after 22 hours.',
     'building'),
    (36, 712, 'SPACE · MOSCOW, RUSSIA',
     'NATO: Russia readies a nuclear-armed satellite',
     "NATO intelligence services say Russia plans to launch 'Sputnik-S', a satellite carrying a nuclear warhead, possibly within 60 days, German media reported on Monday. The Kremlin dismissed the reports.",
     'satellite'),
    (536, 712, 'MARKETS · SEOUL, SOUTH KOREA',
     'AI rout knocks 3.3% off the Kospi',
     "South Korea's Kospi plunged 5.8% intraday before closing down 3.3% at 4,708.54, as doubts over AI spending hammered chip shares. Samsung Electronics fell 3.1% and SK Hynix 2.5%.",
     'chart'),
]
for x, y, kicker, headline, body, kind in stories:
    textblock(f'{kind} kicker', kicker, (x, y, x + 452, y + 20),
              14, bold=True, color=RED)
    headline_end = textblock(
        f'{kind} headline', headline, (x, y + 29, x + 373, y + 134),
        29, bold=True, leading=34)
    icon(kind, x + 392, y + 31, 60)
    textblock(f'{kind} body', body,
              (x, headline_end + 14, x + 452, 675 if y == 427 else 965),
              18, leading=24)

draw.line((32, 982, 992, 982), fill=RED, width=2)
textblock(
    'sources',
    'Sources: Reuters · AP · DW · Al Jazeera · CNBC · SCMP · The Japan Times · Democracy Now',
    (32, 995, 992, 1015), 14, center=True)


def validate_text():
    for name, box, bounds_list in blocks:
        x0, y0, x1, y1 = box
        for left, top, right, bottom in bounds_list:
            assert x0 <= left <= right <= x1 + 0.001, (name, box)
            assert y0 <= top <= bottom <= y1, (name, box)


if __name__ == '__main__':
    validate_text()
    print(f'PASS: all {len(blocks)} text blocks fit their boxes')
    output = Path(__file__).resolve().with_name('entry.png')
    image.save(output, format='PNG', optimize=False)
    with Image.open(output) as saved:
        assert saved.size == (1024, 1024)
        assert saved.format == 'PNG'
        saved.load()
    print('PASS: PNG format and 1024x1024 dimensions')
    assert output.stat().st_size < 1048576
    print(f'PASS: file size {output.stat().st_size} bytes is under 1048576')
    print(f'SHA256: {hashlib.sha256(output.read_bytes()).hexdigest()}')
