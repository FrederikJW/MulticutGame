import math

import numpy as np
from pygame import gfxdraw

import colorsys

import constants


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


def calculate_update_vector(center_new, center_old, total_nodes, relative_nodes):
    base_movement = 2
    total_nodes_factor = 2
    relative_nodes = -math.tan((relative_nodes + 1) * math.pi / 2)
    relative_nodes_factor = 2
    normalized_vector = normalize_vector(sub_pos(center_new, center_old))
    if center_new == center_old:
        normalized_vector = (0, 0)
    val_x = (total_nodes * total_nodes_factor + base_movement + relative_nodes * relative_nodes_factor) * normalized_vector[0]
    val_y = (total_nodes * total_nodes_factor + base_movement + relative_nodes * relative_nodes_factor) * normalized_vector[1]

    return val_x, val_y


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
    bl = (centerx + length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang + length2_sin_ang)
    br = (centerx - length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang - length2_sin_ang)

    gfxdraw.aapolygon(surface, (ul, ur, br, bl), color)
    gfxdraw.filled_polygon(surface, (ul, ur, br, bl), color)


def draw_cut_thick_aaline(surface, pos1, pos2, color, width):
    pos1_array = np.array(pos1)
    pos2_array = np.array(pos2)
    centerx, centery = tuple((pos1_array + pos2_array) / 2)
    length = math.hypot(*(pos2_array - pos1_array))
    gap_length = constants.GRAPH_CUT_GAP
    angle = math.atan2(pos1_array[1] - pos2_array[1], pos1_array[0] - pos2_array[0])
    width2, length2, gap_length2 = width / 2, length / 2, gap_length / 2
    sin_ang, cos_ang = math.sin(angle), math.cos(angle)

    width2_sin_ang = width2 * sin_ang
    width2_cos_ang = width2 * cos_ang
    length2_sin_ang = length2 * sin_ang
    length2_cos_ang = length2 * cos_ang
    gap_length2_sin_ang = gap_length2 * sin_ang
    gap_length2_cos_ang = gap_length2 * cos_ang

    ul1 = (centerx + length2_cos_ang - width2_sin_ang,
          centery + width2_cos_ang + length2_sin_ang)
    ur1 = (centerx - length2_cos_ang - width2_sin_ang,
          centery + width2_cos_ang - length2_sin_ang)
    bl1 = (centerx + length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang + length2_sin_ang)
    br1 = (centerx - length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang - length2_sin_ang)

    ul2 = (centerx + gap_length2_cos_ang - width2_sin_ang,
          centery + width2_cos_ang + gap_length2_sin_ang)
    ur2 = (centerx - gap_length2_cos_ang - width2_sin_ang,
          centery + width2_cos_ang - gap_length2_sin_ang)
    bl2 = (centerx + gap_length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang + gap_length2_sin_ang)
    br2 = (centerx - gap_length2_cos_ang + width2_sin_ang,
          centery - width2_cos_ang - gap_length2_sin_ang)

    gfxdraw.aapolygon(surface, (ur1, br1, br2, ur2), color)
    gfxdraw.filled_polygon(surface, (ur1, br1, br2, ur2), color)
    gfxdraw.aapolygon(surface, (ul1, bl1, bl2, ul2), color)
    gfxdraw.filled_polygon(surface, (ul1, bl1, bl2, ul2), color)


def add_pos(pos1, pos2):
    return pos1[0] + pos2[0], pos1[1] + pos2[1]


def sub_pos(pos1, pos2):
    return pos1[0] - pos2[0], pos1[1] - pos2[1]


def normalize_vector(vector):
    magnitude = np.linalg.norm(np.array(vector))
    normalized_vector = vector / magnitude
    return tuple(normalized_vector)


# found here: https://stackoverflow.com/a/63523520
def line_line_intersect(P0, P1, Q0, Q1):
    d = (P1[0]-P0[0]) * (Q1[1]-Q0[1]) + (P1[1]-P0[1]) * (Q0[0]-Q1[0])
    if d == 0:
        return None
    t = ((Q0[0]-P0[0]) * (Q1[1]-Q0[1]) + (Q0[1]-P0[1]) * (Q0[0]-Q1[0])) / d
    u = ((Q0[0]-P0[0]) * (P1[1]-P0[1]) + (Q0[1]-P0[1]) * (P0[0]-P1[0])) / d
    if 0 <= t <= 1 and 0 <= u <= 1:
        return round(P1[0] * t + P0[0] * (1-t)), round(P1[1] * t + P0[1] * (1-t))
    return None

