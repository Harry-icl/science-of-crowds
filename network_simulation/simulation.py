import csv
import matplotlib.pyplot as plt
from itertools import count
import networkx as nx

from network import NetworkModel

class Simulation:
    def __init__(self, filepaths, limiting_flow_walkway=100, limiting_flow_rate_doorway=42, free_speed_walkway=1.25):
        self.network_model = NetworkModel()
        self.T = 0
        self.evacuated = 0
        for filepath in filepaths:
            self.network_model.add_graph_from_csv(filepath, limiting_flow_walkway, limiting_flow_rate_doorway, free_speed_walkway)
    
    def set_initial_populations(self, filepath):
        with open(filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
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
            
            #REFACTOR ALL THIS TO USE MIN INSTEAD OF MULTIPLE LINES
            else:
                if self.network_model.nodes[next_node]["population"] <= self.network_model.nodes[next_node][flow_rate]:
                    self.evacuated += self.network_model.nodes[next_node]["population"]
                    self.network_model.nodes[next_node]["population"] = 0
                else:
                    self.evacuated += self.network_model.nodes[next_node][flow_rate]
                    self.network_model.nodes[next_node]["population"] -= self.network_model.nodes[next_node][flow_rate]
            for edge in in_edges:
                if self.network_model.edges[edge]["populations"][-1] > 0:
                    self.network_model.nodes[next_node]["population"] += self.network_model.edges[edge]["populations"][-1]
                    self.network_model.edges[edge]["populations"][-1] = 0
                for i in range(1, len(self.network_model.edges[edge]["populations"])):
                    self.network_model.edges[edge]["populations"][i] += self.network_model.edges[edge]["populations"][i - 1]
                    self.network_model.edges[edge]["populations"][i - 1] = 0
                if self.network_model.edges[edge]["populations"][0] > 0:
                    if self.network_model.edges[edge]["populations"][0] <= self.network_model.edges[edge]["flow_rate"]:
                        self.network_model.edges[edge]["populations"][1] += self.network_model.edges[edge]["populations"][0]
                        self.network_model.edges[edge]["populations"][0] = 0
                    else:
                        self.network_model.edges[edge]["populations"][1] += self.network_model.edges[edge]["flow_rate"]
                        self.network_model.edges[edge]["populations"][0] -= self.network_model.edges[edge]["flow_rate"]

                to_go.append(edge[0])         

    def _update_drawing_to_current_state(self):
        groups = set(nx.get_node_attributes(self.network_model, 'population').values())
        mapping = dict(zip(sorted(groups),count()))
        nodes = self.network_model.nodes()
        colors = [mapping[self.network_model.nodes[n]['population']] for n in nodes]

        pos = nx.spring_layout(self.network_model)
        ec = nx.draw_networkx_edges(self.network_model, pos, alpha=0.2)
        nc = nx.draw_networkx_nodes(self.network_model, pos, nodelist=nodes, node_color=colors, with_labels=False, node_size=100, cmap=plt.cm.jet)
        plt.show()
