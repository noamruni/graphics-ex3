"""
Test runner for ray tracing scenes.

Usage:
    uv run test_scenes.py          # run all scenes
    uv run test_scenes.py 1        # run scene 1 only
    uv run test_scenes.py 1 2 4    # run scenes 1, 2, and 4
    uv run test_scenes.py --res 128  # run all at 128x128
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from hw3 import render_scene, your_own_scene
from helper_classes import *


def scene1():
    plane_a = Plane([0, 1, 0], [0, -1, 0])
    plane_a.set_material([1, 0.5, 1], [1, 0.5, 1], [1, 1, 1], 10, 0.5)
    plane_b = Plane([0, 0, 1], [0, 0, -3])
    plane_b.set_material([0, 0.5, 1], [0, 0.5, 1], [1, 1, 1], 10, 0.5)
    objects = [plane_a, plane_b]
    light = PointLight(intensity=np.array([1, 1, 1]), position=np.array([1, 1, 1]), kc=0.1, kl=0.1, kq=0.1)
    lights = [light]
    ambient = np.array([0.1, 0.1, 0.1])
    camera = np.array([0.5, 0.5, 1])
    return camera, ambient, lights, objects, 1


def scene2():
    v_list = np.array([[-1, 0, 0], [0, 0, -3], [0, 3, -2]])
    triangle = Triangle(*v_list)
    triangle.set_material([1, 1, 0], [1, 1, 0], [0, 0, 0], 100, 0.5)
    plane = Plane([0, 0, 1], [0, 0, -4])
    plane.set_material([0, 0.5, 0], [0.2, 0.5, 0.8], [.1, .1, .1], 100, 0.5)
    objects = [triangle, plane]
    light = DirectionalLight(intensity=np.array([1, 1, 1]), direction=np.array([-1, -1, -1]))
    lights = [light]
    ambient = np.array([0.1, 0.1, 0.1])
    camera = np.array([0, 0, 1])
    return camera, ambient, lights, objects, 1


def scene3():
    v_list = np.array([
        [-0.5, -0.142, -0.998],
        [-0.034, 0.092, -0.145],
        [0.484, 0.031, -0.998],
        [-0.104, 0.851, -0.828],
        [0.23, -0.833, -0.591]
    ])
    diamond = Diamond(v_list)
    diamond.set_material([0.1, 0.4, 0.7], [1, 0, 0], [0.7, 0.3, 0.3], 10, 0.5)
    diamond.apply_materials_to_triangles()
    plane = Plane([0, 1, 0], [0, -1, 0])
    plane.set_material([0.2, 0.2, 0.2], [0.2, 0.2, 0.2], [1, 1, 1], 1000, 0.5)
    background = Plane([0, 0, 1], [0, 0, -30])
    background.set_material([1, 0.3, 0.3], [1, 0.3, 0.3], [0.2, 0.2, 0.2], 10, 0.5)
    objects = [diamond, background, plane]
    light = PointLight(intensity=np.array([1, 1, 1]), position=np.array([0, 0, 1]), kc=0.1, kl=0.1, kq=0.1)
    lights = [light]
    ambient = np.array([0.1, 0.1, 0.1])
    camera = np.array([0, 0.5, 0.5])
    return camera, ambient, lights, objects, 3


def scene4():
    sphere_a = Sphere([-0.5, 0.2, -0.2], 0.5)
    sphere_a.set_material([1, 0, 0], [0, 0, 0.7], [0.3, 0.3, 0.3], 100, 1)
    sphere_b = Sphere([0.8, 0.9, -0.8], 0.4)
    sphere_b.set_material([0, 1, 0], [1, 0, 0], [0.3, 0.3, 0.3], 100, 0.2)
    plane = Plane([0, 1, 0], [0, -0.3, 0])
    plane.set_material([0.2, 0.2, 0.2], [0.2, 0.2, 0.2], [1, 1, 1], 1000, 0.5)
    background = Plane([0, 0, 1], [0, 0, -3])
    background.set_material([0.2, 0.2, 0.2], [0.2, 0.2, 0.2], [0.2, 0.2, 0.2], 1000, 0.5)
    objects = [sphere_a, sphere_b, plane, background]
    light = PointLight(intensity=np.array([1, 1, 1]), position=np.array([1, 1.5, 1]), kc=0.1, kl=0.1, kq=0.1)
    lights = [light]
    ambient = np.array([0.1, 0.2, 0.3])
    camera = np.array([0, 0, 1])
    return camera, ambient, lights, objects, 3


def scene5():
    background = Plane([0, 0, 1], [0, 0, -1])
    background.set_material([1, 1, 1], [1, 1, 1], [1, 1, 1], 1000, 0.5)
    objects = [background]
    light_a = SpotLight(intensity=np.array([0, 0, 1]), position=np.array([0.5, 0.5, 0]),
                        direction=([0, 0, -1]), kc=0.1, kl=0.1, kq=0.1)
    light_b = SpotLight(intensity=np.array([0, 1, 0]), position=np.array([-0.5, 0.5, 0]),
                        direction=([0, 0, -1]), kc=0.1, kl=0.1, kq=0.1)
    light_c = SpotLight(intensity=np.array([1, 0, 0]), position=np.array([0, -0.5, 0]),
                        direction=([0, 0, -1]), kc=0.1, kl=0.1, kq=0.1)
    lights = [light_a, light_b, light_c]
    ambient = np.array([0, 0, 0])
    camera = np.array([0, 0, 1])
    return camera, ambient, lights, objects, 3


def scene6():
    camera, lights, objects = your_own_scene()
    ambient = np.array([0, 0, 0])
    return camera, ambient, lights, objects, 3


SCENES = {
    1: ("Hello Ray Tracing - Two Planes", scene1),
    2: ("Triangles and Shadows", scene2),
    3: ("Diamond with Reflections", scene3),
    4: ("Sphere with Reflections", scene4),
    5: ("Different Lighting (Spotlights)", scene5),
    6: ("Custom Scene with Refraction", scene6),
}


def run_scene(num, resolution):
    title, setup_fn = SCENES[num]
    print(f"\n{'='*50}")
    print(f"Scene {num}: {title}")
    print(f"Resolution: {resolution}x{resolution}")
    print(f"{'='*50}")

    try:
        camera, ambient, lights, objects, max_depth = setup_fn()
    except Exception as e:
        print(f"  Setup failed: {e}")
        return

    start = time.time()
    try:
        im = render_scene(camera, ambient, lights, objects, (resolution, resolution), max_depth)
    except Exception as e:
        print(f"  Render failed: {e}")
        return
    elapsed = time.time() - start

    print(f"  Rendered in {elapsed:.2f}s")

    out_path = f"output_scenes/scene{num}.png"
    plt.imsave(out_path, im)
    print(f"  Saved to {out_path}")

    plt.figure(figsize=(4, 4))
    plt.imshow(im)
    plt.title(f"Scene {num}: {title}")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    args = sys.argv[1:]

    resolution = 64
    scene_nums = []

    i = 0
    while i < len(args):
        if args[i] == '--res' and i + 1 < len(args):
            resolution = int(args[i + 1])
            i += 2
        else:
            scene_nums.append(int(args[i]))
            i += 1

    if not scene_nums:
        scene_nums = list(SCENES.keys())

    print(f"Ray Tracing Test Runner")
    print(f"Running scenes: {scene_nums} at {resolution}x{resolution}")

    for num in scene_nums:
        if num not in SCENES:
            print(f"\nScene {num} does not exist. Available: {list(SCENES.keys())}")
            continue
        run_scene(num, resolution)

    print(f"\nDone! Check output_scenes/scene*.png files.")


if __name__ == '__main__':
    main()
