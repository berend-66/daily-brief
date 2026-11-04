"""Sky, water and grass masks, plus a quarter-size depth map and a rough skyline.
In:  photo-day.jpg, depth_raw518.npy (from depth.py)   Out: masks.png, depth.png, ridge.json
The row ranges and colour thresholds are tuned to the seeded sheep photo: adapt them to yours.

This is the recipe used for the seeded sheep photo (photo-day.jpg). Run it from a folder that holds the photo."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
def smooth(x, a, b):
    t = np.clip((x-a)/(b-a), 0, 1); return t*t*(3-2*t)

im = Image.open('photo-day.jpg').convert('RGB')
W, H = im.size
hw, hh = W//2, H//2                                   # half-res work grid 1512x2016
q = np.asarray(im.resize((hw, hh), Image.LANCZOS), dtype=np.float32)/255
r, g, b = q[...,0], q[...,1], q[...,2]
lum = 0.2126*r + 0.7152*g + 0.0722*b
mx, mn = q.max(2), q.min(2); sat = (mx-mn)/(mx+1e-4)
d = np.load('depth_raw518.npy')
D = np.asarray(Image.fromarray(d).resize((hw, hh), Image.BICUBIC))
Y = np.arange(hh)[:, None] * np.ones((1, hw)); fy = Y*2      # full-res row of each half-res pixel

# ---------- skyline: first solid "mountain" pixel scanning down each column
mount = (D > 0.06) & (lum < 0.47)
ridge = np.zeros(hw)
for x in range(hw):
    col = mount[600:1150, x]
    run = col[:-3] & col[1:-2] & col[2:-1] & col[3:]
    idx = np.argmax(run) if run.any() else -1
    ridge[x] = 600 + idx if idx >= 0 else np.nan
ridge = np.where(np.isnan(ridge), np.nanmedian(ridge), ridge)
ridge = ndi.median_filter(ridge, size=9, mode='nearest')
dist = ridge[None, :] - Y                                   # half-res px above the ridge
sky = smooth(dist, 4, 30)                                    # 8..60 full-res px fade above the ridge

# ---------- lake: blue-grey band; fades out before the shore fence so posts and wire stay still
band = (fy > 1990) & (fy < 2290)
wat = band & (b > r - 0.03) & (lum > 0.28) & (lum < 0.88) & (sat < 0.36)
wat = ndi.binary_opening(wat, iterations=1)
lab, n = ndi.label(wat); sizes = ndi.sum(wat, lab, range(1, n+1))
wat = np.isin(lab, 1 + np.where(sizes > 1500)[0])
wat = ndi.binary_closing(wat, iterations=3)
wat = ndi.binary_erosion(wat, iterations=3)                  # keep the far shore line still
water = ndi.gaussian_filter(wat.astype(np.float32), 2.0) * (1 - smooth(fy, 2190, 2232))

# ---------- meadow grass in front of the flock; fence posts excluded
mead = (fy > 2340)
dark = mead & (lum < 0.30)
posts0 = ndi.binary_opening(dark, structure=np.ones((10, 1), bool))
lab, n = ndi.label(posts0); keep = np.zeros(n+1, bool)
for i, sl in enumerate(ndi.find_objects(lab), 1):
    hgt, wid = sl[0].stop-sl[0].start, sl[1].stop-sl[1].start
    keep[i] = hgt >= 18 and hgt >= 2.5*wid
posts = ndi.binary_dilation(keep[lab], iterations=4)
n = int(keep.sum())
fence_left = (fy > 2560) & (fy < 2700) & (np.arange(hw)[None, :]*2 > 280) & (np.arange(hw)[None, :]*2 < 820)
still = posts            # (the row on the left is tall weeds, they sway with the grass)
grass = smooth(fy, 2345, 2620) * (1 - ndi.gaussian_filter(still.astype(np.float32), 2.5).clip(0, 1)*1.6).clip(0, 1)

# ---------- depth for parallax (0 = sky/far, 1 = nearest grass)
Dn = np.clip(D / np.percentile(D, 99.5), 0, 1) ** 0.6
Dn = ndi.gaussian_filter(Dn, 1.5)
Dn[dist > 6] = 0.0                                           # sky stays exactly at infinity

quarter = lambda a: np.asarray(Image.fromarray(a.astype(np.float32)).resize((W//4, H//4), Image.BILINEAR))
out = np.dstack([quarter(sky), quarter(water), quarter(grass)])
Image.fromarray((np.clip(out, 0, 1)*255+0.5).astype(np.uint8), 'RGB').save('masks.png', optimize=True)
Image.fromarray((np.clip(quarter(Dn), 0, 1)*255+0.5).astype(np.uint8), 'L').save('depth.png', optimize=True)
prev = np.dstack([quarter(sky), quarter(water), quarter(grass)])
Image.fromarray((prev*255).astype(np.uint8)).save('preview-masks2_rgb.png')
ov = (np.asarray(im.resize((W//4, H//4)), dtype=np.float32)*0.55 + prev*255*0.45).astype(np.uint8)
Image.fromarray(ov).save('preview-masks2_overlay.jpg', quality=88)
json.dump({'ridge_full': (ridge*2).round(1).tolist()[::8]}, open('ridge.json', 'w'))
print('posts comps', n, '| ridge rows (full res) min/max', ridge.min()*2, ridge.max()*2)
