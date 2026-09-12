import constants
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_tri_2d, intersect_tri_tri_2d
from bpy_extras.object_utils import world_to_camera_view

def ensure_ccw(tri):
    """
    tri: list/tuple of 3 Vector3 (x, y, z).
    Returns a new list of 3 Vector3 in CCW order (as seen looking down -Z,
    i.e. standard screen/camera-space XY convention).
    If already CCW, returns tri unchanged (same vertex objects, same order).
    If CW, returns a copy with two vertices swapped to flip winding.
    Degenerate (zero-area) triangles are returned unchanged.
    """
    a, b, c = tri

    """Cross of ab and ac
    Positive = CCW, negative = CW, zero = degenerate/collinear."""
    cross = (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)

    if cross > 0:
        return [a, b, c]
    elif cross < 0:
        # Swap any two vertices to flip winding order
        return [a, c, b]
    else:
        # Degenerate triangle (collinear points) — no valid winding to fix
        return [a, b, c]

"""
Sutherland-Hodgman algorithm
Clip `subject` polygon against `clip` polygon (both convex, CCW, 2D).
Returns list of Vector2 representing the intersection polygon (may be empty).
"""
def find_intersection_polygon(subject, clip):
    def inside(p, a, b):
        # True if p is on the left side of edge a->b (CCW convex clip)
        edge = b - a
        return edge.cross(p - a) >= 0

    def intersect(p1, p2, a, b):
        edge_ab = b - a
        edge_p = p2 - p1
        denom = edge_p.cross(edge_ab)
        if abs(denom) < 1e-12:
            return p2  # parallel; fallback
        t = (a - p1).cross(edge_ab) / denom
        return p1 + edge_p * t

    output = subject[:]
    for i in range(len(clip)):
        if not output:
            break

        a = clip[i]
        b = clip[(i + 1) % len(clip)]
        input_list = output
        output = []

        for j in range(len(input_list)):
            curr = input_list[j]
            prev = input_list[j - 1]
            curr_in = inside(curr, a, b)
            prev_in = inside(prev, a, b)

            if curr_in:
                if not prev_in:
                    output.append(intersect(prev, curr, a, b))
                output.append(curr)

            elif prev_in:
                output.append(intersect(prev, curr, a, b))

    return output

def find_sample_point(polygon):
    """
    Returns the centroid Vector2 of the polygon if it has meaningful area (> 1e-6).
    Returns None if degenerate, collinear, or edge/vertex-only touching.
    """
    n = len(polygon)
    if n < 3:
        return None

    area2 = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        cross = p1.x * p2.y - p2.x * p1.y
        area2 += cross
        cx += (p1.x + p2.x) * cross
        cy += (p1.y + p2.y) * cross

    area = 0.5 * abs(area2)
    # Ignore zero-area or sliver intersections (< 0.4 of an 854x480 screen pixel)
    if area < constants.EPSILON:
        return None

    return Vector((cx / (3.0 * area2), cy / (3.0 * area2)))

"""
tri: 3 Vector3 (x, y, z) in CCW screen/camera space.
sample: Vector2 point known to be inside tri (2D).
Returns interpolated z at `sample` via barycentric weights.
"""
def find_barycentric_z(tri, sample):
    a, b, c = tri
    a2, b2, c2 = Vector((a.x, a.y)), Vector((b.x, b.y)), Vector((c.x, c.y))

    def area2(p, q, r):
        return (q - p).cross(r - p)

    total = area2(a2, b2, c2)
    if abs(total) < 1e-12:
        return None  # degenerate triangle

    w_a = area2(sample, b2, c2) / total
    w_b = area2(sample, c2, a2) / total
    w_c = 1.0 - w_a - w_b

    return w_a * a.z + w_b * b.z + w_c * c.z

# Orders triangles from back to front using topological sort
def order_triangles(triangles):
    # Order in world coordinates using topo sort
    graph = {i: [] for i in range(len(triangles))}
    indegree = {i: 0 for i in range(len(triangles))}

    # Build graphs
    for i in range(len(triangles)):
        for j in range(i + 1, len(triangles)):
            a, b = triangles[i][0], triangles[j][0]

            if not intersect_tri_tri_2d(a[0].xy, a[1].xy, a[2].xy, b[0].xy, b[1].xy, b[2].xy):
                continue

            a_ccw = ensure_ccw(a)
            b_ccw = ensure_ccw(b)

            a_2d = [Vector((v.x, v.y)) for v in a_ccw]
            b_2d = [Vector((v.x, v.y)) for v in b_ccw]

            intersection = find_intersection_polygon(a_2d, b_2d)
            sample = find_sample_point(intersection)
            if sample is None:
                continue  # Degenerate, collinear, or edge/vertex-only touching

            a_z = find_barycentric_z(a_ccw, sample)
            b_z = find_barycentric_z(b_ccw, sample)
            if a_z is None or b_z is None:
                continue

            if a_z < b_z - constants.EPSILON:
                # a is closer to camera (front), b is further (back) -> b drawn before a
                graph[j].append(i)
                indegree[i] += 1
            elif b_z < a_z - constants.EPSILON:
                # b is closer to camera (front), a is further (back) -> a drawn before b
                graph[i].append(j)
                indegree[j] += 1

    ordered = []

    # Sort with graph
    cycle = 0
    no_front = 0
    while indegree:
        smallest_indegree = min(indegree.values())
            
        for key in list(indegree.keys()):
            if indegree[key] > smallest_indegree:
                continue

            ordered.append(triangles[key])

            del indegree[key]

            for dep in graph[key]:
                if dep not in indegree:
                    cycle += 1
                    continue

                indegree[dep] -= 1

            if smallest_indegree > 0:
                no_front += 1
                break

    print("cycle", cycle)
    print("no_front", no_front)

    return ordered

# Occlude triangles that are fully behind by triangles in front
def occlude_triangles(triangles):
    occluded = []

    # Use reversed() to go from front -> back
    for triangle in reversed(triangles):
        tri_pts = triangle[0]

        # Skip triangle if a triangle in front fully covers it
        if any(
            all(
                intersect_point_tri_2d(
                    v.xy,
                    occlude[0][0].xy,
                    occlude[0][1].xy,
                    occlude[0][2].xy
                )
                for v in tri_pts
            )
            for occlude in occluded
        ):
            continue

        occluded.append(triangle)

    # Make sure to reverse back so that the final list is back -> front for rendering
    occluded.reverse()
    return occluded

def frame_triangles(scene, camera, materials):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    camera_location = camera.matrix_world.translation

    objects = []
    for object in scene.objects:
        if not object.visible_get():
            continue
        
        # Ignore things like camera and rigs
        if object.type != "MESH":
            continue
        
        # Only consider objects that have some scale value
        if object.scale.x == 0.0 or object.scale.y == 0.0 or object.scale.z == 0.0:
            continue
        
        objects.append(object)

    triangles = []
    for object in objects:
        evaluated = object.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()

        world_matrix = evaluated.matrix_world
        normal_matrix = world_matrix.to_3x3().inverted_safe().transposed()

        for loop_triangle in mesh.loop_triangles:
            # Cull if normal points away from camera
            world_normal = (normal_matrix @ loop_triangle.normal).normalized()
            to_camera = (camera_location - world_matrix @ mesh.vertices[loop_triangle.vertices[0]].co).normalized()
            if world_normal.dot(to_camera) <= 0:
                continue

            world_triangle = [world_matrix @ mesh.vertices[i].co for i in loop_triangle.vertices]

            # Bottom left origin where x and y are 0 to 1
            camera_triangle = [world_to_camera_view(scene, camera, v) for v in world_triangle]

            # Cull if any vertex is behind camera
            if any(v.z <= 0 for v in camera_triangle):
                continue

            # Cull if all outside edge
            if (all(v.x >= 1 for v in camera_triangle) or
                all(v.x <= 0 for v in camera_triangle) or
                all(v.y >= 1 for v in camera_triangle) or
                all(v.y <= 0 for v in camera_triangle)):
                continue

            # Get material file
            material = evaluated.material_slots[loop_triangle.material_index].material
            if not material:
                continue
            file = materials[material.name]

            triangles.append((camera_triangle, file))

        evaluated.to_mesh_clear()

    ordered = order_triangles(triangles)
    print('ordered', len(ordered))

    occluded = occlude_triangles(ordered)
    print('occluded', len(occluded))

    return occluded

