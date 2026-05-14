import numpy as np


# This function gets a vector and returns its normalized form.
def normalize(vector):
    return vector / np.linalg.norm(vector)


# This function gets a vector and the normal of the surface it hit
# This function returns the vector that reflects from the surface
def reflected(vector, axis):
    n = normalize(axis)
    return vector - 2 * np.dot(vector, n) * n

## Lights


class LightSource:
    def __init__(self, intensity):
        self.intensity = intensity


class DirectionalLight(LightSource):

    def __init__(self, intensity, direction):
        super().__init__(intensity)
        self.direction = normalize(np.array(direction, dtype=np.float64))

    def get_light_ray(self, intersection_point):
        return Ray(intersection_point - self.direction * 1000, self.direction)

    def get_distance_from_light(self, intersection):
        return np.inf

    def get_intensity(self, intersection):
        return self.intensity


class PointLight(LightSource):
    def __init__(self, intensity, position, kc, kl, kq):
        super().__init__(intensity)
        self.position = np.array(position)
        self.kc = kc
        self.kl = kl
        self.kq = kq

    # This function returns the ray that goes from the light source to a point
    def get_light_ray(self, intersection):
        return Ray(self.position, normalize(intersection - self.position))

    # This function returns the distance from a point to the light source
    def get_distance_from_light(self, intersection):
        return np.linalg.norm(self.position - intersection)

    # This function returns the light intensity at a point
    def get_intensity(self, intersection):
        d = self.get_distance_from_light(intersection)
        return self.intensity / (self.kc + self.kl * d + self.kq * d * d)


class SpotLight(LightSource):
    def __init__(self, intensity, position, direction, kc, kl, kq):
        super().__init__(intensity)
        self.position = np.array(position, dtype=np.float64)
        self.direction = normalize(np.array(direction, dtype=np.float64))
        self.kc = kc
        self.kl = kl
        self.kq = kq

    def get_light_ray(self, intersection):
        return Ray(self.position, normalize(intersection - self.position))

    def get_distance_from_light(self, intersection):
        return np.linalg.norm(self.position - intersection)

    def get_intensity(self, intersection):
        d = self.get_distance_from_light(intersection)
        vec_to_point = normalize(intersection - self.position)
        cos_angle = np.dot(vec_to_point, self.direction)
        return self.intensity * cos_angle / (self.kc + self.kl * d + self.kq * d * d)


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    # The function is getting the collection of objects in the scene and looks for the one with minimum distance.
    # The function should return the nearest object and its distance (in two different arguments)
    def nearest_intersected_object(self, objects):
        nearest_object = None
        min_distance = np.inf
        for obj in objects:
            result = obj.intersect(self)
            if result is not None:
                t, hit_obj = result
                if t < min_distance:
                    min_distance = t
                    nearest_object = hit_obj
        return nearest_object, min_distance


class Object3D:
    def set_material(self, ambient, diffuse, specular, shininess, reflection):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection


class Plane(Object3D):
    def __init__(self, normal, point):
        self.normal = np.array(normal)
        self.point = np.array(point)

    def intersect(self, ray: Ray):
        v = self.point - ray.origin
        t = np.dot(v, self.normal) / (np.dot(self.normal, ray.direction) + 1e-6)
        if t > 0:
            return t, self
        else:
            return None


class Triangle(Object3D):
    """
        C
        /\
       /  \
    A /____\ B

    The fornt face of the triangle is A -> B -> C.
    
    """
    def __init__(self, a, b, c):
        self.a = np.array(a)
        self.b = np.array(b)
        self.c = np.array(c)
        self.normal = self.compute_normal()

    def compute_normal(self):
        edge1 = self.b - self.a
        edge2 = self.c - self.a
        return normalize(np.cross(edge1, edge2))

    def intersect(self, ray: Ray):
        denom = np.dot(self.normal, ray.direction)
        if abs(denom) < 1e-6:
            return None
        t = np.dot(self.a - ray.origin, self.normal) / denom
        if t < 0:
            return None
        P = ray.origin + t * ray.direction
        # Barycentric coordinate test
        v0 = self.c - self.a
        v1 = self.b - self.a
        v2 = P - self.a
        d00 = np.dot(v0, v0)
        d01 = np.dot(v0, v1)
        d11 = np.dot(v1, v1)
        d20 = np.dot(v2, v0)
        d21 = np.dot(v2, v1)
        inv_denom = 1.0 / (d00 * d11 - d01 * d01)
        u = (d11 * d20 - d01 * d21) * inv_denom
        v = (d00 * d21 - d01 * d20) * inv_denom
        if u >= -1e-5 and v >= -1e-5 and u + v <= 1 + 1e-5:
            return t, self
        return None

class Diamond(Object3D):
    """     
            D
            /\*\
           /==\**\
         /======\***\
       /==========\***\
     /==============\****\
   /==================\*****\
A /&&&&&&&&&&&&&&&&&&&&\ B &&&/ C
   \==================/****/
     \==============/****/
       \==========/****/
         \======/***/
           \==/**/
            \/*/
             E 
    
    Similar to Traingle, every from face of the diamond's faces are:
        A -> B -> D
        B -> C -> D
        A -> C -> B
        E -> B -> A
        E -> C -> B
        C -> E -> A
    """
    def __init__(self, v_list):
        self.v_list = v_list
        self.triangle_list = self.create_triangle_list()

    def create_triangle_list(self):
        l = []
        t_idx = [
                [0,1,3],
                [1,2,3],
                [0,3,2],
                 [4,1,0],
                 [4,2,1],
                 [2,4,0]]
        for indices in t_idx:
            t = Triangle(self.v_list[indices[0]], self.v_list[indices[1]], self.v_list[indices[2]])
            l.append(t)
        return l

    def apply_materials_to_triangles(self):
        for t in self.triangle_list:
            t.set_material(self.ambient, self.diffuse, self.specular, self.shininess, self.reflection)

    def intersect(self, ray: Ray):
        min_t = np.inf
        nearest = None
        for t in self.triangle_list:
            result = t.intersect(ray)
            if result is not None and result[0] < min_t:
                min_t = result[0]
                nearest = result[1]
        if nearest is not None:
            return min_t, nearest
        return None

class Sphere(Object3D):
    def __init__(self, center, radius: float):
        self.center = np.array(center, dtype=np.float64)
        self.radius = radius

    def intersect(self, ray: Ray):
        L = ray.origin - self.center
        a = np.dot(ray.direction, ray.direction)
        b = 2 * np.dot(ray.direction, L)
        c = np.dot(L, L) - self.radius * self.radius
        disc = b * b - 4 * a * c
        if disc < 0:
            return None
        sqrt_disc = np.sqrt(disc)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)
        if t1 > 0:
            return t1, self
        elif t2 > 0:
            return t2, self
        return None

