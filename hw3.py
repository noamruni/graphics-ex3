from helper_classes import *
import matplotlib.pyplot as plt

EPSILON = 1e-5


def get_normal(obj, point):
    if isinstance(obj, Sphere):
        return normalize(point - np.array(obj.center))
    elif isinstance(obj, Triangle):
        return obj.normal
    elif isinstance(obj, Plane):
        return obj.normal
    return np.zeros(3)


def compute_color(ray, objects, lights, ambient, camera, depth):
    if depth == 0:
        return np.zeros(3)

    nearest_object, t = ray.nearest_intersected_object(objects)
    if nearest_object is None:
        return np.zeros(3)

    intersection = ray.origin + t * ray.direction
    normal = get_normal(nearest_object, intersection)

    # Flip normal if it faces away from the ray
    if np.dot(normal, ray.direction) > 0:
        normal = -normal

    color = np.array(nearest_object.ambient, dtype=np.float64) * ambient

    for light in lights:
        light_ray = light.get_light_ray(intersection)
        if isinstance(light, DirectionalLight):
            light_dir = -light.direction
        else:
            light_dir = normalize(light.position - intersection)
        light_distance = light.get_distance_from_light(intersection)

        # Shadow check (transparent objects don't fully block light)
        shadow_origin = intersection + EPSILON * normal
        shadow_ray = Ray(shadow_origin, light_dir)
        shadow_obj, shadow_dist = shadow_ray.nearest_intersected_object(objects)
        if shadow_obj is not None and shadow_dist < light_distance:
            if getattr(shadow_obj, 'refraction', 0) > 0:
                pass  # transparent object — light passes through
            else:
                continue

        intensity = light.get_intensity(intersection)

        # Diffuse
        n_dot_l = max(0, np.dot(normal, light_dir))
        color += np.array(nearest_object.diffuse, dtype=np.float64) * intensity * n_dot_l

        # Specular
        view_dir = normalize(camera - intersection)
        reflect_dir = reflected(-light_dir, normal)
        r_dot_v = max(0, np.dot(reflect_dir, view_dir))
        color += np.array(nearest_object.specular, dtype=np.float64) * intensity * (r_dot_v ** nearest_object.shininess)

    # Reflection
    if depth > 1 and nearest_object.reflection > 0:
        reflect_ray_dir = reflected(ray.direction, normal)
        reflect_origin = intersection + EPSILON * normal
        reflect_ray = Ray(reflect_origin, normalize(reflect_ray_dir))
        reflected_color = compute_color(reflect_ray, objects, lights, ambient, camera, depth - 1)
        color += reflected_color * nearest_object.reflection

    # Refraction (simplified - ray continues in same direction)
    refraction = getattr(nearest_object, 'refraction', 0)
    if depth > 1 and refraction > 0:
        refracted_origin = intersection - EPSILON * normal
        refracted_ray = Ray(refracted_origin, ray.direction)
        refracted_color = compute_color(refracted_ray, objects, lights, ambient, camera, depth - 1)
        color = color * (1 - refraction) + refracted_color * refraction

    return color


def render_scene(camera, ambient, lights, objects, screen_size, max_depth):
    width, height = screen_size
    ratio = float(width) / height
    screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom

    image = np.zeros((height, width, 3))

    for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
        for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
            # screen is on origin
            pixel = np.array([x, y, 0])
            origin = camera
            direction = normalize(pixel - origin)
            ray = Ray(origin, direction)

            color = compute_color(ray, objects, lights, ambient, camera, max_depth)

            # We clip the values between 0 and 1 so all pixel values will make sense.
            image[i, j] = np.clip(color, 0, 1)

    return image


def your_own_scene():
    # Crystal ball: transparent sphere containing a diamond
    glass_sphere = Sphere([0, 0.3, -0.5], 0.6)
    glass_sphere.set_material([0.01, 0.01, 0.02], [0.02, 0.02, 0.05], [1, 1, 1], 300, 0.05, refraction=0.95)

    # Red gem diamond inside the sphere
    v_list = np.array([
        [-0.15, 0.15, -0.5],
        [0.15, 0.15, -0.35],
        [0.15, 0.15, -0.65],
        [0.0, 0.5, -0.5],
        [0.0, 0.0, -0.5]
    ])
    diamond = Diamond(v_list)
    diamond.set_material([0.7, 0.05, 0.05], [1.0, 0.1, 0.1], [1, 0.5, 0.5], 60, 0.2)
    diamond.apply_materials_to_triangles()

    # Left triangle
    tri_left = Triangle([-1.5, -0.5, -2.0], [-1.0, -0.5, -1.5], [-1.2, 0.5, -1.7])
    tri_left.set_material([0.1, 0.3, 0.6], [0.2, 0.4, 0.8], [1, 1, 1], 100, 0.3)

    # Right triangle
    tri_right = Triangle([1.0, -0.5, -1.5], [1.5, -0.5, -2.0], [1.2, 0.5, -1.7])
    tri_right.set_material([0.1, 0.6, 0.3], [0.2, 0.8, 0.4], [1, 1, 1], 100, 0.3)

    # Floor plane
    floor = Plane([0, 1, 0], [0, -0.5, 0])
    floor.set_material([0.2, 0.2, 0.2], [0.3, 0.3, 0.3], [0.6, 0.6, 0.6], 500, 0.3)

    # Background plane
    background = Plane([0, 0, 1], [0, 0, -5])
    background.set_material([0.05, 0.02, 0.1], [0.1, 0.05, 0.15], [0, 0, 0], 10, 0.0)

    objects = [glass_sphere, diamond, tri_left, tri_right, floor, background]

    # Warm point light from upper left
    light1 = PointLight(intensity=np.array([1.5, 1.3, 1.0]), position=np.array([-2, 2, 1]), kc=0.1, kl=0.05, kq=0.02)
    # Cool spotlight from upper right
    light2 = SpotLight(intensity=np.array([1.0, 1.2, 1.5]), position=np.array([2, 2, 0]),
                       direction=[-1, -1, -1], kc=0.1, kl=0.05, kq=0.02)

    lights = [light1, light2]
    camera = np.array([0, 0.5, 2])

    return camera, lights, objects
