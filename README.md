# AI Mesh Cleanup

A small Blender add-on that cleans up heavy, messy meshes (for example AI-generated or scanned models) in one click.

## What it does
- Welds vertices that are closer than a set distance
- Removes loose vertices and edges and degenerate geometry
- Recalculates face normals so they point the same way
- Optionally fills small holes (up to a chosen number of sides)
- Optionally converts triangles to quads
- Optionally reduces the face count to a target number
- Reports faces, vertices, loose parts and open edges before and after

## Install
1. Download the `ai_mesh_cleanup` folder as a zip (or use the release zip).
2. Blender: Edit > Preferences > Add-ons > Install from Disk, choose the zip.
3. Enable "AI Mesh Cleanup". The panel appears in the 3D View sidebar (N) under the "Cleanup" tab.

## Test
Run headless with Blender 5.2:

```
blender -b --python tests/test_cleanup.py
```

The test builds a broken sphere (detached faces, stray points, flipped normals, holes), runs the cleanup and checks the result.

## Status
Prototype (v0.1). Tested with Blender 5.2.3 on synthetic data only. Not yet tested on very large (millions of faces) models or for UV and texture preservation.

## License
GPL-3.0-or-later, as Blender add-ons that use the `bpy` API are required to be GPL-compatible. See `LICENSE`.
