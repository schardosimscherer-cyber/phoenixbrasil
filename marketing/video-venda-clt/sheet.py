import sys
from PIL import Image, ImageDraw
tag, out, *ts = sys.argv[1:]
W, H, cols = 270, 480, 6
rows = (len(ts) + cols - 1) // cols
c = Image.new('RGB', (W * cols, (H + 24) * rows), 'white')
d = ImageDraw.Draw(c)
for i, t in enumerate(ts):
    im = Image.open(f'pv_{tag}_{t}.png').resize((W, H))
    x, y = (i % cols) * W, (i // cols) * (H + 24)
    c.paste(im, (x, y + 24)); d.text((x + 6, y + 6), f't={t}s', fill='black')
c.save(out)
