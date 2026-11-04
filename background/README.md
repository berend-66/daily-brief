# The living background

How the daytime photo comes alive, and how to do the same with your own photo.

## What runs

All of it is in [`page/index.html`](../page/index.html): plain JavaScript and WebGL, no libraries, no video. It draws about 30 frames a second, only while the daytime photo is on screen. It pauses when the page is hidden and stays still if the phone has Reduce Motion on.

- **The photo.** A small GPU program runs on every pixel each frame. It shifts the sky sideways with a slight billow (the clouds drift), makes the lake glint, and lays in the "clean plate": grass painted where the real flock stood.
- **The sheep.** A second GPU program draws each sheep from simple shapes (wool body, head, ears, four legs). Legs swing and the body bobs as they walk. They cast a soft shadow, and fence posts and weeds pass in front of them.
- **Their behaviour.** Each sheep is a small state machine in JavaScript: graze, look up, walk, each on a random timer. A walk picks a random free spot inside the fenced field, turns and heads there.
- **Perspective.** Positions live on a flat ground in metres and are projected into the photo with a pinhole camera fitted to it, so a sheep further away is smaller and higher in the frame.

Because the sheep are simulated, it never repeats.

## The files it reads

All of them live in `page/`, next to `index.html`. The numbers that go with them are `scene` in `BRIEF_CONFIG` (defaults: the sheep photo).

| File | What it holds | Needed for |
|---|---|---|
| `photo-day.jpg` | the photo itself, with its colour profile kept | everything |
| `masks.png` | quarter size: red = sky, green = water (blue = grass, unused) | clouds, water |
| `sky-matte.png` | full width, over the rows in `skyRows`: how much sky each pixel holds | clouds |
| `ridge.png` | the skyline row of every column (16-bit fixed point ×8, in red and green) | clouds |
| `sky-fill.jpg` | half size: what lies behind the skyline, so drifting clouds never show a hole | clouds |
| `flock-clean.png` | grass painted over things that should go (here, the real flock), placed at `clean` | optional |
| `occ.png` | over the rows in `occluderRows`: things that pass in front of the animals | optional |
| `depth.png` | a quarter-size depth map, for a parallax effect that is switched off | optional |

The optional files can simply be missing; the page stands in a blank for them.

## Bring your own photo to life

Do this with Claude: point it at this folder and your photo. The steps:

1. **Pick a photo** with a clear skyline and, ideally, water. A portrait photo suits a phone best: the page frames it the way CSS `background-size: cover` does, at `position`.
2. **Replace `page/photo-day.jpg`** with yours. Keep its colour profile (Display P3 or sRGB, embedded).
3. **Build the masks** with the scripts in [`tools/`](tools/). They are the exact recipe used for the sheep photo, so their row ranges and colour thresholds need adapting to yours. Check every output by laying it over the photo before moving on.
   - `depth.py` (optional): a depth map with Depth Anything V2 Small, which helps find the skyline.
   - `masks.py`: sky, water and grass → `masks.png`, `depth.png` and a rough skyline.
   - `sky.py`: the exact skyline → `sky-matte.png`, `ridge.png`, and the rows for `skyRows`.
   - `skyfill.py`: what lies behind the skyline → `sky-fill.jpg`.
   - `flock_seg.py` and `flock.py` (optional): paint out anything that shouldn't stay → `flock-clean.png`.
   - `occ.py` (optional): things in front of the animals → `occ.png`.
4. **Set the scene** in `BRIEF_CONFIG` at the top of `page/index.html`. A photo with sky and water but no sheep:
   ```js
   scene: {
     size: [3024, 4032],          // your photo's width and height
     position: [0.5, 0.5],        // how it's framed on screen
     skyRows: [900, 1500],        // from sky.json
     clean: null,                 // nothing painted out
     sheep: false                 // no animals
   }
   ```
5. **Animals on the ground (optional).** Sheep need the ground plane: the `horizon` row (where the ground would meet the sky), `groundScale` and `f` solved from two things of known size or distance (fence posts, a person), the `field` they may wander, and the near `posts`. `bodyLength` sets their size. The sheep shader (`FS_SHEEP`) can be restyled, or swapped for another animal.
6. **Preview** with `python3 -m http.server` in `page/` and open http://localhost:8000. It shows example data and the living background. Then publish it (step 4 of [`CLAUDE.md`](../CLAUDE.md)).

Clouds and water work on most landscapes. Things worth trying: boats bobbing on a lake, birds crossing the sky, falling snow.

## Credits

The photos are by Berend van Nieuwland. You're welcome to use them in your own Daily brief.
