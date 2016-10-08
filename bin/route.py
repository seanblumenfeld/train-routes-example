class Node:

    def __init__(self, name):
        """node is supplied in the form: [A-Z][A-Z][0-9]."""
        self.name = name
        self.links = {}

    def __str__(self):
        return self.name

    @property
    def pretty_links(self):
        """Print the links in a pretty format

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
    def pretty_nodes(self):
        """Print the nodes in a readable format.

        [node1.name, node2.name, etc.]
        """
        return [n.name for n in self.nodes]

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

    def paths_between_nodes(self, start_node, end_node, revisits=0):
        neighbours = [(start_node, [start_node])]
        all_paths = []
        while neighbours:
            (this_node, path) = neighbours.pop(0)
            for next_node in this_node.links:
                _path = path + [next_node]
                if next_node == end_node:
                    all_paths.append(_path)
                if _path.count(end_node) < revisits + 1:
                    neighbours.append((next_node, _path))
        return all_paths

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

        # Build new graph of nodes and links applicable to this route only
        route = Route(start_town_name=town_names[0])
        for town in towns[1:]:
            previous_town = towns[towns.index(town)-1]
            distance = self.graph.distance_from_node1_to_node2(
                from_node=previous_town,
                to_node=town
            )
            route.add_destination(town.name, distance)
        return route

    def get_routes_between(self, start_town_name, end_town_name, min_stops,
                           max_stops):
        min_towns = min_stops + 1
        max_towns = max_stops + 1
        start_node = self.graph[start_town_name]
        end_node = self.graph[end_town_name]
        paths = self.graph.paths_between_nodes(start_node, end_node, revisits=1)
        accepted_paths = [p for p in paths if min_towns <= len(p) <= max_towns]
        return [[t.name for t in p] for p in accepted_paths]


class Route:

    def __init__(self, start_town_name):
        """A Route requires a starting town in order to be a valid route."""
        self.graph = Graph()
        self.start_town = Node(start_town_name)
        self.graph.add_nodes(self.start_town)

    @property
    def distance(self):
        """Total distance of this route."""
        distance = 0
        for node in self.graph.nodes:
            distance += sum(node.links.values())
        return distance

    @property
    def end_town(self):
        return self.graph.nodes[-1]

    def add_destination(self, town_name, distance):
        """Add the next destination to the end of our route.

        Args:
            town_name - The name of the town to add as the next destination
            distance - distance from previous town in route to this town_name
        """
        town = Node(town_name)
        self.graph.nodes[-1].add_link(town, distance)
        self.graph.add_nodes(town)
