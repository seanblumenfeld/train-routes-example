import argparse
import os

from data import DATA_DIR


class Node:

    def __init__(self, name):
        """node is supplied in the form: [A-Z][A-Z][0-9]."""
        self.name = name
        self.links = {}

    def __str__(self):
        return self.name

    @property
    def pretty(self):
        """Return links in a readable format

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
        """Override getitem to retrieve a node from the graph by its name."""
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
        """Retrieve a node from the graph by its name. If node_name cannot be
        found in the graph then default is returned.

        This method mirrors the standard python builtin dict.get().
        """
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
        """The Integer distance from one node to another node."""
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

    def paths_between_nodes(self, start_node, end_node, revisits=5):
        """Return all possible paths between two nodes in the graph.

        This is the main algorithm of the graph. The algorithm iterates through
        nodes while maintaining a list of neighbours and thus possible
        alternate routes.

        This algorithm will return a list of paths where the first always has
        the fewest nodes and the last will have the most nodes.

        Args:
            start_node - Node object of start node
            end_node - Node object of end node
            revisits - The number of times we allow the algorithm to revist the
                       start_node. This can be used to limit the number of
                       returned paths for a more optimal search.
        """
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


class Planner:
    ERR = 'NO SUCH ROUTE'

    def __init__(self, *edges):
        self.graph = Graph()
        self._build_graph_from_edges(*edges)

    def _build_graph_from_edges(self, *edges):
        """Build a graph object from a supplied list of "edges".

        An edge is defined as a string of the format [A-Z][A-Z][0-9], where:
            - The first character is the start town of an edge.
            - The second character is the end town of an edge.
            - The third character is the (one-way) distance of the edge.
        """
        for edge in edges:
            from_node = self.graph.get(edge[0], Node(edge[0]))
            to_node = self.graph.get(edge[1], Node(edge[1]))
            distance = int(edge[2])
            self.graph.add_nodes(from_node, to_node)
            from_node.add_link(to_node, distance)

    def _paths_to_journeys(self, paths):
        """Convert a list of Graph paths to Journey objects."""
        return [Journey(*path) for path in paths]

    def _filter_journeys_by_stops(self, journeys, min_stops, max_stops):
        """Filter a list of Journeys by the number of stops it has."""
        return [j for j in journeys if min_stops <= j.stops <= max_stops]

    def _filter_journeys_by_distance(self, journeys, max_distance):
        """Filter a list of Journeys by its distance."""
        return [j for j in journeys if j.distance < max_distance]

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
        """Return all possible routes between two towns.

        This method has 3 arguements available to the user to limit the routes
        returned to an acceptable list.

        Args:
            start_town_name - String (format: [A-Z]) name of start town
            end_town_name - String (format: [A-Z]) name of end town
            max_distance - Positive Integer. Maximum distance allowed for all
                           returned routes.
            min_stops - Integer >= 0. Minimum number of stops allowed for all
                           returned routes.
            max_stops - Integer >= 0. Maximum number of stops allowed for all
                           returned routes.
        """
        paths = self.graph.paths_between_nodes(
            start_node=self.graph[start_town_name],
            end_node=self.graph[end_town_name]
        )
        journeys = self._paths_to_journeys(paths)
        journeys = self._filter_journeys_by_stops(
            journeys,
            min_stops,
            max_stops
        )
        # Filter using max_distance boundary
        max_distance = max_distance or self.graph.total_graph_distance
        return self._filter_journeys_by_distance(journeys, max_distance)

    def get_shortest_route_between(self, start_town_name, end_town_name):
        """Return the shortest possible route between two towns.

        This method uses the paths_between_nodes method with 0 or 1 revisits
        depending on the town inputs.

        Here we do not simply use the get_routes_between method and filter
        for shortest list because this is a more expensive operation. We know
        that the paths_between_nodes method always returns the shortest route
        first. Therefore we set revisits to 0 or 1 depending on town input so
        that we get a shorter list and the paths_between_nodes algorithm does
        minimal work.

        Args:
            start_town_name - String (format: [A-Z]) name of start town
            end_town_name - String (format: [A-Z]) name of end town
        """
        revisits = 0
        if start_town_name == end_town_name:
            revisits = 1
        paths = self.graph.paths_between_nodes(
            start_node=self.graph[start_town_name],
            end_node=self.graph[end_town_name],
            revisits=revisits
        )

        journeys = self._paths_to_journeys(paths)
        if journeys:
            return min(journeys, key=lambda r: r.distance)
        return Journey()


class Journey:

    def __init__(self, *towns):
        """A Journey is a single path through a route Graph."""
        self.towns = towns

    @property
    def stops(self):
        """Number of stops on this route."""
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--graph_file',
        '-g',
        help='--graph_file <FILEPATH> ; Build a graph from an input file.'
    )
    xargs = parser.parse_args()
    if xargs.graph_file:
        # The problem sheet is very vague as to what the input file will
        # contain and what the purpose of tis file is. I have assumed that the
        # input file will contain a definition of a graph following a format
        # of one edge per line; file example:
        #   AB2
        #   BC3
        #   CA9
        # This simply prints out that graph in a readable format.
        print('Graph File supplied: {}'.format(xargs.graph_file))
        with open(os.path.join(DATA_DIR, xargs.graph_file)) as f:
            edges = f.read().splitlines()
        planner = Planner(*edges)
        print('Graph nodes: {0}'.format(planner.graph.pretty))
