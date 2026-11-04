"""Optional. Paints grass over the real flock (the clean plate) so the animated sheep replace it.
In:  photo-day.jpg, flock_mask.npy   Out: flock-clean.png (and flock.png/flock.json, an older sprite atlas the page no longer uses)

This is the recipe used for the seeded sheep photo (photo-day.jpg). Run it from a folder that holds the photo."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
im = Image.open('photo-day.jpg'); P = np.asarray(im.convert('RGB'), dtype=np.float32)/255
X0, Y0, X1, Y1 = 1230, 2262, 2410, 2356
c = P[Y0:Y1, X0:X1]; H, W = c.shape[:2]
r, g, b = c[...,0], c[...,1], c[...,2]; lum = 0.2126*r + 0.7152*g + 0.0722*b
mask = np.load('flock_mask.npy'); peaks = np.load('flock_peaks.npy'); n = len(peaks)
ys, xs = np.nonzero(mask)
# ---- every flock pixel belongs to exactly one sheep: nearest back, legs reach further down than up
dy = ys[:, None] - peaks[None, :, 0]; dx = xs[:, None] - peaks[None, :, 1]
d = (dx/11.0)**2 + np.where(dy < 0, (dy/6.0)**2, (dy/15.0)**2)
own = np.argmin(d, 1)
L = -np.ones((H, W), int); L[ys, xs] = own
soft = np.clip(ndi.gaussian_filter(mask.astype(np.float32), 0.8)*1.6, 0, 1)   # anti-aliased flock outline
bottom = np.array([np.percentile(ys[own == i], 92) if (own == i).any() else peaks[i, 0] for i in range(n)])
cream_col = np.median(c[mask & (lum > 0.6)], 0)
DARK = np.array([0.16, 0.15, 0.13], np.float32)
sprites = []
for i in range(n):
    core = L == i
    if core.sum() < 25: continue
    yy, xx = np.nonzero(core)
    yt, xl, xr = yy.min(), np.percentile(xx, 4), np.percentile(xx, 96)
    w = max(10.0, xr - xl + 1); Hs = 0.92*w; xc = (xl + xr)/2
    gy, gx = np.mgrid[0:H, 0:W]
    body = ((gx - xc)/(0.5*w))**2 + ((gy - (yt + 0.33*Hs))/(0.36*Hs))**2 <= 1
    legs = np.zeros_like(core)
    for f in (0.2, 0.38, 0.62, 0.8):
        lx = int(round(xl + f*w)); legs[int(yt + 0.58*Hs):int(yt + Hs) + 1, max(0, lx-1):lx+1] = True
    front = np.isin(L, [j for j in range(n) if bottom[j] > bottom[i]])
    comp = (body | legs) & front & ~core                          # parts hidden behind sheep in front of it
    rgb = c.copy(); a = np.zeros((H, W), np.float32)
    a[core] = 1.0
    fringe = ndi.binary_dilation(core, iterations=1) & (L == -1)
    a[fringe] = np.maximum(a[fringe], soft[fringe]*0.9)
    mine = np.median(c[core & (lum > 0.55)], 0) if (core & (lum > 0.55)).sum() > 5 else cream_col
    shade = np.clip(1 - 0.45*((gy - yt)/(0.7*Hs)), 0.45, 1)[..., None]
    rgb[comp & body] = (mine*shade)[comp & body]
    rgb[comp & legs & ~body] = DARK
    a[comp] = 1.0
    sel = a > 0
    sy, sx = np.nonzero(sel)
    by0, by1, bx0, bx1 = max(0, sy.min()-2), min(H, sy.max()+3), max(0, sx.min()-2), min(W, sx.max()+3)
    dk = core & (lum < 0.3); facing = 1
    if dk.sum() > 4: facing = 1 if np.nonzero(dk)[1].mean() >= xx.mean() else -1
    sprites.append(dict(i=i, rgba=np.dstack([rgb, a])[by0:by1, bx0:bx1], o=[X0 + bx0, Y0 + by0],
                        c=[float(X0 + xc), float(Y0 + yt + 0.4*Hs)], f=float(Y0 + bottom[i]), face=facing, w=float(w)))
print('sprites', len(sprites))
# ---- grass under the whole flock: copied from the meadow just below, colour matched at low frequency
hole = ndi.binary_dilation(mask, iterations=2)
SH = 76
src = P[Y0+SH:Y1+SH, X0:X1]
ok = ~ndi.binary_dilation(mask, iterations=4)
def lowpass(img, m, s=22):
    num = ndi.gaussian_filter(img*m[..., None], (s, s, 0)); den = ndi.gaussian_filter(m.astype(np.float32), s)[..., None]
    return num/np.maximum(den, 1e-3)
okS = np.ones(src.shape[:2], bool)
fill = np.clip(src + lowpass(c, ok) - lowpass(src, okS), 0, 1)
# the top of the flock sat against a paler strip of grass: continue that strip down (copied from just above,
# along a smooth line rather than the bumpy outline of the flock), then fade into the meadow fill
tops = np.array([np.nonzero(hole[:, x])[0].min() if hole[:, x].any() else H for x in range(W)], np.float32)
env = ndi.minimum_filter1d(tops, 41); env = ndi.gaussian_filter1d(np.where(env < H, env, np.nan_to_num(env)), 30)
plate = c.copy(); plate[hole] = fill[hole]
D = 14
for yy in range(H):
    xs_ = np.nonzero(hole[yy])[0]
    if not len(xs_) or yy - D < 0: continue
    strip = plate[yy - D, xs_]
    k = np.clip((yy - env[xs_]) / 14.0, 0, 1); k = (k*k*(3 - 2*k))[:, None]
    plate[yy, xs_] = strip*(1 - k) + fill[yy, xs_]*k
fill = plate
# match each row's colour to the grass left and right of the flock in that same row
def hblur(img, m, s):
    num = ndi.gaussian_filter1d(img*m[..., None], s, axis=1); den = ndi.gaussian_filter1d(m.astype(np.float32), s, axis=1)[..., None]
    return num/np.maximum(den, 1e-4), den
ref, rw = hblur(c, ok, 160)
fm, _ = hblur(fill, hole, 160)
corr = ndi.gaussian_filter(ref - fm, (2.0, 0, 0))
conf = np.clip(rw*40, 0, 1)
fill = np.clip(fill + corr*conf, 0, 1)
ha = np.clip(ndi.gaussian_filter(hole.astype(np.float32), 1.0)*1.6, 0, 1)
Image.fromarray((np.dstack([fill, ha])*255 + 0.5).astype(np.uint8), 'RGBA').save('flock-clean.png', optimize=True, icc_profile=im.info.get('icc_profile'))
# ---- pack sprites into a power-of-two atlas (wide padding so resampling never bleeds between sheep)
PAD = 16; AW = 1024; x = PAD; y = PAD; rowh = 0; place = []
for s in sprites:
    h, w = s['rgba'].shape[:2]
    if x + w + PAD > AW: x = PAD; y += rowh + PAD; rowh = 0
    place.append((x, y)); x += w + PAD; rowh = max(rowh, h)
AH = 1
while AH < y + rowh + PAD: AH *= 2
atlas = np.zeros((AH, AW, 4), np.float32)
meta = []
for s, (ax, ay) in zip(sprites, place):
    h, w = s['rgba'].shape[:2]; atlas[ay:ay+h, ax:ax+w] = s['rgba']
    meta.append([int(ax), int(ay), int(w), int(h), int(s['o'][0]), int(s['o'][1]), round(float(s['c'][0]), 1), round(float(s['c'][1]), 1), round(float(s['f']), 1), int(s['face']), round(float(s['w']), 1)])
Image.fromarray((atlas*255 + 0.5).astype(np.uint8), 'RGBA').save('flock.png', optimize=True, icc_profile=im.info.get('icc_profile'))
json.dump({'atlas': [AW, AH], 'clean': [X0, Y0, X1 - X0, Y1 - Y0], 'sheep': meta}, open('flock.json', 'w'), separators=(',', ':'))
print('atlas', AW, AH)
# ---- previews: flock removed, and flock rebuilt from sprites (must equal the original)
clean = P[Y0:Y1, X0:X1]*(1 - ha[..., None]) + fill*ha[..., None]
rebuilt = clean.copy()
for s in sorted(sprites, key=lambda s: s['f']):
    h, w = s['rgba'].shape[:2]; ox, oy = s['o'][0] - X0, s['o'][1] - Y0
    a = s['rgba'][..., 3:]; rebuilt[oy:oy+h, ox:ox+w] = s['rgba'][..., :3]*a + rebuilt[oy:oy+h, ox:ox+w]*(1 - a)
print('rebuilt vs original: mean abs diff %.4f, max %.3f' % (np.abs(rebuilt - c).mean(), np.abs(rebuilt - c).max()))
Image.fromarray((np.concatenate([c, clean, rebuilt], 0)*255).astype(np.uint8)).crop((0, 0, 600, 3*H)).resize((1200, 6*H), Image.NEAREST).save('preview-flock_cmp.png')
