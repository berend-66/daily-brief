"""Optional. A depth map of the photo with Depth Anything V2 Small (ONNX), used by masks.py to find the skyline.
Needs onnxruntime and depth_anything_v2_vits.onnx next to this script.
In:  photo-day.jpg   Out: depth_raw518.npy

This is the recipe used for the seeded sheep photo (photo-day.jpg). Run it from a folder that holds the photo."""
import numpy as np, onnxruntime as ort, time
from PIL import Image
im = Image.open('photo-day.jpg').convert('RGB')
W, H = im.size
x = np.asarray(im.resize((518, 518), Image.BICUBIC), dtype=np.float32) / 255.0
x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
x = x.transpose(2, 0, 1)[None].astype(np.float32)
s = ort.InferenceSession('depth_anything_v2_vits.onnx', providers=['CPUExecutionProvider'])
t = time.time(); d = s.run(None, {s.get_inputs()[0].name: x})[0][0]; print('inference %.1fs' % (time.time() - t))
print('raw range', d.min(), d.max())
np.save('depth_raw518.npy', d)
v = (d - d.min()) / (d.max() - d.min())
Image.fromarray((v * 255).astype(np.uint8)).resize((756, 1008), Image.BICUBIC).save('preview-depth_preview.png')
