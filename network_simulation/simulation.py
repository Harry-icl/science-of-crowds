import csv
import matplotlib.pyplot as plt
import matplotlib
from itertools import count
import networkx as nx
from numpy import random
from copy import deepcopy
import matplotlib.colors as mcolors

from .network import NetworkModel

cmap = mcolors.LinearSegmentedColormap('CustomMap', {'red': ((0, 0, 0), (1, 1, 1)), 'green': ((0, 0, 0), (1, 0, 0)), 'blue': ((0, 0, 0), (1, 0, 0))})

class Simulation:
    def __init__(self, filepaths, limiting_flow_walkway=3.3, limiting_flow_rate_doorway=0.7, free_speed_walkway=1.25):
        self.network_model = NetworkModel()
        self.T = 0
        self.evacuated = 0
        for filepath in filepaths:
            self.network_model.add_graph_from_csv(filepath, limiting_flow_walkway, limiting_flow_rate_doorway, free_speed_walkway)
    
    def set_initial_populations(self, filepath):
        self.evacuated = 0
        with open(filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    node_num, population = row
                    self.network_model.nodes[node_num]["population"] = float(population)

    def _increment_time(self):
        self.T += 1
        to_go = ["8"]
        while to_go: # ASSUME THAT THE WALKWAYS ARE WIDTHLESS - I.E. INFINITE CROWDS CAN FORM AT THE END
            next_node = to_go.pop()
            in_edges = self.network_model.in_edges(next_node)
            # NODE OUTFLOWS
            out_edges = self.network_model.out_edges(next_node)
            if out_edges:
                to_dist = min(self.network_model.nodes[next_node]["population"], self.network_model.nodes[next_node]["flow_rate"]) / len(out_edges)
                for edge in out_edges:
                    self.network_model.edges[edge]["populations"][0] += to_dist
                    self.network_model.nodes[next_node]["population"] -= to_dist
            
            else:
                moving = min(self.network_model.nodes[next_node]["population"], self.network_model.nodes[next_node]["flow_rate"])
                self.evacuated += moving
                self.network_model.nodes[next_node]["population"] -= moving

            for edge in in_edges:
                if self.network_model.edges[edge]["populations"][-1] > 0:
                    self.network_model.nodes[next_node]["population"] += self.network_model.edges[edge]["populations"][-1]
                    self.network_model.edges[edge]["populations"][-1] = 0
                for i in range(len(self.network_model.edges[edge]["populations"]) - 1, 1, -1):
                    self.network_model.edges[edge]["populations"][i] += self.network_model.edges[edge]["populations"][i - 1]
                    self.network_model.edges[edge]["populations"][i - 1] = 0
                if self.network_model.edges[edge]["populations"][0] > 0:
                    moving = min(self.network_model.edges[edge]["flow_rate"], self.network_model.edges[edge]["populations"][0])
                    self.network_model.edges[edge]["populations"][1] += moving
                    self.network_model.edges[edge]["populations"][0] -= moving

                to_go.append(edge[0])         

    def _update(self, num, fixed_pos):
        self.ax.clear()
        graph = self.simulation_results[num]
        nodes = graph.nodes()
        edges = graph.edges()
        colors_nodes = [graph.nodes[n]['population']/self._get_total_population() if n != "8" else (graph.nodes[n]["population"] + self.evacuated_results[num])/self._get_total_population() for n in nodes]
        colors_edges = [sum(graph.edges[e]["populations"])/self._get_total_population() for e in edges]
        pos = nx.spring_layout(graph, fixed=fixed_pos.keys(), pos=fixed_pos)
        ec = nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color=colors_edges, width=3, edge_cmap=plt.cm.jet, edge_vmin=0, edge_vmax=1)
        nc = nx.draw_networkx_nodes(graph, pos, nodelist=nodes, node_color=colors_nodes, node_size=100, cmap=plt.cm.jet, vmin=0, vmax=1)
    
    def _get_total_population(self):
        population = self.evacuated + sum([self.network_model.nodes[node]["population"] for node in self.network_model.nodes()]) + sum([sum([self.network_model.edges[edge]["populations"][i] for i in range(len(self.network_model.edges[edge]["populations"]))]) for edge in self.network_model.edges()])
        return population

    def animation(self, pos, filepath=None, show=False):
        self.simulate()
        print("Simulation DONE")
        self.fig, self.ax = plt.subplots(figsize=(20, 15))
        ani = matplotlib.animation.FuncAnimation(self.fig, lambda num: self._update(num, pos), frames=len(self.simulation_results), interval=600, repeat=False)
        print("Animation DONE")
        if filepath:
            Writer = matplotlib.animation.writers['ffmpeg']
            writer = Writer(fps=10, metadata=dict(artist="Harrison Mouat"), bitrate=1800)
            ani.save(filepath, writer=writer)
            print("SAVED")
        if show:
            plt.show()

    def simulate(self):
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
