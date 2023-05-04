import math

import numpy
from pygame import gfxdraw


# draw an anti-aliased line with thickness more than 1px
# reference: https://stackoverflow.com/a/30599392
def draw_thick_aaline(surface, pos1, pos2, color, width):
    pos1_array = numpy.array(pos1)
    pos2_array = numpy.array(pos2)
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

    gfxdraw.aapolygon(surface, (ul, ur, bl, br), color)
    gfxdraw.filled_polygon(surface, (ul, ur, bl, br), color)
