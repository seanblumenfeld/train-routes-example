from bin import route

from unittest import TestCase


class NodeTests(TestCase):

    def setUp(self):
        self.root_node = route.Node('root_node')

    def test_can_add_link_to_node(self):
        node = route.Node('node')
        self.root_node.add_link(node, 1)
        self.assertIn(node, self.root_node.links)

    def test_distance_of_link_to_node(self):
        node = route.Node('node')
        distance = 5
        self.root_node.add_link(node, distance)
        self.assertEquals(distance, self.root_node.links[node])


class GraphTests(TestCase):

    def setUp(self):
        self.graph = route.Graph()

    def test_can_add_nodes_to_graph(self):
        nodes = [route.Node('0'), route.Node('1')]
        self.graph.add_nodes(*nodes)
        self.assertListEqual(nodes, self.graph.nodes)

    def test_adding_existing_node_to_graph_does_not_duplicate(self):
        node = route.Node('0')
        self.graph.add_nodes(node, node)
        self.assertListEqual([node], self.graph.nodes)

    def test_can_add_no_nodes(self):
        self.graph.add_nodes()
        self.assertFalse(self.graph.nodes)

    def test_get_node_gives_back_correct_node(self):
        node = route.Node('1')
        self.graph.add_nodes(node)
        self.assertEquals(node, self.graph['1'])

    def _build_0123_graph(self):
        """Graph for this TestCase is as follows.
                  0
                ↙ ↘
               1    2
             ↙
            3
        """
        nodes = [
            route.Node('0'),
            route.Node('1'),
            route.Node('2'),
            route.Node('3'),
        ]
        nodes[0].add_link(nodes[1], 0)
        nodes[0].add_link(nodes[2], 0)
        nodes[1].add_link(nodes[3], 0)
        self.graph.add_nodes(*nodes)
        return nodes

    def test_is_valid_path_returns_true(self):
        nodes = self._build_0123_graph()
        self.assertTrue(self.graph.is_valid_path(nodes[0]))
        self.assertTrue(self.graph.is_valid_path(nodes[0], nodes[1]))
        self.assertTrue(self.graph.is_valid_path(nodes[0], nodes[1], nodes[3]))
        self.assertTrue(self.graph.is_valid_path(nodes[1], nodes[3]))

    def test_is_not_valid_path_for_invalid_path(self):
        nodes = self._build_0123_graph()
        self.assertFalse(self.graph.is_valid_path(nodes[0], nodes[3]))
        self.assertFalse(self.graph.is_valid_path(nodes[1], nodes[2]))

    def test_is_valid_path_raises_for_backwards_path(self):
        nodes = self._build_0123_graph()
        self.assertFalse(self.graph.is_valid_path(nodes[1], nodes[0]))

    def test_paths_between_same_node_is_empty(self):
        nodes = self._build_0123_graph()
        paths = self.graph.paths_between_nodes(nodes[0], nodes[0])
        self.assertListEqual([p for p in paths], [])

    def test_paths_between_0_and_3(self):
        nodes = self._build_0123_graph()
        paths = self.graph.paths_between_nodes(nodes[0], nodes[3])
        expected = [[nodes[0], nodes[1], nodes[3]]]
        self.assertListEqual([p for p in paths], expected)

    def test_paths_between_3_and_2_is_empty(self):
        nodes = self._build_0123_graph()
        paths = self.graph.paths_between_nodes(nodes[3], nodes[2])
        self.assertListEqual([p for p in paths], [])


class BDDTests(TestCase):

    def setUp(self):
        """Tree for this TestCase is as follows.
                          ____
                         A    \
                         ↓\   \
                       → B \   \
                     /   ↓  \  |
                    /    C   |  |
                    |  / ↕  /  |
                    | /  D ←   |
                    | \  ↓     /
                    |  → E ←←
                    |____/
        """
        edges = ['AB5', 'BC4', 'CD8', 'DC8', 'DE6', 'AD5', 'CE2', 'EB3', 'AE7']
        self.planner = route.Planner(*edges)

    def test_distance_of_ABC_is_9(self):
        route = self.planner.get_route('A', 'B', 'C')
        self.assertEquals(route.distance, 9)

    def test_distance_of_AD_is_5(self):
        route = self.planner.get_route('A', 'D')
        self.assertEquals(route.distance, 5)

    def test_distance_of_ADC_is_13(self):
        route = self.planner.get_route('A', 'D', 'C')
        self.assertEquals(route.distance, 13)

    def test_distance_of_AEBCD_is_22(self):
        route = self.planner.get_route('A', 'E', 'B', 'C', 'D')
        self.assertEquals(route.distance, 22)

    def test_AED_route_gives_no_such_route(self):
        self.assertRaisesRegex(
            ValueError,
            'NO SUCH ROUTE',
            self.planner.get_route, 'A', 'E', 'D'
        )

    def test_number_of_routes_starting_at_C_and_ending_at_C_3_max_stops(self):
        routes = self.planner.get_routes_between(
            start_town_name='C',
            end_town_name='C',
            min_stops=0,
            max_stops=3
        )
        self.assertEquals(len(routes), 2)

    def test_number_of_routes_starting_at_A_and_ending_at_C_4_stops(self):
        routes = self.planner.get_routes_between(
            start_town_name='A',
            end_town_name='C',
            min_stops=4,
            max_stops=4
        )
        self.assertEquals(len(routes), 3)

    def test_shortest_route_starting_at_A_and_ending_at_C(self):
        route = self.planner.get_shortest_route_between(
            start_town_name='A',
            end_town_name='C'
        )
        self.assertEquals(route.distance, 9)

    def test_shortest_route_starting_at_B_and_ending_at_B(self):
        route = self.planner.get_shortest_route_between(
            start_town_name='B',
            end_town_name='B'
        )
        self.assertEquals(route.distance, 9)

    def test_number_of_routes_from_C_to_C_with_distance_less_than_30(self):
        routes = self.planner.get_routes_between(
            start_town_name='C',
            end_town_name='C',
            max_distance=30
        )
        self.assertEquals(7, len(routes))
        pretty_routes = [r.pretty for r in routes]
        self.assertIn(['C', 'D', 'C'], pretty_routes)
        self.assertIn(['C', 'E', 'B', 'C'], pretty_routes)
        self.assertIn(['C', 'E', 'B', 'C', 'D', 'C'], pretty_routes)
        self.assertIn(['C', 'D', 'C', 'E', 'B', 'C'], pretty_routes)
        self.assertIn(['C', 'D', 'E', 'B', 'C'], pretty_routes)
        self.assertIn(['C', 'E', 'B', 'C', 'E', 'B', 'C'], pretty_routes)
        self.assertIn(
            ['C', 'E', 'B', 'C', 'E', 'B', 'C', 'E', 'B', 'C'],
            pretty_routes
        )
