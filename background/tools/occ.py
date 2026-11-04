"""Optional. Fence posts and weeds that pass in front of the sheep.
In:  photo-day.jpg   Out: occ.png, occ.json (the rows for occluderRows)

This is the recipe used for the seeded sheep photo (photo-day.jpg). Run it from a folder that holds the photo."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
P = np.asarray(Image.open('photo-day.jpg').convert('RGB'), dtype=np.float32)/255
lum = 0.2126*P[...,0] + 0.7152*P[...,1] + 0.0722*P[...,2]
sat = (P.max(2) - P.min(2))/(P.max(2) + 1e-4)
Y0, Y1 = 2490, 2750
occ = np.zeros((Y1 - Y0, P.shape[1]), np.float32)
# the three fence posts: grey wood (dark side and sunlit side), grown from their dark core
for (x0, x1, ya, yb) in [(400, 436, 2528, 2668), (1340, 1378, 2550, 2702), (2357, 2400, 2558, 2730)]:
    sub_l = lum[ya:yb, x0:x1]; sub_s = sat[ya:yb, x0:x1]
    core = ndi.binary_opening(sub_l < 0.30, structure=np.ones((25, 1), bool))
    wood = (sub_s < 0.34) & (sub_l < 0.62)
    lab, n = ndi.label(wood | core)
    keep = np.isin(lab, np.unique(lab[core & (lab > 0)]))
    keep = ndi.binary_closing(keep, iterations=1)
    m = np.zeros_like(occ); m[ya - Y0:yb - Y0, x0:x1] = keep
    occ = np.maximum(occ, m)
# tall weeds by the left post stand in front of anything grazing behind them
wy0, wy1, wx0, wx1 = 2555, 2705, 270, 830
w = (lum[wy0:wy1, wx0:wx1] < 0.32)
w = ndi.binary_opening(w, structure=np.ones((9, 1), bool))
m = np.zeros_like(occ); m[wy0 - Y0:wy1 - Y0, wx0:wx1] = w
occ = np.maximum(occ, m*0.9)
occ = np.clip(ndi.gaussian_filter(occ, 0.7)*1.3, 0, 1)
Image.fromarray((occ*255 + 0.5).astype(np.uint8), 'L').save('occ.png', optimize=True)
json.dump({'occ': [Y0, Y1]}, open('occ.json', 'w'))
pv = (P[Y0:Y1, 250:2450]*255).astype(np.uint8).copy(); o = occ[:, 250:2450]
pv[..., 0] = np.clip(pv[..., 0]*(1 - o) + 255*o, 0, 255)
Image.fromarray(pv).resize((1100, 130)).save('preview-occ_prev.png')
print('occ px', int((occ > 0.5).sum()))
