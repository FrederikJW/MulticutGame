import math
import threading
import random

import networkx as nx
import numpy
import pygame
from pygame import gfxdraw

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import constants
import utils
from colors import *
from solvers import multicut_ilp
from utils import draw_thick_aaline, draw_cut_thick_aaline, calculate_polygon, get_distance, generate_distinct_colors, \
    line_line_intersect


class GraphFactory:
    @staticmethod
    def generate_grid(size_factor, size, seed=None):
        # get weights
        num_edges = 2 * size[0] * size[1] - size[0] - size[1]
        weights = GraphFactory.get_weights(num_edges, seed)

        # generate vertices
        graph = Graph(size_factor, *(0, 0), *constants.GAME_MODE_BODY_SIZE)
        i = 0
        for y in range(size[1]):
            for x in range(size[0]):
                graph.add_vertex(
                    Vertex(size_factor, i, (
                    (x * constants.GRAPH_VERTEX_DISTANCE_GRID + constants.GRAPH_RELATIVE_OFFSET[0]) * size_factor,
                    (y * constants.GRAPH_VERTEX_DISTANCE_GRID + constants.GRAPH_RELATIVE_OFFSET[1]) * size_factor)))
                i += 1

        # generate edges
        i = 0
        j = 0
        for y in range(size[1]):
            for x in range(size[0]):
                if x != size[0] - 1:
                    graph.add_edge(i, i + 1, weights[j])
                    j += 1
                if y != size[1] - 1:
                    graph.add_edge(i, i + size[0], weights[j])
                    j += 1
                i += 1

        # calculating optimal solution is done in a new thread so the game can continue
        my_thread = threading.Thread(target=graph.calculate_solution)
        my_thread.start()
        return graph

    @staticmethod
    def generate_complete_graph(size_factor, size, seed=None):
        # get weights
        num_edges = size * (size - 1) // 2
        weights = GraphFactory.get_weights(num_edges, seed)

        graph = Graph(size_factor, *(0, 0), *constants.GAME_MODE_BODY_SIZE)

        angle_distance = 360 / size
        radius = constants.GRAPH_PENTAGRAM_RADIUS
        center = ((constants.GRAPH_RELATIVE_OFFSET[0] + radius) * size_factor,
                  (constants.GRAPH_RELATIVE_OFFSET[1] + radius) * size_factor)

        k = 0
        for i in range(size):
            x = radius * (math.sin(math.pi * 2 * (angle_distance * i) / 360)) + center[0]
            y = -(radius * (math.cos(math.pi * 2 * (angle_distance * i) / 360))) + center[1]
            graph.add_vertex(Vertex(size_factor, i, (x, y)))
            for j in range(i):
                graph.add_edge(i, j, weights[k])
                k += 1

        # calculating optimal solution is done in a new thread so the game can continue
        my_thread = threading.Thread(target=graph.calculate_solution)
        my_thread.start()
        return graph

    @staticmethod
    def get_weights(num_edges, seed=None):
        weights = []
        if seed is None:
            for i in range(num_edges):
                weights.append(random.choice([-1, 1]))
        else:
            seed = str(bin(seed))[3:]
            for value in seed:
                weights.append(int(value) if int(value) == 1 else -1)

        return weights


class Graph:
    def __init__(self, size_factor, x, y, width, height):
        self.size_factor = size_factor
        self.groups = []
        self.vertices = {}
        self.edges = []

        self.surface = pygame.Surface((width, height))
        self.surface.set_colorkey(COLOR_KEY)
        self.rec = pygame.Rect(x, y, width, height)
        self.optimal_score = None
        self.optimal_edge_set = None
        self.optimal_groups = None
        self.vertices_color = None

        self.draw()

    def print_cut_edges_as_seed(self):
        seed = ''
        for edge in self.edges:
            seed += '0' if edge.is_cut() else '1'
        seed = int('1' + seed, 2)
        print(seed)
        return seed

    def get_collided_vertex(self, vertex1):
        radius = constants.GRAPH_GROUP_RADIUS * 2 * self.size_factor
        for vertex2 in self.vertices.values():
            if vertex2 == vertex1:
                continue
            if utils.get_distance(vertex1.pos, vertex2.pos) < radius:
                return vertex2
        return None

    def get_groups_by_cut(self, multicut):
        groups = []
        for vertex in self.vertices.values():
            vertex_was_added = False
            for vertex_list_group in groups:
                if vertex in vertex_list_group:
                    vertex_was_added = True
                    break

            if vertex_was_added:
                continue
            groups.append(self.get_group_by_cut(vertex, multicut))
        return groups

    def get_group_by_cut(self, vertex, multicut):
        vertices = [vertex]
        i = 0
        while i < len(vertices):
            vertices.extend([v for v in self.get_connected_vertices(vertices[i], multicut) if v not in vertices])
            i += 1
        return vertices

    def get_connected_vertices(self, vertex, multicut):
        connected_vertices = []
        for edge in self.edges:
            if edge.tuple in multicut:
                continue
            if edge.vertex1 == vertex:
                connected_vertices.append(edge.vertex2)
            if edge.vertex2 == vertex:
                connected_vertices.append(edge.vertex1)
        return connected_vertices

    def group_overlap(self, group1):
        for group2 in self.groups:
            if group1 == group2:
                continue
            for vertex1 in group1.vertices.values():
                for vertex2 in group2.vertices.values():
                    if utils.get_distance(vertex1.pos, vertex2.pos) < 2 * constants.GRAPH_GROUP_RADIUS:
                        return group2
        return None

    def merge_groups(self, group1, group2):
        for vertex in list(group1.vertices.values()):
            self.move_vertex_to_group(vertex, group2)

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

    def reset_to_one_group(self):
        group = Group(self.size_factor, list(self.vertices.values())[0])
        self.groups = [group]
        for vertex in self.vertices.values():
            group.add_vertex(vertex)
            vertex.group = group

        group.init_pos = self.rec.center
        group.pos = self.rec.center
        group.calculate_pos()

    def cut(self, edge_set):
        edge_set = [e for e in edge_set if not e.is_cut()]
        cut_edges = [e for e in self.edges if e.is_cut()]
        cut_edges.extend(edge_set)
        cut_edges_tuples = [edge.tuple for edge in cut_edges]
        # validate cut
        if len(edge_set) == 0:
            return False
        for edge in edge_set:
            if edge.vertex1 in self.get_group_by_cut(edge.vertex2, cut_edges_tuples):
                return False

        # make cut
        groups = self.get_groups_by_cut(cut_edges_tuples)

        relevant_vertices = set([vertex for edge in edge_set for vertex in (edge.vertex1, edge.vertex2)])
        old_group_center_pos_by_vertex = dict([(vertex.id, vertex.group.get_center()) for vertex in relevant_vertices])
        old_group_center_pos_by_group = {}
        old_group_total_nodes_by_vertex = dict(
            [(vertex.id, len(vertex.group.vertices)) for vertex in relevant_vertices])
        old_group_total_nodes_by_group = {}

        for vertex in relevant_vertices:
            for group in groups:
                if vertex not in group:
                    continue
                old_group = vertex.group
                new_group = Group(self.size_factor, vertex)
                self.groups.append(new_group)
                if old_group in self.groups:
                    self.groups.remove(old_group)
                for group_vertex in group:
                    new_group.add_vertex(group_vertex)
                    group_vertex.group = new_group
                old_group_center_pos_by_group[new_group] = old_group_center_pos_by_vertex[vertex.id]
                old_group_total_nodes_by_group[new_group] = old_group_total_nodes_by_vertex[vertex.id]
                groups.remove(group)

        for group, old_center in old_group_center_pos_by_group.items():
            old_total_nodes = old_group_total_nodes_by_group[group]
            update_vector = utils.calculate_update_vector(
                group.get_center(), old_center, old_total_nodes, len(group.vertices) / old_total_nodes)
            update_vector = (update_vector[0] * self.size_factor, update_vector[1] * self.size_factor)
            group.move(utils.add_pos(group.pos, update_vector))

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
            group = Group(self.size_factor, vertex)
            self.groups.append(group)

        vertex.group = group
        group.add_vertex(vertex)
        group.calculate_pos()

    def calculate_solution(self):
        self.optimal_edge_set, self.optimal_score = multicut_ilp(self.get_nx_graph())

        optimal_groups = self.get_groups_by_cut(self.optimal_edge_set)

        self.vertices_color = {}
        colors = set(generate_distinct_colors(len(optimal_groups)))
        self.optimal_groups = zip(colors, optimal_groups)
        for color, group in self.optimal_groups:
            for vertex in group:
                self.vertices_color[vertex.id] = color

    def get_score(self):
        score = 0
        for edge in self.edges:
            if edge.vertex1.group != edge.vertex2.group:
                score += edge.weight
        return score

    def get_intersected_edges(self, point1, point2):
        intersected_edges = []
        for edge in self.edges:
            if edge.intersects(point1, point2):
                intersected_edges.append(edge)
        return intersected_edges

    def is_solved(self):
        return self.optimal_score is not None and self.optimal_score == self.get_score()

    def draw(self, highlight_group=None, show_solution=False):
        self.surface.fill(COLOR_KEY)

        # draw groups
        for group in self.groups:
            group.draw(self.surface, group == highlight_group)

        # draw edges
        for edge in self.edges:
            edge.draw(self.surface)

        # draw vertices
        for vertex in self.vertices.values():
            color = self.vertices_color[vertex.id] if self.optimal_score is not None and show_solution else DARK_BLUE
            vertex.draw(self.surface, color)

    def objects(self):
        return self.surface, self.rec


class Group:
    def __init__(self, size_factor, vertex):
        self.size_factor = size_factor
        self.vertices = {}
        self.init_pos = vertex.init_pos
        self.pos = vertex.pos
        self.rel_pos = {}
        self.polygon = None
        self.radius = round(constants.GRAPH_GROUP_RADIUS * self.size_factor)

    def get_center(self):
        center_x = sum([vertex.pos[0] for vertex in self.vertices.values()]) / len(self.vertices)
        center_y = sum([vertex.pos[1] for vertex in self.vertices.values()]) / len(self.vertices)
        return center_x, center_y

    def add_vertex(self, vertex):
        if vertex.id not in self.vertices.keys():
            self.vertices[vertex.id] = vertex

    def remove_vertex(self, vertex):
        self.vertices.pop(vertex.id)

    def is_hit(self, pos):
        if self.polygon is not None:
            polygon = Polygon(self.polygon)
            if polygon.contains(Point(*pos)):
                return True

        for vertex in self.vertices.values():
            if vertex.is_hit(pos, True):
                return True
        return False

    def move(self, pos):
        self.pos = pos
        self.calculate_pos()

    def calculate_pos(self):
        while not self._calculate_pos():
            pass

    def _calculate_pos(self):
        self.rel_pos = {}

        for vertex in self.vertices.values():
            rel_pos = (numpy.array(vertex.init_pos) - self.init_pos) / 2
            self.rel_pos[vertex] = rel_pos
            total_pos = [round(n) for n in (numpy.array(self.pos) + self.rel_pos[vertex])]

            vertex_out_of_bounds = False
            left_bound = constants.GAME_MODE_BODY_MARGIN
            right_bound = constants.GAME_MODE_BODY_SIZE[0] - constants.GAME_MODE_BODY_MARGIN
            top_bound = constants.GAME_MODE_BODY_MARGIN
            bottom_bound = constants.GAME_MODE_BODY_SIZE[1] - constants.GAME_MODE_BODY_MARGIN
            pos_update = list(self.pos)
            if left_bound > total_pos[0]:
                pos_update[0] = self.pos[0] + left_bound - total_pos[0]
                vertex_out_of_bounds = True
            if right_bound < total_pos[0]:
                pos_update[0] = self.pos[0] + right_bound - total_pos[0]
                vertex_out_of_bounds = True
            if top_bound > total_pos[1]:
                pos_update[1] = self.pos[1] + top_bound - total_pos[1]
                vertex_out_of_bounds = True
            if bottom_bound < total_pos[1]:
                pos_update[1] = self.pos[1] + bottom_bound - total_pos[1]
                vertex_out_of_bounds = True

            total_pos = tuple(total_pos)

            vertex.move(total_pos)
            if vertex_out_of_bounds:
                self.pos = tuple(pos_update)
                return False
        return True

    def draw(self, surface, highlight):
        size_increase = 0
        if highlight:
            size_increase = 5
        radius = round(self.radius + (size_increase * self.size_factor))

        for vertex in self.vertices.values():
            gfxdraw.filled_circle(surface, *vertex.pos, radius, LIGHT_BLUE)
            gfxdraw.aacircle(surface, *vertex.pos, radius, LIGHT_BLUE)

        if len(self.vertices) > 1:
            self.polygon = calculate_polygon([vertex.pos for vertex in self.vertices.values()], radius)

            gfxdraw.filled_polygon(surface, self.polygon, LIGHT_BLUE)
            gfxdraw.aapolygon(surface, self.polygon, LIGHT_BLUE)
        else:
            self.polygon = None


class Vertex:
    def __init__(self, size_factor, id, pos):
        self.size_factor = size_factor
        self.pos = (round(pos[0]), round(pos[1]))
        self.init_pos = self.pos
        self.radius = round(constants.GRAPH_VERTEX_RADIUS * self.size_factor)
        self.id = id
        self.edges = {}
        self.group = Group(self.size_factor, self)
        self.group.add_vertex(self)

    def reset(self):
        self.pos = self.init_pos
        self.group = Group(self.size_factor, self)
        self.group.add_vertex(self)

    @property
    def rec(self):
        rec = pygame.Rect((0, 0), (2 * self.radius, 2 * self.radius))
        rec.center = self.pos
        return rec

    def is_hit(self, pos, use_group_radius=False):
        radius = self.radius
        if use_group_radius:
            radius = self.group.radius
        return utils.get_distance(self.pos, pos) < radius

    def draw(self, surface, color):
        gfxdraw.aacircle(surface, *self.pos, self.radius, color)
        gfxdraw.filled_circle(surface, *self.pos, self.radius, color)

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
        if self.vertex1.group != self.vertex2.group:
            draw_cut_thick_aaline(surface, self.vertex1.pos, self.vertex2.pos, GREEN if self.weight == 1 else RED, 3)
        else:
            draw_thick_aaline(surface, self.vertex1.pos, self.vertex2.pos, GREEN if self.weight == 1 else RED, 3)

    def intersects(self, point1, point2):
        return line_line_intersect(point1, point2, self.vertex1.pos, self.vertex2.pos) is not None

    def is_cut(self):
        return self.vertex1.group != self.vertex2.group

    @property
    def tuple(self):
        return self.vertex1.id, self.vertex2.id
