"""Module containing the Simulation class."""

import csv
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
from copy import deepcopy

from .network import NetworkModel


class Simulation:
    """
    Class for creating a network model simulation.

    Attributes
    ----------
    network_model(NetworkModel): The underlying model.
    T(int): The time since the start of the evacuation.
    evacuated(float): The number of people already evacuated.
    start(NetworkModel): The initial state of the model.
    simulation_results(list): The state of the model at different timesteps.
    evacuated_results(list): The number of people evacuated at different
    timesteps.
    """

    def __init__(self,
                 filepaths,
                 limiting_flow_walkway=3.3,
                 limiting_flow_rate_doorway=0.7,
                 free_speed_walkway=1.25):
        """
        Create an instance of the Simulation class.

        Parameters
        ----------
        filepaths(list): The list of filepaths for edge/node files.
        limiting_flow_walkway(float): The limiting flow in walkways.
        limiting_flow_rate_doorway(float): The limiting flow rate through
        doorways.
        free_speed_walkway(float): The free speed in walkways.
        """
        self.network_model = NetworkModel()
        self.T = 0
        self.evacuated = 0
        for filepath in filepaths:
            self.network_model.add_graph_from_csv(filepath,
                                                  limiting_flow_walkway,
                                                  limiting_flow_rate_doorway,
                                                  free_speed_walkway)

    def set_initial_populations(self, filepath):
        """
        Set the initial populations of the network.

        Parameters
        ----------
        filepath(str): The filepath of the populations file.
        """
        self.evacuated = 0
        with open(filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    num, pop = row
                    self.network_model.nodes[num]["population"] = float(pop)

    def _increment_time(self):
        self.T += 1
        to_go = ["8"]
        while to_go:
            next = to_go.pop()
            in_edges = self.network_model.in_edges(next)
            out_edges = self.network_model.out_edges(next)
            if out_edges:
                to_dist = (min(self.network_model.nodes[next]["population"],
                               self.network_model.nodes[next]["flow_rate"])
                           / len(out_edges))
                for edge in out_edges:
                    self.network_model.edges[edge]["populations"][0] += to_dist
                    self.network_model.nodes[next]["population"] -= to_dist

            else:
                moving = min(self.network_model.nodes[next]["population"],
                             self.network_model.nodes[next]["flow_rate"])
                self.evacuated += moving
                self.network_model.nodes[next]["population"] -= moving

            for edge in in_edges:
                if self.network_model.edges[edge]["populations"][-1] > 0:
                    self.network_model.nodes[next]["population"] += \
                        self.network_model.edges[edge]["populations"][-1]
                    self.network_model.edges[edge]["populations"][-1] = 0
                pop_len = len(self.network_model.edges[edge]["populations"])
                for i in range(pop_len - 1, 1, -1):
                    self.network_model.edges[edge]["populations"][i] += \
                        self.network_model.edges[edge]["populations"][i - 1]
                    self.network_model.edges[edge]["populations"][i - 1] = 0
                if self.network_model.edges[edge]["populations"][0] > 0:
                    flow_rate = self.network_model.edges[edge]["flow_rate"]
                    pop = self.network_model.edges[edge]["populations"][0]
                    moving = min(flow_rate,
                                 pop)
                    self.network_model.edges[edge]["populations"][1] += moving
                    self.network_model.edges[edge]["populations"][0] -= moving
                to_go.append(edge[0])

    def _update(self, num, fixed_pos):
        self.ax.clear()
        graph = self.simulation_results[num]
        nodes = graph.nodes()
        edges = graph.edges()
        colors_nodes = [((graph.nodes[n]['population']
                          / self._get_total_population())
                         if n != "8"
                         else ((graph.nodes[n]["population"]
                               + self.evacuated_results[num])
                               / self._get_total_population())
                         for n in nodes)]
        colors_edges = [((sum(graph.edges[e]["populations"])
                          / self._get_total_population())
                         for e in edges)]
        pos = nx.spring_layout(graph, fixed=fixed_pos.keys(), pos=fixed_pos)
        nx.draw_networkx_edges(graph,
                               pos,
                               edgelist=edges,
                               edge_color=colors_edges,
                               width=3,
                               edge_cmap=plt.cm.jet,
                               edge_vmin=0,
                               edge_vmax=1)
        nx.draw_networkx_nodes(graph,
                               pos,
                               nodelist=nodes,
                               node_color=colors_nodes,
                               node_size=100,
                               cmap=plt.cm.jet,
                               vmin=0,
                               vmax=1)

    def _get_total_population(self):
        pop = (self.evacuated
               + sum([(self.network_model.nodes[node]["population"]
                       for node in self.network_model.nodes())])
               + sum([(sum(self.network_model.edges[edge]["populations"])
                       for edge in self.network_model.edges())]))
        return pop

    def animation(self, pos, filepath=None, show=False):
        """
        Animate the evacuation simulation.

        Parameters
        ----------
        pos(dict): The list of positions of nodes.
        filepath(str): The filepath to save the animation in.
        show(bool): Whether to display the animation or not.
        """
        self.simulate()
        print("Simulation DONE")
        self.fig, self.ax = plt.subplots(figsize=(20, 15))
        frame_count = len(self.simulation_results)
        ani = matplotlib.animation.FuncAnimation(self.fig,
                                                 lambda num: self._update(num,
                                                                          pos),
                                                 frames=frame_count,
                                                 interval=600,
                                                 repeat=False)
        print("Animation DONE")
        if filepath:
            ffmpeg_writer = matplotlib.animation.writers['ffmpeg']
            writer = ffmpeg_writer(fps=10,
                                   metadata=dict(artist="Harrison Mouat"),
                                   bitrate=1800)
            ani.save(filepath, writer=writer)
            print("SAVED")
        if show:
            plt.show()

    def simulate(self):
        """Simulate the evacuation."""
        self.start = self.network_model
        self.simulation_results = [deepcopy(self.network_model)]
        self.evacuated_results = [self.evacuated]
        while self.evacuated < self._get_total_population():
            self._increment_time()
            self.simulation_results.append(deepcopy(self.network_model))
            self.evacuated_results.append(self.evacuated)
        self.network_model = self.start
        print(f"Time to evacuate: {self.T}")
        print(f"Total population: {self._get_total_population()}")
        self.T = 0
