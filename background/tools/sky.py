"""The exact skyline: how much sky each pixel holds, so clouds drift without the mountains moving.
In:  photo-day.jpg, ridge.json   Out: sky-matte.png, ridge.png, sky.json (the rows for skyRows)

This is the recipe used for the seeded sheep photo (photo-day.jpg). Run it from a folder that holds the photo."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
P = np.asarray(Image.open('photo-day.jpg').convert('RGB'), dtype=np.float32)/255
H, W = P.shape[:2]
lum = 0.2126*P[...,0] + 0.7152*P[...,1] + 0.0722*P[...,2]
rough = np.array(json.load(open('ridge.json'))['ridge_full'])        # every 8th full-res column (from masks2)
rx = np.arange(len(rough))*8*2/2*1.0
r0 = np.interp(np.arange(W), np.arange(len(rough))*16, rough)        # ridge.json stored every 8 half-res cols = 16 full-res
# ---- precise skyline per column: where brightness falls from the sky level to the mountain level
ridge = np.zeros(W); strength = np.zeros(W)
for x in range(W):
    a = int(r0[x])
    col = ndi.gaussian_filter1d(lum[max(0, a-60):a+60, x], 0.8); base = max(0, a-60)
    S = np.median(lum[max(0, a-40):max(1, a-14), x]); Mv = np.median(lum[a+14:a+40, x])
    strength[x] = S - Mv
    mid = (S + Mv)/2
    seg = col[30:90]                                                  # rows a-30 .. a+30
    below = np.nonzero(seg < mid)[0]
    ridge[x] = base + 30 + (below[0] if len(below) else 30)
# faint distant peaks on the left sit only slightly darker than the sky: catch the first clear drop
for x in range(150, 466):
    a0 = int(r0[x]) - 90
    col = ndi.gaussian_filter1d(lum[a0:a0+110, x], 1.2)
    S = np.median(lum[a0:a0+25, x])
    dn = col < S - 0.065
    run = dn[:-3] & dn[1:-2] & dn[2:-1] & dn[3:]
    if run.any():
        cand = a0 + int(np.argmax(run))
        if cand < ridge[x]: ridge[x] = cand
ridge = ndi.median_filter(ridge, 5, mode='nearest')
ridge = ndi.gaussian_filter1d(ridge, 1.0, mode='nearest')
print('ridge min/max', ridge.min(), ridge.max(), '| weak-edge columns', int((strength < 0.08).sum()))
# ---- coverage of the sky in a thin band around the skyline (1 = sky, 0 = mountain)
yb0, yb1 = int(ridge.min()) - 12, int(ridge.max()) + 12
band = np.zeros((yb1 - yb0, W), np.float32)
for x in range(W):
    rr = ridge[x]
    a = int(rr)
    S = np.median(lum[a-30:a-6, x]); Mv = np.median(lum[a+6:a+30, x])
    y = np.arange(yb0, yb1)
    lin = np.clip((lum[yb0:yb1, x] - Mv)/max(S - Mv, 0.05), 0, 1)
    geo = np.clip(rr - y + 0.5, 0, 1)                                   # 1 px wide edge along the skyline
    near = np.abs(y - rr) <= 2
    band[:, x] = np.where(near, 0.5*lin + 0.5*geo, geo)
Image.fromarray((band*255 + 0.5).astype(np.uint8), 'L').save('sky-matte.png', optimize=True)
# ridge row per column, 16-bit fixed point (1/8 px) in R,G
v = np.round(ridge*8).astype(np.uint16)
rg = np.zeros((1, W, 4), np.uint8); rg[0, :, 0] = v >> 8; rg[0, :, 1] = v & 255; rg[0, :, 3] = 255
Image.fromarray(rg, 'RGBA').save('ridge.png')
json.dump({'band': [yb0, yb1]}, open('sky.json', 'w'))
print('band rows', yb0, yb1)
# preview: matte over the ridge region
ov = (P[1200:1800, 0:3024]*255).astype(np.uint8).copy()
m = np.zeros((600, 3024), np.float32); m[yb0-1200:yb1-1200] = band; m[:yb0-1200] = 1
ov[..., 0] = np.clip(ov[..., 0]*0.6 + m*100, 0, 255)
Image.fromarray(ov).resize((1512, 300)).save('preview-matte_prev.png')
z = (P[1240:1340, 600:860]*255).astype(np.uint8).copy(); mz = np.zeros((100, 260), np.float32); mz[:] = 0
for yy in range(100):
    Y = 1240 + yy
    mz[yy] = np.where(Y < yb0, 1, np.where(Y >= yb1, 0, band[min(max(Y - yb0, 0), yb1 - yb0 - 1), 600:860]))
z[..., 0] = np.clip(z[..., 0]*0.5 + mz*120, 0, 255)
Image.fromarray(z).resize((1040, 400), Image.NEAREST).save('preview-matte_zoom.png')
