"""Module containing the NetworkModel class."""

import networkx as nx
import csv

class NetworkModel(nx.DiGraph):
    """Abstract class to provide some more intuitive functions for modelling a building as a network."""

    def add_walkway(self, start, end, length, width=1, limiting_flow_rate=100, free_speed=1.25):
        """
        Add a walkway to the network model.

        Parameters
        ----------
        start(str): The starting node.
        end(str): The finishing node.
        width(float): The width of the walkway (at the narrowest point).
        limiting_flow_rate(float): The limiting flow rate in min^-1m^-1.
        free_speed(float): The free speed of the walkway.
        """
        self.add_edge(start, end, length=length, flow_rate=limiting_flow_rate*width, free_speed=free_speed})

    def add_doorway(self, name, width=1, limiting_flow_rate=42):
        """
        Add a doorway to the network model.

        Parameters
        ----------
        start(str): The starting node.
        end(str): The finishing node.
        width(float): The width of the doorway.
        limiting_flow_rate(float): The limiting flow rate in min^-1m^-1.
        free_speed(float): The free speed of the walkway.
        """
        if name in self.nodes():
            self.nodes[name]["flow_rate"] = limiting_flow_rate*width
        else:
            self.add_node(name, flow_rate=limiting_flow_rate*width)

    def add_open_space(self, name):
        """
        Add an open space to the network model.

        Parameters
        ----------
        name(str): The number of the node.
        """
        if name not in self.nodes():
            self.add_node(name)

    def add_edges_from_csv(filepath, limiting_flow_rate_walkway=100, limiting_flow_rate_doorway, free_speed_walkway=1.25, free_speed_doorway=1.25):
        """
        Add edges from a csv that is formatted as:
            start, end, type, width
        with the specified default values.

        Parameters
        ----------
        filepath(str): The filepath of the csv file.
        limiting_flow_rate_walkway(float): The limiting flow 
        """
        with open(filepath) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == "w":
                    start, end, _, length = row
                    self.add_walkway(start, end, length)
                elif row[0] == "d":
                    _, location, width = row
                    self.add_doorway(location, width)
                elif row[0]:
                    _, location = row
                    self.add_open_space(location)
