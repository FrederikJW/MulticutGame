import pulp


async def multicut_ilp(graph):
    # Define the ILP model which is a minimum multicut problem
    model = pulp.LpProblem("Multicut", pulp.LpMinimize)

    # Generate symmetric edges
    edges = list(graph.edges)
    edges += [(v, u) for (u, v) in graph.edges]

    # Create a binary variable for each edge where
    # x(u, v) = 0 means the edge between u and v is not cut
    # x(u, v) = 1 means the edge between u and v is cut
    x = pulp.LpVariable.dicts("x", edges, lowBound=0, upBound=1, cat=pulp.LpInteger)

    # Generate symmetric and non-symmetric vertex pairs
    all_vertex_perm = [pair for pair in pulp.allpermutations(graph.nodes, 2) if len(pair) == 2]
    all_vertex_comb = [pair for pair in pulp.allcombinations(graph.nodes, 2) if len(pair) == 2]

    # Create a binary variable for each vertex pair where
    # path(u, v) = 0 means there is a path from u to v
    # path(u, v) = 1 means there is no path from u to v
    path = pulp.LpVariable.dicts("path", all_vertex_perm, lowBound=0, upBound=1, cat=pulp.LpInteger)

    # Create a PuLP model
    model += pulp.lpSum([graph[u][v]['weight'] * x[(u, v)] for (u, v) in graph.edges])

    # Add the constraints
    for (u, v) in graph.edges:
        # if the edge from u to v is cut then the edge from v to u is also cut
        model += x[(u, v)] - x[(v, u)] == 0

        # if cut then there is no path, if not cut then there is a path
        model += path[(u, v)] + x[(u, v)] == 1

    for (u, v) in all_vertex_comb:
        # if there is a path from u to v, then there is a path from v to u
        model += path[(u, v)] - path[(v, u)] == 0

        for (w, l) in edges:
            if w == u and l != v:
                # if there is an uncut edge u to l and a path l to v, there must be a path u to v
                # if there is an uncut edge u to l but no path l to v, there can't be a path u to v
                # if there is a cut edge u to l but a path l to v, there can't be a path u to v
                # NOTE: if there is a cut edge u to l and no path l to v, there can be a path from u to v but doesn't
                # have to, both is possible
                # DNF: (PATH(u, v) ∧ UNCUT(u, l) ∧ PATH(l, v)) ∨ (¬PATH(u, v) ∧ ¬UNCUT(u, l))
                # ∨ (¬PATH(u, v) ∧ ¬PATH(l, v)) ∨ (¬UNCUT(u, l) ∧ ¬PATH(l, v))
                # CNF: (¬PATH(u, v) ∨ ¬UNCUT(u, l) ∨ PATH(l, v)) ∧ (¬PATH(u, v) ∨ UNCUT(u, l) ∨ ¬PATH(l, v))
                # ∧ (PATH(u, v) ∨ ¬UNCUT(u, l) ∨ ¬PATH(l, v))
                model += 1 - path[(u, v)] + x[(u, l)] + path[(l, v)] >= 1
                model += 1 - path[(u, v)] + 1 - x[(u, l)] + 1 - path[(l, v)] >= 1
                model += path[(u, v)] + x[(u, l)] + 1 - path[(l, v)] >= 1

    # Solve the problem
    model.solve()

    # Print the results for debugging
    print("Status: ", pulp.LpStatus[model.status])
    print("Optimal value: ", pulp.value(model.objective))
    for e in graph.edges:
        print("Edge ({},{}): {}".format(e[0], e[1], pulp.value(x[e])))

    # Extract the optimal solution and return
    opt_cut = []
    for (u, v) in graph.edges():
        if x[(u, v)].varValue == 1:
            opt_cut.append((u, v))
    return opt_cut, pulp.value(model.objective)
