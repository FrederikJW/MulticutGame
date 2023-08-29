import colorsys
import math

import numpy as np
import pygame
from pygame import gfxdraw
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

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
    base_movement = 0
    total_nodes_factor = 1
    relative_nodes = -math.tan((relative_nodes + 1) * math.pi / 2)
    relative_nodes_factor = 3
    normalized_vector = normalize_vector(sub_pos(center_new, center_old))
    if center_new == center_old:
        normalized_vector = (0, 0)
    val_x = (total_nodes * total_nodes_factor + base_movement + relative_nodes * relative_nodes_factor) * \
            normalized_vector[0]
    val_y = (total_nodes * total_nodes_factor + base_movement + relative_nodes * relative_nodes_factor) * \
            normalized_vector[1]

    return val_x, val_y


def calculate_polygon(points, edges, radius, ignore_edges=False):
    center = np.zeros((2,))
    for point_pos in points.values():
        center += np.array(point_pos)
    center /= len(points)

    distances = []
    for point_id, point_pos in points.items():
        distances.append((point_id, get_distance(center, point_pos)))

    start_point = max(distances, key=lambda x: x[1])[0]
    polygon = [start_point]
    current_angle = get_angle(center, points[start_point]) % 360
    current_point = start_point
    prev_point = None

    while True:
        angles = []
        for point_id, point_pos in points.items():
            if point_id == current_point or point_id == prev_point:
                continue

            if not ignore_edges and (current_point, point_id) not in edges and (point_id, current_point) not in edges:
                continue

            current_point_pos = points[current_point]
            angle = get_angle(current_point_pos, point_pos)
            angles.append((point_id, angle))

        if len(angles) == 0:
            # in this case there is only the path back to the previous vertex
            current_point, prev_point = prev_point, current_point
            polygon.append(current_point)
            current_angle = (current_angle - 180) % 360
        else:
            # calculate angle mod 360
            angles = map(lambda x: (x[0], x[1] % 360), angles)

            prev_point = current_point
            current_point, current_angle = min(angles, key=lambda x: (x[1] - current_angle) % 360 if (x[1] - current_angle) % 360 != 0 else 360)
            current_angle = (current_angle - 180) % 360
            polygon.append(current_point)

        if current_point == start_point:
            polygon_points = [points[vertex_id] for vertex_id in polygon]
            polygon_obj = Polygon(polygon_points)
            finished = True
            for point in points.values():
                if not (polygon_obj.contains(Point(*point)) or point in polygon_points):
                    finished = False
                    break
            if finished:
                break
            else:
                continue

    rounded_polygon = []

    for i in range(len(polygon) - 1):
        current_point = np.array(points[polygon[i]])
        next_point = np.array(points[polygon[i + 1]])
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

    i = 0
    while i <= len(rounded_polygon) - 4:
        intersection = line_line_intersect(rounded_polygon[i], rounded_polygon[i+1], rounded_polygon[i+2], rounded_polygon[i+3])
        if intersection is not None:
            rounded_polygon.pop(i+1)
            rounded_polygon.pop(i+1)
            rounded_polygon.insert(i+1, round_pos(intersection))
            continue
        i += 1

    return tuple(rounded_polygon)


def ndarray_to_surface(ndarray):
    height, width, _ = ndarray.shape
    surface = pygame.surfarray.make_surface(ndarray.swapaxes(0, 1))
    return surface


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


def mult_pos(pos1, pos2):
    return pos1[0] * pos2[0], pos1[1] * pos2[1]


def div_pos(pos1, pos2):
    return pos1[0] / pos2[0], pos1[1] / pos2[1]


def round_pos(pos):
    return round(pos[0]), round(pos[1])


def normalize_vector(vector):
    magnitude = np.linalg.norm(np.array(vector))
    normalized_vector = vector / magnitude
    return tuple(normalized_vector)


# found here: https://stackoverflow.com/a/63523520
def line_line_intersect(P0, P1, Q0, Q1):
    d = (P1[0] - P0[0]) * (Q1[1] - Q0[1]) + (P1[1] - P0[1]) * (Q0[0] - Q1[0])
    if d == 0:
        return None
    t = ((Q0[0] - P0[0]) * (Q1[1] - Q0[1]) + (Q0[1] - P0[1]) * (Q0[0] - Q1[0])) / d
    u = ((Q0[0] - P0[0]) * (P1[1] - P0[1]) + (Q0[1] - P0[1]) * (P0[0] - P1[0])) / d
    if 0 <= t <= 1 and 0 <= u <= 1:
        return round(P1[0] * t + P0[0] * (1 - t)), round(P1[1] * t + P0[1] * (1 - t))
    return None


# found here: https://stackoverflow.com/a/42015712
def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.
