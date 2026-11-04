bl_info = {
    "name": "AI Mesh Cleanup",
    "author": "Yangeok",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Cleanup",
    "description": "One-click cleanup for heavy, messy meshes (AI-generated / scanned): weld, remove loose and degenerate geometry, fix normals, reduce face count, report.",
    "category": "Mesh",
}

import bmesh
import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty


def mesh_stats(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    stats = {
        "verts": len(bm.verts),
        "faces": len(bm.faces),
        "loose": sum(1 for v in bm.verts if not v.link_edges)
        + sum(1 for e in bm.edges if not e.link_faces),
        "non_manifold": sum(1 for e in bm.edges if len(e.link_faces) != 2),
    }
    bm.free()
    return stats


def clean_topology(me, weld_dist, fill_holes, hole_sides, to_quads):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=weld_dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=weld_dist * 0.1)
    loose_edges = [e for e in bm.edges if not e.link_faces]
    bmesh.ops.delete(bm, geom=loose_edges, context="EDGES")
    loose_verts = [v for v in bm.verts if not v.link_edges]
    bmesh.ops.delete(bm, geom=loose_verts, context="VERTS")
    if fill_holes:
        boundary = [e for e in bm.edges if len(e.link_faces) == 1]
        if boundary:
            bmesh.ops.holes_fill(bm, edges=boundary, sides=hole_sides)
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if to_quads:
        tris = [f for f in bm.faces if len(f.verts) == 3]
        bmesh.ops.join_triangles(bm, faces=tris, angle_face_threshold=0.0872665, angle_shape_threshold=0.261799)
    bm.to_mesh(me)
    bm.free()
    me.update()


def reduce_faces(obj, target_faces):
    me = obj.data
    n = len(me.polygons)
    if target_faces <= 0 or n <= target_faces:
        return
    mod = obj.modifiers.new("_cleanup_decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = max(0.001, target_faces / n)
    mod.use_collapse_triangulate = False
    dg = bpy.context.evaluated_depsgraph_get()
    new_me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.remove(mod)
    old = obj.data
    obj.data = new_me
    new_me.name = old.name
    if old.users == 0:
        bpy.data.meshes.remove(old)


class MESH_OT_ai_cleanup(bpy.types.Operator):
    bl_idname = "mesh.ai_cleanup"
    bl_label = "Clean Up Mesh"
    bl_options = {"REGISTER", "UNDO"}

    weld_dist: FloatProperty(name="Weld Distance", default=0.0001, min=0.0, max=1.0, precision=6, unit="LENGTH")
    fill_holes: BoolProperty(name="Fill Small Holes", default=True)
    hole_sides: IntProperty(name="Max Hole Sides", default=8, min=3, max=64)
    to_quads: BoolProperty(name="Triangles to Quads", default=False)
    target_faces: IntProperty(name="Target Face Count (0 = keep)", default=0, min=0)

    @classmethod
    def poll(cls, context):
        return any(o.type == "MESH" for o in context.selected_objects)

    def execute(self, context):
        done = 0
        for obj in [o for o in context.selected_objects if o.type == "MESH"]:
            before = mesh_stats(obj.data)
            if obj.data.users > 1:
                obj.data = obj.data.copy()
            clean_topology(obj.data, self.weld_dist, self.fill_holes, self.hole_sides, self.to_quads)
            reduce_faces(obj, self.target_faces)
            after = mesh_stats(obj.data)
            self.report(
                {"INFO"},
                f"{obj.name}: faces {before['faces']:,} -> {after['faces']:,}, verts {before['verts']:,} -> {after['verts']:,}, "
                f"loose {before['loose']} -> {after['loose']}, open edges {before['non_manifold']} -> {after['non_manifold']}",
            )
            done += 1
        return {"FINISHED"} if done else {"CANCELLED"}


class VIEW3D_PT_ai_cleanup(bpy.types.Panel):
    bl_label = "AI Mesh Cleanup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Cleanup"

    def draw(self, context):
        col = self.layout.column()
        col.operator("mesh.ai_cleanup", icon="BRUSH_DATA")


classes = (MESH_OT_ai_cleanup, VIEW3D_PT_ai_cleanup)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
