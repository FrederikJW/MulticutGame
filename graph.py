import numpy
import pygame

from pygame import gfxdraw

from colors import *
from utils import draw_thick_aaline


class Graph:
    def __init__(self, x, y, width, height):
        self.groups = []
        self.vertices = {}
        self.edges = []

        self.surface = pygame.Surface((width, height))
        self.surface.set_colorkey(COLOR_KEY)
        self.rec = pygame.Rect(x, y, width, height)

        self.draw()

    def add_vertex(self, vertex):
        self.vertices[vertex.id] = vertex
        self.groups.append(vertex.group)
        self.draw()

    def add_edge(self, vertex1_id, vertex2_id, weight=-1):
        vertex1 = self.vertices[vertex1_id]
        vertex2 = self.vertices[vertex2_id]
        edge = Edge(vertex1, vertex2, weight)
        self.edges.append(edge)
        vertex1.add_edge(vertex2_id, edge)
        vertex2.add_edge(vertex1_id, edge)
        self.draw()

    def get_vertex(self, vertex_id):
        if vertex_id in self.vertices.keys():
            return self.vertices[vertex_id]
        return None

    def move_vertex_to_group(self, vertex, group):
        group_old = vertex.group
        group_old.remove_vertex(vertex)
        if len(group_old.vertices) == 0:
            self.groups.remove(group_old)
        vertex.group = group
        group.add_vertex(vertex)

    def draw(self, highlight_group=None):
        self.surface.fill(COLOR_KEY)

        # draw edges
        for edge in self.edges:
            draw_thick_aaline(self.surface, edge.vertex1.pos, edge.vertex2.pos, RED if edge.weight == 1 else GREEN, 2)

        # draw vertices
        for group in self.groups:
            size_increase = 0
            if group == highlight_group:
                size_increase = 5
            if len(group.vertices) == 1:
                radius = int((group.rec.width/2) + size_increase)
                gfxdraw.aacircle(self.surface, *group.pos, radius, DARK_BLUE)
                gfxdraw.aacircle(self.surface, *group.pos, radius - 1, LIGHT_BLUE)
                gfxdraw.filled_circle(self.surface, *group.pos, radius - 1, LIGHT_BLUE)

                vertex = list(group.vertices.values())[0]
                gfxdraw.aacircle(self.surface, *vertex.pos, 10, DARK_BLUE)
                gfxdraw.filled_circle(self.surface, *vertex.pos, 10, DARK_BLUE)
            elif len(group.vertices) > 1:
                group.draw_mini_graph(self.surface, size_increase)

    def objects(self):
        return self.surface, self.rec


class Group:
    def __init__(self, pos):
        self.vertices = {}
        self.pos = pos
        self.rec = pygame.Rect((0, 0), (40, 40))
        self.rec.center = pos

    def add_vertex(self, vertex):
        self.vertices[vertex.id] = vertex

    def remove_vertex(self, vertex):
        self.vertices.pop(vertex.id)

    def draw_mini_graph(self, surface, size_increase):
        rel_pos = {}

        center = numpy.zeros((1, 2))
        for vertex in self.vertices.values():
            center += numpy.array(vertex.init_pos)
        center /= len(self.vertices)
        for vertex in self.vertices.values():
            rel_pos[vertex] = (numpy.array(vertex.init_pos) - center) / 5  # smaller by a factor of 6

        radius = int((self.rec.width / 2) + size_increase)
        gfxdraw.aacircle(surface, *self.pos, radius, DARK_BLUE)
        gfxdraw.aacircle(surface, *self.pos, radius - 1, LIGHT_BLUE)
        gfxdraw.filled_circle(surface, *self.pos, radius - 1, LIGHT_BLUE)

        for vertex in self.vertices.values():
            pos = tuple(round(n) for n in (numpy.array(self.pos) + rel_pos[vertex])[0])
            gfxdraw.aacircle(surface, *pos, 5, DARK_BLUE)
            gfxdraw.filled_circle(surface, *pos, 5, DARK_BLUE)

    def move(self, pos):
        self.pos = pos
        self.rec.center = pos


class Vertex:
    def __init__(self, id, pos):
        self.pos = pos
        self.init_pos = pos
        self.rec = pygame.Rect((0, 0), (20, 20))
        self.rec.center = self.pos
        self.id = id
        self.edges = {}
        self.group = Group(pos)
        self.group.add_vertex(self)

    def add_edge(self, vertex_id, edge):
        self.edges[vertex_id] = edge

    def get_edges(self):
        return self.edges.values()

    def get_weight(self, vertex_id):
        return self.edges[vertex_id].weight

    def move(self, pos):
        self.pos = pos
        self.rec.center = pos
        if len(self.group.vertices) == 1:
            self.group.move(pos)


class Edge:
    def __init__(self, vertex1, vertex2, weight):
        self.weight = weight
        self.vertex1 = vertex1
        self.vertex2 = vertex2
