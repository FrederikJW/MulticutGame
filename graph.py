import pygame

from pygame import gfxdraw

from colors import *


class Graph:
    def __init__(self, x, y, width, height):
        self.vertices = dict()

        self.surface = pygame.Surface((width, height))
        self.surface.fill(COLOR_KEY)
        self.surface.set_colorkey(COLOR_KEY)
        self.rec = pygame.Rect(x, y, width, height)

        self.draw()

    def add_vertex(self, vertex):
        self.vertices[vertex.id] = vertex
        self.draw()

    def add_edge(self, vertex1_id, vertex2_id, weight=-1):
        self.vertices[vertex1_id].add_edge(vertex2_id, weight)
        self.vertices[vertex2_id].add_edge(vertex1_id, weight)
        self.draw()

    def get_vertex(self, vertex_id):
        if vertex_id in self.vertices.keys():
            return self.vertices[vertex_id]
        return None

    def draw(self):
        # draw edges
        for vertex in self.vertices.values():
            for vertex2_id, weight in vertex.edges.items():
                gfxdraw.line(self.surface, *vertex.pos, *self.get_vertex(vertex2_id).pos, GREEN)

        # draw vertices
        for vertex in self.vertices.values():
            gfxdraw.aacircle(self.surface, *vertex.pos, 20, DARK_BLUE)
            gfxdraw.aacircle(self.surface, *vertex.pos, 19, LIGHT_BLUE)
            gfxdraw.filled_circle(self.surface, *vertex.pos, 19, LIGHT_BLUE)
            gfxdraw.aacircle(self.surface, *vertex.pos, 10, DARK_BLUE)
            gfxdraw.filled_circle(self.surface, *vertex.pos, 10, DARK_BLUE)

    def objects(self):
        return self.surface, self.rec


class Vertex:
    def __init__(self, id, pos):
        self.pos = pos
        self.id = id
        self.edges = {}

    def add_edge(self, vertex_id, weight=-1):
        self.edges[vertex_id] = weight

    def get_edges(self):
        self.edges.keys()

    def get_weight(self, vertex_id):
        return self.edges[vertex_id]
