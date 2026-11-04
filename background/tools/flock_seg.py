"""Optional. Finds the real flock in the photo (the strip it stood in is hard-coded).
In:  photo-day.jpg   Out: flock_mask.npy, flock_peaks.npy

This is the recipe used for the seeded sheep photo (photo-day.jpg). Run it from a folder that holds the photo."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
P = np.asarray(Image.open('photo-day.jpg').convert('RGB'), dtype=np.float32)/255
X0, Y0, X1, Y1 = 1230, 2262, 2410, 2356
c = P[Y0:Y1, X0:X1]; r, g, b = c[...,0], c[...,1], c[...,2]
ratio = b/(r+1e-3); lum = 0.2126*r + 0.7152*g + 0.0722*b
rows = np.arange(Y1-Y0)[:, None] + Y0
cols = np.arange(X1-X0)[None, :] + X0
top = np.where(cols < 1850, 2279, np.where(cols < 2000, 2284, 2289))          # pale dry grass strip above the right half of the flock
cream = (ratio > 0.62) & (ratio < 0.98) & (lum > 0.40) & (rows > top)
dark = (lum < 0.36) & (rows > 2280)
near = ndi.binary_dilation(cream, iterations=8)
sheep = cream | (dark & near)
sheep = ndi.binary_closing(sheep, iterations=1)
sheep = ndi.binary_fill_holes(sheep)
lab, n = ndi.label(sheep); sizes = ndi.sum(sheep, lab, range(1, n+1))
sheep = np.isin(lab, 1 + np.where(sizes >= 40)[0])
# backs: bright cream; one peak per animal
bright = (cream & (lum > 0.58)).astype(np.float32)
sm = ndi.gaussian_filter(bright, (2.2, 3.4))
fp = np.zeros((11, 17), bool); yy, xx = np.mgrid[-5:6, -8:9]; fp[(yy/5.5)**2 + (xx/8.5)**2 <= 1] = True
mx = ndi.maximum_filter(sm, footprint=fp, mode='constant')
peaks = np.argwhere((sm == mx) & (sm > 0.22) & sheep)
print('flock px', int(sheep.sum()), 'peaks', len(peaks))
np.save('flock_mask.npy', sheep); np.save('flock_peaks.npy', peaks)
vis = (c*255).astype(np.uint8).copy()
vis[sheep] = (vis[sheep]*0.55 + np.array([255, 40, 120])*0.45).astype(np.uint8)
for (py, px) in peaks:
    vis[max(0,py-1):py+2, max(0,px-1):px+2] = [0, 255, 255]
im = Image.fromarray(vis)
im.crop((0, 0, 600, 94)).resize((1800, 282), Image.NEAREST).save('preview-seg_left.png')
im.crop((580, 0, 1180, 94)).resize((1800, 282), Image.NEAREST).save('preview-seg_right.png')
