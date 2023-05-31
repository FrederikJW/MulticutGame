import math
import threading
import random

import networkx as nx
import numpy
import pygame
from pygame import gfxdraw

import constants
from colors import *
from solvers import multicut_ilp
from utils import draw_thick_aaline


class GraphFactory:
    @staticmethod
    def generate_grid(size):
        graph = Graph(*(0, 0), *constants.GAME_MODE_BODY_SIZE)
        i = 0
        for y in range(size[1]):
            for x in range(size[0]):
                graph.add_vertex(
                    Vertex(i, (x * constants.GRAPH_VERTEX_DISTANCE_GRID + constants.GRAPH_RELATIVE_OFFSET[0],
                               y * constants.GRAPH_VERTEX_DISTANCE_GRID + constants.GRAPH_RELATIVE_OFFSET[1])))
                i += 1
        i = 0
        for y in range(size[1]):
            for x in range(size[0]):
                if x != size[0] - 1:
                    graph.add_edge(i, i + 1, random.choice([-1, 1]))
                if y != size[1] - 1:
                    graph.add_edge(i, i + size[0], random.choice([-1, 1]))
                i += 1

        # calculating optimal solution is done in a new thread so the game can continue
        my_thread = threading.Thread(target=graph.calculate_solution)
        my_thread.start()
        return graph

    @staticmethod
    def generate_pentagram():
        graph = Graph(*(0, 0), *constants.GAME_MODE_BODY_SIZE)

        angle_distance = 360/5
        radius = constants.GRAPH_PENTAGRAM_RADIUS
        center = (constants.GRAPH_RELATIVE_OFFSET[0] + radius,
                  constants.GRAPH_RELATIVE_OFFSET[1] + radius)

        for i in range(5):
            x = radius * (math.sin(math.pi * 2 * (angle_distance * i) / 360)) + center[0]
            y = -(radius * (math.cos(math.pi * 2 * (angle_distance * i) / 360))) + center[1]
            graph.add_vertex(Vertex(i, (x, y)))
            for j in range(i):
                graph.add_edge(i, j, random.choice([-1, 1]))

        # calculating optimal solution is done in a new thread so the game can continue
        my_thread = threading.Thread(target=graph.calculate_solution)
        my_thread.start()
        return graph


class Graph:
    def __init__(self, x, y, width, height):
        self.groups = []
        self.vertices = {}
        self.edges = []

        self.surface = pygame.Surface((width, height))
        self.surface.set_colorkey(COLOR_KEY)
        self.rec = pygame.Rect(x, y, width, height)
        self.optimal_score = None
        self.optimal_edge_set = None

        self.draw()

    def get_nx_graph(self):
        graph = nx.Graph()
        graph.add_nodes_from([v.id for v in self.vertices.values()])
        graph.add_edges_from([(e.vertex1.id, e.vertex2.id, {'weight': e.weight}) for e in self.edges])
        return graph

    def reset(self):
        self.groups = []
        for vertex in self.vertices.values():
            vertex.reset()
            self.groups.append(vertex.group)

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
        else:
            group_old.calculate_pos()

        if group is None:
            group = Group(vertex.pos)
            self.groups.append(group)

        vertex.group = group
        group.add_vertex(vertex)
        group.calculate_pos()

    def calculate_solution(self):
        self.optimal_edge_set, self.optimal_score = multicut_ilp(self.get_nx_graph())

    def get_score(self):
        score = 0
        for edge in self.edges:
            if edge.vertex1.group != edge.vertex2.group:
                score += edge.weight
        return score

    def is_solved(self):
        return self.optimal_score is not None and self.optimal_score == self.get_score()

    def draw(self, highlight_group=None):
        self.surface.fill(COLOR_KEY)

        # draw groups
        for group in self.groups:
            group.draw(self.surface, group == highlight_group)

        # draw edges
        for edge in self.edges:
            edge.draw(self.surface)

        # draw vertices
        for vertex in self.vertices.values():
            vertex.draw(self.surface)

    def objects(self):
        return self.surface, self.rec


class Group:
    def __init__(self, pos):
        self.vertices = {}
        self.pos = (round(pos[0]), round(pos[1]))
        self.radius = constants.GRAPH_GROUP_RADIUS
        self.rel_pos = {}

    @property
    def rec(self):
        rec = pygame.Rect((0, 0), (2 * self.radius, 2 * self.radius))
        rec.center = self.pos
        return rec

    def add_vertex(self, vertex):
        self.vertices[vertex.id] = vertex

    def remove_vertex(self, vertex):
        self.vertices.pop(vertex.id)

    def calculate_pos(self):
        if len(self.vertices) == 1:
            self.radius = constants.GRAPH_GROUP_RADIUS
            list(self.vertices.values())[0].move(self.pos)
            return

        max_distance = 0
        self.rel_pos = {}

        center = numpy.zeros((2,))
        for vertex in self.vertices.values():
            center += numpy.array(vertex.init_pos)
        center /= len(self.vertices)

        for vertex in self.vertices.values():
            rel_pos = (numpy.array(vertex.init_pos) - center) / 2
            distance = numpy.linalg.norm(rel_pos)
            max_distance = distance if distance > max_distance else max_distance
            self.rel_pos[vertex] = rel_pos
            total_pos = tuple(round(n) for n in (numpy.array(self.pos) + self.rel_pos[vertex]))
            vertex.move(total_pos)

        self.radius = max_distance + constants.GRAPH_GROUP_OVERSIZE

    def draw(self, surface, highlight):
        size_increase = 0
        if highlight:
            size_increase = 5
        radius = round(self.radius + size_increase)
        gfxdraw.aacircle(surface, *self.pos, radius, DARK_BLUE)
        gfxdraw.aacircle(surface, *self.pos, radius - 1, LIGHT_BLUE)
        gfxdraw.filled_circle(surface, *self.pos, radius - 1, LIGHT_BLUE)


class Vertex:
    def __init__(self, id, pos):
        self.pos = (round(pos[0]), round(pos[1]))
        self.init_pos = self.pos
        self.radius = constants.GRAPH_VERTEX_RADIUS
        self.id = id
        self.edges = {}
        self.group = Group(self.pos)
        self.group.add_vertex(self)

    def reset(self):
        self.pos = self.init_pos
        self.group = Group(self.pos)
        self.group.add_vertex(self)

    @property
    def rec(self):
        rec = pygame.Rect((0, 0), (2 * self.radius, 2 * self.radius))
        rec.center = self.pos
        return rec

    def draw(self, surface):
        gfxdraw.aacircle(surface, *self.pos, self.radius, DARK_BLUE)
        gfxdraw.filled_circle(surface, *self.pos, self.radius, DARK_BLUE)

    def add_edge(self, vertex_id, edge):
        self.edges[vertex_id] = edge

    def get_edges(self):
        return self.edges.values()

    def get_weight(self, vertex_id):
        return self.edges[vertex_id].weight

    def move(self, pos):
        pos = (round(pos[0]), round(pos[1]))
        self.pos = pos
        if len(self.group.vertices) == 1:
            self.group.pos = pos


class Edge:
    def __init__(self, vertex1, vertex2, weight):
        self.weight = weight
        self.vertex1 = vertex1
        self.vertex2 = vertex2

    def draw(self, surface):
        draw_thick_aaline(surface, self.vertex1.pos, self.vertex2.pos, GREEN if self.weight == 1 else RED, 3)
