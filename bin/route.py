class Node:

    def __init__(self, name):
        """node is supplied in the form: [A-Z][A-Z][0-9]."""
        self.name = name
        self.links = {}

    def __str__(self):
        return self.name

    @property
    def pretty(self):
        """Reeturn links in a readable format

        [{node1.name: distance}, {node2.name: distance}, etc.]
        """
        return {str(l): v for l, v in self.links.items()}

    def add_link(self, node, distance):
        """Add a link from this node to another node."""
        self.links[node] = distance


class Graph:

    def __init__(self):
        self.nodes = []

    def __getitem__(self, index):
        return [n for n in self.nodes if n.name == index][0]

    @property
    def pretty(self):
        """Return the nodes in a readable format.

        [node1.name, node2.name, etc.]
        """
        return [n.name for n in self.nodes]

    @property
    def total_graph_distance(self):
        return sum([sum(n.links.values()) for n in self.nodes])

    def get(self, node_name, default=None):
        try:
            return self[node_name]
        except IndexError:
            return default

    def add_nodes(self, *nodes):
        """Add a node to the graph."""
        for node in nodes:
            if node.name not in [n.name for n in self.nodes]:
                self.nodes.append(node)

    def distance_from_node1_to_node2(self, from_node, to_node):
        return from_node.links[to_node]

    def is_valid_path(self, *nodes):
        """Assert that the supplied node names are linked in the graph. Order
        of node names provided dertermines the traverse path.

        Args:
            node_names - list of node names to test. String

        Returns:
            True - The path provided exists in the graph
            False - The path provided does not exist in the graph
        """
        for i, node in enumerate(nodes[:-1]):
            next_node = nodes[i+1]
            if next_node not in node.links:
                return False
        return True

    def _stuck(self, path):
        """Determine whether a path generation is stuck in an infinite loop.

        We consider that the following sequence indicates that we have
        entered an infinite loop.
            1. [C, A]
            2. [C, A, B]
            3. [C, A, B, A]
            4. [C, A, B, A, B]
        """
        if len(path) > 4 and path[-4] == path[-2] and path[-3] == path[-1]:
            return True

    def paths_between_nodes(self, start_node, end_node):
        revisits = 5
        neighbours = [(start_node, [start_node])]
        paths = []
        while neighbours:
            (this_node, path) = neighbours.pop(0)
            if self._stuck(path):
                continue
            for next_node in this_node.links:
                full_path = path + [next_node]
                if next_node == end_node:
                    paths.append(full_path)
                if full_path.count(end_node) < revisits + 1:
                    neighbours.append((next_node, full_path))
        return paths

    def _path_from_node(self, node, max_depth=-1):
        yield node
        if node:
            for link in node.links:
                for n in self._path_from_node(link):
                    yield n


class Planner:
    ERR = 'NO SUCH ROUTE'

    def __init__(self, *edges):
        self.graph = Graph()
        self._build_graph_from_edges(*edges)

    def _build_graph_from_edges(self, *edges):
        for edge in edges:
            from_node = self.graph.get(edge[0], Node(edge[0]))
            to_node = self.graph.get(edge[1], Node(edge[1]))
            distance = int(edge[2])
            self.graph.add_nodes(from_node, to_node)
            from_node.add_link(to_node, distance)

    def get_route(self, *town_names):
        """Return a Route object for a supplied list of towns to visit. The
        Route is determined by the order of the towns passed as args.

        Args:
            town_names - the list of town names in order of travel ordered
        """
        towns = [self.graph[t] for t in town_names]
        if not self.graph.is_valid_path(*towns):
            raise ValueError(self.ERR)
        return Journey(*towns)

    def get_routes_between(self, start_town_name, end_town_name,
                           max_distance=None, min_stops=0, max_stops=10):
        paths = self.graph.paths_between_nodes(
            start_node=self.graph[start_town_name],
            end_node=self.graph[end_town_name]
        )
        journeys = [Journey(*path) for path in paths]
        # Filter using stop boundaries
        journeys = [j for j in journeys if min_stops <= j.stops <= max_stops]
        # Filter using max_distance boundary
        max_distance = max_distance or self.graph.total_graph_distance
        return [j for j in journeys if j.distance < max_distance]

    def get_shortest_route_between(self, start_town_name, end_town_name):
        all_routes = self.get_routes_between(
            start_town_name,
            end_town_name
        )
        if all_routes:
            return min(all_routes, key=lambda r: r.distance)
        return Journey()


class Journey:

    def __init__(self, *towns):
        """A Journey is a single path through a route Graph."""
        self.towns = towns

    @property
    def stops(self):
        return len(self.towns) - 1

    @property
    def pretty(self):
        """Return towns in a readable format.

        [town1.name, town2.name, etc.]
        """
        return [t.name for t in self.towns]

    @property
    def distance(self):
        """Total distance of this route. An empty route has distance == 0."""
        distance = 0
        for i, town in enumerate(self.towns[:-1]):
            next_town = self.towns[i+1]
            distance += town.links[next_town]
        return distance
