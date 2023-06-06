import math

import numpy as np
from pygame import gfxdraw

import colorsys


def generate_distinct_colors(n):
    colors = []
    hue_values = [i / n for i in range(n)]
    saturation = 0.5
    lightness = 0.5

    for hue in hue_values:
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        colors.append((r, g, b))

    return colors


def calculate_polygon(points, radius):
    center = np.zeros((2,))
    for point in points:
        center += np.array(point)
    center /= len(points)

    distances = []
    for point in points:
        distances.append((point, get_distance(center, point)))

    start_point = max(distances, key=lambda x: x[1])[0]
    polygon = [start_point]
    current_angle = get_angle(center, start_point)
    current_point = start_point

    while True:
        angles = []
        for point in points:
            if point == current_point:
                continue
            angle = get_angle(current_point, point)
            angles.append((point, angle))

        angles = map(lambda x: (x[0], x[1] % 360), angles)
        current_point, current_angle = min(angles, key=lambda x: (x[1] - current_angle) % 360)
        polygon.append(current_point)

        if current_point == start_point:
            break

    rounded_polygon = []

    for i in range(len(polygon) - 1):
        current_point = np.array(polygon[i])
        next_point = np.array(polygon[i + 1])
        centerx, centery = tuple((current_point + next_point) / 2)
        length = math.hypot(*(current_point - next_point))
        angle = math.atan2(current_point[1] - next_point[1], current_point[0] - next_point[0])
        length2 = length / 2
        sin_ang, cos_ang = math.sin(angle), math.cos(angle)

        radius_sin_ang = radius * sin_ang
        radius_cos_ang = radius * cos_ang
        length2_sin_ang = length2 * sin_ang
        length2_cos_ang = length2 * cos_ang

        ul = (centerx + length2_cos_ang - radius_sin_ang,
              centery + radius_cos_ang + length2_sin_ang)
        ur = (centerx - length2_cos_ang - radius_sin_ang,
              centery + radius_cos_ang - length2_sin_ang)

        rounded_polygon.append(ul)
        rounded_polygon.append(ur)

    return tuple(rounded_polygon)


def get_angle(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return np.degrees(np.arctan2(dy, dx))


def get_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


# draw an anti-aliased line with thickness more than 1px
# reference: https://stackoverflow.com/a/30599392
def draw_thick_aaline(surface, pos1, pos2, color, width):
    pos1_array = np.array(pos1)
    pos2_array = np.array(pos2)
    centerx, centery = tuple((pos1_array + pos2_array) / 2)
    length = math.hypot(*(pos2_array - pos1_array))
    angle = math.atan2(pos1_array[1] - pos2_array[1], pos1_array[0] - pos2_array[0])
    width2, length2 = width / 2, length / 2
    sin_ang, cos_ang = math.sin(angle), math.cos(angle)

    width2_sin_ang = width2 * sin_ang
    width2_cos_ang = width2 * cos_ang
    length2_sin_ang = length2 * sin_ang
    length2_cos_ang = length2 * cos_ang

    ul = (centerx + length2_cos_ang - width2_sin_ang,
          centery + width2_cos_ang + length2_sin_ang)
    ur = (centerx - length2_cos_ang - width2_sin_ang,
          centery + width2_cos_ang - length2_sin_ang)
    bl = (centerx - length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang - length2_sin_ang)
    br = (centerx + length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang + length2_sin_ang)

    gfxdraw.aapolygon(surface, (ul, ur, bl, br), color)
    gfxdraw.filled_polygon(surface, (ul, ur, bl, br), color)


def add_pos(pos1, pos2):
    return pos1[0] + pos2[0], pos1[1] + pos2[1]


def sub_pos(pos1, pos2):
    return pos1[0] - pos2[0], pos1[1] - pos2[1]
