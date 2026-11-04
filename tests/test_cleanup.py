import sys, random, bpy, bmesh
sys.path.insert(0, "..")
import ai_mesh_cleanup as m
m.register()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=6, radius=1)
o = bpy.context.active_object
n0 = len(o.data.polygons)
bm = bmesh.new(); bm.from_mesh(o.data)
bmesh.ops.split_edges(bm, edges=bm.edges[:])           # "triangle soup": every face detached
for _ in range(50): bm.verts.new((random.uniform(-2,2),)*3)  # stray points
for f in random.sample(bm.faces[:], 500): f.normal_flip()
for f in random.sample(bm.faces[:], 20): bm.faces.remove(f)     # holes
bm.to_mesh(o.data); bm.free()
b = m.mesh_stats(o.data)
bpy.ops.mesh.ai_cleanup(target_faces=20000)
a = m.mesh_stats(o.data)
print("RESULT", n0, b, a)
assert b["loose"] >= 50 and b["non_manifold"] > 0
assert a["loose"] == 0 and a["faces"] <= 22000 and a["faces"] > 15000, a
print("TEST_OK")
