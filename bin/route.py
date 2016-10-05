class Node:

    def __init__(self, name):
        """node is supplied in the form: [A-Z][A-Z][0-9]."""
        self.name = name
        self.links = {}

    @property
    def pretty_links(self):
        """Print the links in a pretty format

        [{node1.name: distance}, {node2.name: distance}, etc.]
        """
        return {str(l): v for l, v in self.links.items()}

    def __str__(self):
        return self.name

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

    @property
    def distance(self):
        """Total distance of a graph."""
        distance = 0
        for node in self.nodes:
            distance += sum(node.links.values())
        return distance

    def get_node_from_name(self, node_name):
        try:
            node = [n for n in self.nodes if n.name == node_name][0]
        except IndexError as e:
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
        self._build_graph_from_edges(self.graph, *edges)

    def _build_graph_from_edges(self, graph, *edges):
        for edge in edges:
            node_from = graph.get_node_from_name(edge[0]) or Node(edge[0])
            node_to = graph.get_node_from_name(edge[1]) or Node(edge[1])
            distance = int(edge[2])
            graph.add_nodes(node_from, node_to)
            node_from.add_link(node_to, distance)

    def get_route(self, *destinations):
        """Get a route for number of destinations.

            The Order of the route plan is determined by the order or destinations
            passed.

            args:
                start_destination
                first_destination
                other destinations
        """
        if not self.graph.is_valid_path(*destinations):
            raise ValueError(self.ERR)

        # Build new graph of nodes and links applicable to this route only
        route_nodes = [Node(d) for d in destinations]
        for i, node in enumerate(route_nodes[:-1]):
            next_node = route_nodes[i+1]
            node_from_graph = self.graph.get_node_from_name(node.name)
            next_node_from_graph = self.graph.get_node_from_name(next_node.name)
            node_to_next_node_distance_from_graph = node_from_graph.links[next_node_from_graph]
            node.add_link(next_node, node_to_next_node_distance_from_graph)
        route_graph = Graph()
        route_graph.add_nodes(*route_nodes)
        return route_graph

