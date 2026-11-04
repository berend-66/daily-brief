"""What lies "behind" the skyline, so drifting clouds never reveal a hole.
In:  photo-day.jpg, sky.json, sky-matte.png, ridge.png   Out: sky-fill.jpg

This is the recipe used for the seeded sheep photo (photo-day.jpg). Run it from a folder that holds the photo."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
im = Image.open('photo-day.jpg'); P = np.asarray(im.convert('RGB'), dtype=np.float32)/255
H, W = P.shape[:2]
yb0, yb1 = json.load(open('sky.json'))['band']
band = np.asarray(Image.open('sky-matte.png'), dtype=np.float32)/255           # sky coverage, rows yb0..yb1
rg = np.asarray(Image.open('ridge.png'))[0]; ridge = (rg[:, 0].astype(np.float32)*256 + rg[:, 1])/8
# What sits behind the mountains: for every row, mirror the nearest clean sky across each mountain gap,
# blend the two sides in the middle, then soften. Only ever seen where drifting clouds pass behind a peak.
fill = np.zeros((yb1 - yb0, W, 3), np.float32)
xs = np.arange(W)
for j, y in enumerate(range(yb0, yb1)):
    sky = (band[j] > 0.98) & (ridge - y > 9)
    row = P[y]
    if not sky.any():
        fill[j] = fill[j-1] if j else row; continue
    idx = np.where(sky, xs, -1); left = np.maximum.accumulate(idx)                           # nearest sky to the left
    idx2 = np.where(sky, xs, W*2); right = np.minimum.accumulate(idx2[::-1])[::-1]             # nearest sky to the right
    out = row.copy()
    gap = ~sky
    L = np.where(left >= 0, left, right); R = np.where(right < W, right, left)
    gl = np.maximum(1, xs - L); gr = np.maximum(1, R - xs)
    srcL = np.clip(L - (xs - L), 0, W - 1); srcR = np.clip(R + (R - xs), 0, W - 1)
    # keep the mirrored source inside clean sky; fall back to the edge pixel of the span
    srcL = np.where(sky[srcL], srcL, L); srcR = np.where(sky[srcR], srcR, R)
    k = np.clip(gl/(gl + gr), 0, 1); k = k*k*(3 - 2*k)
    k = np.where(left < 0, 1.0, np.where(right >= W, 0.0, k))
    v = row[srcL]*(1 - k)[:, None] + row[srcR]*k[:, None]
    out[gap] = v[gap]
    fill[j] = out
fill = ndi.gaussian_filter(fill, (5, 2.5, 0))
half = Image.fromarray((np.clip(fill, 0, 1)*255 + 0.5).astype(np.uint8)).resize((W//2, (yb1 - yb0)//2), Image.LANCZOS)
half.save('sky-fill.jpg', quality=90, subsampling=0, icc_profile=im.info.get('icc_profile'))
print('fill', half.size)
# preview: sky with the mountains replaced
pv = P[1150:1760].copy(); pv[yb0-1150:yb1-1150] = np.where(band[..., None] > 0.98, P[yb0:yb1], fill)
Image.fromarray((pv*255).astype(np.uint8)).resize((1512, 305)).save('preview-skyfill_prev.jpg', quality=88)
