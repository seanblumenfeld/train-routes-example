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

    def add_nodes(self, *nodes):
        """Add a node to the graph."""
        for node in nodes:
            if node.name not in [n.name for n in self.nodes]:
                self.nodes.append(node)

    @property
    def pretty_nodes(self):
        """Print the nodes in a readable format.

        [node1.name, node2.name, etc.]
        """
        return [n.name for n in self.nodes]

    def distance_from_node1_to_node2(self, node_from_name, node_to_name):
        node_from = self.get_node_from_name(node_from_name)
        node_to = self.get_node_from_name(node_to_name)
        try:
            return node_from.links[node_to]
        except IndexError:
            return

    def get_node_from_name(self, node_name):
        try:
            node = [n for n in self.nodes if n.name == node_name][0]
        except IndexError:
            node = None
        return node

    def is_valid_path(self, *node_names):
        """Assert that the supplied node names are linked in the graph. Order
        of node names provided dertermines the traverse path.

        Args:
            node_names - list of node names to test. String

        Returns:
            True - The path provided exists in the graph
            False - The path provided does not exist in the graph
        """
        for i, node_name in enumerate(node_names[:-1]):
            this_node = self.get_node_from_name(node_name)
            next_node = self.get_node_from_name(node_names[i+1])
            if next_node not in this_node.links:
                return False
        return True


class Planner:
    ERR = 'NO SUCH ROUTE'

    def __init__(self, *edges):
        self.graph = Graph()
        self._build_graph_from_edges(*edges)

    def _build_graph_from_edges(self, *edges):
        for edge in edges:
            node_from = self.graph.get_node_from_name(edge[0]) or Node(edge[0])
            node_to = self.graph.get_node_from_name(edge[1]) or Node(edge[1])
            distance = int(edge[2])
            self.graph.add_nodes(node_from, node_to)
            node_from.add_link(node_to, distance)

    def get_route(self, *town_names):
        """Return a Route object for a supplied list of towns to visit. The
        Route is determined by the order of the towns passed as args.

        Args:
            town_names - the list of town names in order of travel ordered
        """
        if not self.graph.is_valid_path(*town_names):
            raise ValueError(self.ERR)

        # Build new graph of nodes and links applicable to this route only
        route = Route(start_town_name=town_names[0])
        for town_name in town_names[1:]:
            previous_town_name = town_names[town_names.index(town_name)-1]
            distance = self.graph.distance_from_node1_to_node2(
                node_from_name=previous_town_name,
                node_to_name=town_name
            )
            route.add_destination(town_name, distance)
        return route

    def get_routes_between(self, start_town_name, end_town_name, max_stops):
        return [1,2]


class Route:

    def __init__(self, start_town_name):
        """A Route requires a starting town in order to be a valid route."""
        self.graph = Graph()
        start_town = Node(start_town_name)
        self.graph.add_nodes(start_town)

    def add_destination(self, town_name, distance):
        """Add the next destination to the end of our route.

        Args:
            town_name - The name of the town to add as the next destination
            distance - distance from previous town in route to this town_name
        """
        town = Node(town_name)
        self.graph.nodes[-1].add_link(town, distance)
        self.graph.add_nodes(town)

    @property
    def distance(self):
        """Total distance of this route."""
        distance = 0
        for node in self.graph.nodes:
            distance += sum(node.links.values())
        return distance
