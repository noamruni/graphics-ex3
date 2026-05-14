# Ray Tracing Assignment - Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Task 1: Pinhole Camera](#task-1-pinhole-camera-7-points)
4. [Task 2: Ray-Object Intersections](#task-2-ray-object-intersections)
5. [Task 3: Lighting Model](#task-3-lighting-model)
6. [Task 4: Hard Shadows](#task-4-hard-shadows-5-points)
7. [Task 5: Reflections](#task-5-reflections-10-points)
8. [Task 6: Custom Scene with Refraction](#task-6-custom-scene-with-refraction-10-points)
9. [Implementation Order](#implementation-order)

---

## Overview

A ray tracer works by shooting rays from a camera through each pixel of a virtual screen into a 3D scene. For each ray, we:
1. Find the closest object it intersects
2. Calculate the color at that intersection point using lighting equations
3. Optionally trace reflected/refracted rays recursively

**Key files:**
- `helper_classes.py` — Contains classes for rays, lights, and 3D objects
- `hw3.py` — Contains `render_scene()` (main render loop) and `your_own_scene()`
- `Ray Tracing Assignment.ipynb` — Test scenes and expected outputs

---

## Architecture

```
Camera  --->  Screen Pixel  --->  Ray  --->  Scene
  |                                           |
  |                                     Find nearest
  |                                     intersection
  |                                           |
  |                                     Calculate color:
  |                                       - Ambient
  |                                       - Diffuse
  |                                       - Specular
  |                                       - Shadow check
  |                                       - Reflection (recursive)
  |                                           |
  v                                           v
Final Image  <--------------------------  Pixel Color
```

---

## Task 1: Pinhole Camera (7 points)

### Learning Material
The pinhole camera model is the simplest camera model. It projects 3D points onto a 2D image plane through a single point (the camera/eye position).

**Key concepts:**
- The screen (image plane) is at z=0
- The camera is at some position (typically z>0, looking toward negative z)
- A ray goes FROM the camera THROUGH each pixel on the screen INTO the scene

**Resource:** [Scratchapixel - Ray Tracing: Generating Camera Rays](https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-generating-camera-rays)

### What's Already Given
In `hw3.py`, the render loop already:
- Maps pixel coordinates (i, j) to screen-space coordinates (x, y)
- Creates a ray from camera through the pixel
- Clips the final color to [0, 1]

### Subtasks

#### 1.1 Implement `reflected()` in `helper_classes.py`
The reflection formula for a vector `v` about a normal `n`:

```
r = v - 2 * dot(v, n) * n
```

Where `n` must be normalized. This is used later for specular highlights and mirror reflections.

#### 1.2 Implement `nearest_intersected_object()` in class `Ray`
This method iterates over all objects, calls each object's `intersect()` method, and returns the closest hit.

**Algorithm:**
1. For each object in the scene, call `object.intersect(ray)`
2. If the result is not `None` and the distance `t` is smaller than current minimum, update
3. Return the nearest object and its distance

**Important:** For `Diamond` objects, calling `intersect()` may return the nearest triangle within the diamond. Handle accordingly.

#### 1.3 Implement the main color computation loop in `render_scene()`
After finding the nearest intersection:
1. Compute intersection point: `point = origin + t * direction`
2. Determine the surface normal at that point
3. For each light, compute the color contribution (ambient + diffuse + specular)
4. Add shadow checking
5. Add reflection (recursive ray tracing)

**For Scene 1 (validation):** You only need basic color computation — two planes with a point light.

---

## Task 2: Ray-Object Intersections

### 2A: Triangles (8 points)

#### Learning Material
Ray-triangle intersection uses two steps:
1. Find where the ray hits the triangle's plane
2. Check if the hit point is inside the triangle (using barycentric coordinates)

**Resource:** [Scratchapixel - Ray-Triangle Intersection](https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle)

#### Subtasks

##### 2A.1 Implement `compute_normal()` in `Triangle`
The normal of a triangle with vertices A, B, C is:
```
normal = normalize(cross(B - A, C - A))
```

The order matters! The front face is A -> B -> C (counter-clockwise), so the normal points toward the viewer using the right-hand rule.

##### 2A.2 Implement `intersect()` in `Triangle`
**Algorithm (Moller-Trumbore or barycentric):**

1. Compute the plane intersection parameter `t` using the triangle's normal:
   ```
   denom = dot(normal, ray.direction)
   if abs(denom) < epsilon: return None  # ray parallel to triangle
   t = dot(A - ray.origin, normal) / denom
   if t < 0: return None  # triangle behind ray
   ```

2. Compute intersection point: `P = ray.origin + t * ray.direction`

3. Check if P is inside triangle using barycentric coordinates:
   - Compute vectors: `v0 = C - A`, `v1 = B - A`, `v2 = P - A`
   - Compute dot products: `d00 = dot(v0,v0)`, `d01 = dot(v0,v1)`, `d11 = dot(v1,v1)`, `d20 = dot(v2,v0)`, `d21 = dot(v2,v1)`
   - Compute barycentric coords: `u = (d11*d20 - d01*d21) / (d00*d11 - d01*d01)`, `v = (d00*d21 - d01*d20) / (d00*d11 - d01*d01)`
   - Point is inside if: `u >= 0` and `v >= 0` and `u + v <= 1` (use small epsilon for float tolerance)

4. If inside, return `(t, self)`. Otherwise return `None`.

---

### 2B: Diamonds (15 points)

#### Learning Material
A diamond is simply a collection of triangles forming a closed 3D shape. The intersection test checks all constituent triangles and returns the nearest hit.

#### Subtasks

##### 2B.1 Implement `create_triangle_list()` in `Diamond`
Using the vertex indices provided in `t_idx`, create `Triangle` objects:
```
for indices in t_idx:
    triangle = Triangle(v_list[indices[0]], v_list[indices[1]], v_list[indices[2]])
    l.append(triangle)
```

##### 2B.2 Implement `apply_materials_to_triangles()`
Copy the diamond's material properties to each triangle in the list:
```
for triangle in self.triangle_list:
    triangle.set_material(self.ambient, self.diffuse, self.specular, self.shininess, self.reflection)
```

##### 2B.3 Implement `intersect()` in `Diamond`
Find the nearest triangle intersection:
1. For each triangle in `self.triangle_list`, call `triangle.intersect(ray)`
2. Return the closest hit `(min_t, closest_triangle)` or `None`

---

### 2C: Spheres (15 points)

#### Learning Material
Ray-sphere intersection uses the quadratic formula. A sphere is defined by center `C` and radius `r`. A point `P` is on the sphere if `|P - C|^2 = r^2`.

**Resource:** [Scratchapixel - Ray-Sphere Intersection](https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection)

#### Subtasks

##### 2C.1 Implement `intersect()` in `Sphere`
**Algorithm:**
1. Let `L = ray.origin - self.center`
2. Compute quadratic coefficients:
   - `a = dot(ray.direction, ray.direction)` (should be 1 if direction is normalized)
   - `b = 2 * dot(ray.direction, L)`
   - `c = dot(L, L) - self.radius^2`
3. Compute discriminant: `disc = b^2 - 4*a*c`
4. If `disc < 0`: no intersection, return `None`
5. Compute solutions: `t1 = (-b - sqrt(disc)) / (2*a)`, `t2 = (-b + sqrt(disc)) / (2*a)`
6. Return the smallest positive `t`:
   - If `t1 > 0`: return `(t1, self)`
   - Elif `t2 > 0`: return `(t2, self)` (ray origin inside sphere)
   - Else: return `None`

**Normal at intersection point:** `normalize(point - self.center)`

---

## Task 3: Lighting Model

### Learning Material
We use the **Phong reflection model** which has three components:
- **Ambient**: constant base illumination
- **Diffuse**: light scattered equally in all directions (Lambert's cosine law)
- **Specular**: bright highlight from mirror-like reflection

**Formula:**
```
color = ambient_color * ambient_light
      + SUM over lights:
          * diffuse_color * intensity * max(0, dot(N, L))
          + specular_color * intensity * max(0, dot(R, V))^shininess
```

Where:
- `N` = surface normal
- `L` = direction FROM intersection point TO light
- `V` = direction FROM intersection point TO camera
- `R` = reflection of light direction about normal

**Resource:** [Learn OpenGL - Basic Lighting](https://learnopengl.com/Lighting/Basic-Lighting)

---

### 3A: Ambient Light (5 points)

#### Subtasks

##### 3A.1 Apply ambient lighting in `render_scene()`
```
color = object.ambient * ambient_light
```
This is the simplest component — just multiply the object's ambient coefficient by the scene's ambient intensity.

---

### 3B: Directional Light (7 points)

#### Learning Material
A directional light has no position — it represents infinitely distant light (like the sun). All rays are parallel and travel in the same direction. The intensity does not attenuate with distance.

#### Subtasks

##### 3B.1 Implement `DirectionalLight.__init__()`
Store the normalized direction vector (the direction the light shines).

##### 3B.2 Implement `get_light_ray()`
The light ray goes FROM far away TOWARD the intersection point. The origin should be far along the opposite direction:
```
origin = intersection_point - self.direction * large_number  # or just use direction
direction = normalize(self.direction)
```
Actually, think of it as: the ray travels in `self.direction`. So the "source" is at `intersection - direction * infinity`. For shadow rays, the origin is the intersection point and direction is toward the light: `-self.direction`.

##### 3B.3 Implement `get_distance_from_light()`
For directional lights, return `np.inf` (infinite distance — used for shadow comparison).

##### 3B.4 Implement `get_intensity()`
Return `self.intensity` directly (no attenuation).

---

### 3C: Spotlight (8 points)

#### Learning Material
A spotlight is a point light with a preferred direction. It combines position-based attenuation with angular falloff. The intensity is modulated by how closely the point-to-light direction aligns with the spotlight's direction.

**Intensity formula:**
```
I = intensity * dot(direction_to_point, spot_direction) / (kc + kl*d + kq*d^2)
```

#### Subtasks

##### 3C.1 Implement `SpotLight.__init__()`
Store: position, direction (normalized), kc, kl, kq.

##### 3C.2 Implement `get_light_ray()`
Same as PointLight: ray from light position toward intersection.

##### 3C.3 Implement `get_distance_from_light()`
Euclidean distance from position to intersection point.

##### 3C.4 Implement `get_intensity()`
```
d = distance to intersection
vec_to_point = normalize(intersection - self.position)
cos_angle = dot(vec_to_point, normalize(self.direction))
intensity = self.intensity * cos_angle / (kc + kl*d + kq*d^2)
```

---

### 3D: PointLight `get_distance_from_light()` and `get_intensity()`

#### Subtasks

##### 3D.1 Implement `get_distance_from_light()`
```
return np.linalg.norm(self.position - intersection)
```

##### 3D.2 Implement `get_intensity()`
```
d = self.get_distance_from_light(intersection)
return self.intensity / (self.kc + self.kl * d + self.kq * d * d)
```

---

### 3E: Material/Phong Shading (10 points)

#### Subtasks

##### 3E.1 Compute diffuse component
```
L = normalize(light_position - intersection)  # or -light_direction for directional
diffuse = object.diffuse * light_intensity * max(0, dot(N, L))
```

##### 3E.2 Compute specular component
```
V = normalize(camera - intersection)
R = reflected(-L, N)  # reflect light direction about normal
specular = object.specular * light_intensity * max(0, dot(R, V)) ** object.shininess
```

##### 3E.3 Combine in render loop
```
color = ambient_component
for light in lights:
    color += diffuse + specular  # (per light)
```

---

## Task 4: Hard Shadows (5 points)

### Learning Material
To check if a point is in shadow, cast a **shadow ray** from the intersection point toward the light source. If the ray hits any object before reaching the light, the point is in shadow (skip diffuse and specular for that light).

**Important tip:** Offset the shadow ray origin slightly above the surface to avoid self-intersection (shadow acne):
```
shadow_origin = intersection_point + epsilon * normal
```

**Resource:** [Scratchapixel - Shadows](https://www.scratchapixel.com/lessons/3d-basic-rendering/introduction-to-shading/ligth-and-shadows)

### Subtasks

#### 4.1 Cast shadow ray
```
shadow_ray_origin = intersection + epsilon * normal
shadow_ray_direction = normalize(light_position - intersection)  # or -light.direction
shadow_ray = Ray(shadow_ray_origin, shadow_ray_direction)
```

#### 4.2 Check for occlusion
```
shadow_object, shadow_dist = shadow_ray.nearest_intersected_object(objects)
light_distance = light.get_distance_from_light(intersection)

if shadow_object is not None and shadow_dist < light_distance:
    # Point is in shadow for this light — skip diffuse and specular
    continue
```

---

## Task 5: Reflections (10 points)

### Learning Material
Mirror reflections are implemented by recursively tracing rays. When a ray hits a reflective surface, compute the reflected ray direction and trace it into the scene. The reflected color is blended with the local color using the object's reflection coefficient.

**Reflection direction:**
```
R = reflected(ray.direction, normal)
  = ray.direction - 2 * dot(ray.direction, normal) * normal
```

**Resource:** [Scratchapixel - Reflection](https://www.scratchapixel.com/lessons/3d-basic-rendering/introduction-to-shading/reflection-refraction-fresnel)

### Subtasks

#### 5.1 Implement recursive ray tracing
Convert the color computation into a recursive function (or use a loop with depth):

```python
def trace_ray(ray, objects, lights, ambient, camera, depth):
    if depth == 0:
        return np.zeros(3)
    
    nearest_object, t = ray.nearest_intersected_object(objects)
    if nearest_object is None:
        return np.zeros(3)  # background color
    
    intersection = ray.origin + t * ray.direction
    normal = get_normal(nearest_object, intersection)
    
    # Compute local color (ambient + diffuse + specular with shadows)
    color = compute_local_color(...)
    
    # Compute reflection
    reflected_dir = reflected(ray.direction, normal)
    reflected_origin = intersection + epsilon * normal
    reflected_ray = Ray(reflected_origin, reflected_dir)
    reflected_color = trace_ray(reflected_ray, objects, lights, ambient, camera, depth - 1)
    
    color = color * (1 - nearest_object.reflection) + reflected_color * nearest_object.reflection
    # OR simply: color += reflected_color * nearest_object.reflection
    
    return color
```

#### 5.2 Handle normals for different objects
You need a helper to get the normal at an intersection point:
- **Plane**: `plane.normal`
- **Triangle**: `triangle.normal`
- **Sphere**: `normalize(intersection - sphere.center)`

#### 5.3 Set `max_depth` from `render_scene` parameter
The `max_depth` parameter controls recursion depth. Scene 1 uses depth=1 (no reflections), Scenes 3-6 use depth=3.

---

## Task 6: Custom Scene with Refraction (10 points)

### Learning Material
Refraction occurs when light passes through transparent objects. In this simplified version, the refracted ray continues in the **same direction** as the incoming ray (no bending).

This means when a ray hits a transparent object, part of the light reflects and part continues straight through.

### Subtasks

#### 6.1 Add refraction coefficient to materials
Add a `refraction` parameter (default 0) to `set_material()` or as a separate attribute. A value of 0 means fully opaque; higher values mean more transparent.

#### 6.2 Implement refraction in trace_ray
When hitting a refractive object:
```python
if hasattr(nearest_object, 'refraction') and nearest_object.refraction > 0:
    refracted_origin = intersection - epsilon * normal  # go through the surface
    refracted_ray = Ray(refracted_origin, ray.direction)  # same direction (simplified)
    refracted_color = trace_ray(refracted_ray, objects, lights, ambient, camera, depth - 1)
    
    color = color * (1 - nearest_object.refraction) + refracted_color * nearest_object.refraction
```

#### 6.3 Design your scene in `your_own_scene()`
Requirements:
- At least 2 different light sources
- Plane + at least 2 different 3D objects
- Inner object visible through outer object

---

## Implementation Order

Follow this order to build incrementally, validating with each scene:

| Step | What to Implement | Validates With |
|------|-------------------|----------------|
| 1 | `reflected()`, `nearest_intersected_object()`, basic render loop with ambient only | Partial Scene 1 |
| 2 | `PointLight.get_distance_from_light()`, `PointLight.get_intensity()`, diffuse + specular | Scene 1 |
| 3 | `Triangle.compute_normal()`, `Triangle.intersect()` | Scene 2 (partial) |
| 4 | `DirectionalLight` (all methods) | Scene 2 (partial) |
| 5 | Shadow rays | Scene 2 (complete) |
| 6 | `Diamond` (all methods) | Scene 3 (partial) |
| 7 | Reflections (recursive tracing) | Scene 3 (complete) |
| 8 | `Sphere.intersect()` | Scene 4 |
| 9 | `SpotLight` (all methods) | Scene 5 |
| 10 | Refraction + custom scene | Scene 6 |

---

## Quick Reference: Normal Computation

| Object | Normal at Point P |
|--------|-------------------|
| Plane | `plane.normal` (constant everywhere) |
| Triangle | `triangle.normal` (constant, from `compute_normal()`) |
| Sphere | `normalize(P - sphere.center)` |

---

## Common Pitfalls

1. **Shadow acne**: Always offset shadow/reflection ray origins by `epsilon * normal`
2. **Float precision**: Use epsilon (~1e-5) for barycentric coordinate checks
3. **Normal direction**: Ensure normals point toward the camera. If `dot(normal, ray.direction) > 0`, flip the normal
4. **Self-intersection**: The same object that was hit should not block its own shadow ray
5. **Diamond intersect**: Returns the nearest triangle, not the diamond itself — material must be on each triangle
6. **Light direction convention**: `L` in Phong should point FROM surface TO light, not the other way

---

## Commit Strategy

We will implement and commit in this order:
1. `reflected()` + `nearest_intersected_object()` + basic render loop
2. `PointLight` completion + Phong shading (Scene 1 works)
3. `Triangle` intersection (Scene 2 partial)
4. `DirectionalLight` + shadows (Scene 2 complete)
5. `Diamond` (Scene 3 partial)
6. Reflections (Scene 3 complete)
7. `Sphere` (Scene 4)
8. `SpotLight` (Scene 5)
9. Refraction + custom scene (Scene 6)
