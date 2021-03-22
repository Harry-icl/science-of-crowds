"""Module containing the NetworkModel class."""

import networkx as nx
import csv
import numpy as np
from math import ceil

class NetworkModel(nx.DiGraph):
    """Abstract class to provide some more intuitive functions for modelling a building as a network."""

    def add_walkway(self, start, end, length, limiting_flow=3.3, free_speed=1.25):
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
        self.add_edge(start, end, length=length, flow_rate=limiting_flow, free_speed=free_speed, populations=[0] * (int(length / free_speed) + 1))

    def add_doorway(self, name, width=1, limiting_flow_rate=0.7):
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
            self.nodes[name]["population"] = 0
        else:
            self.add_node(name, flow_rate=limiting_flow_rate*width, population=0)

    def add_open_space(self, name):
        """
        Add an open space to the network model.

        Parameters
        ----------
        name(str): The number of the node.
        """
        if name in self.nodes():
            self.nodes[name]["flow_rate"] = np.inf
            self.nodes[name]["population"] = 0
        else:
            self.add_node(name, flow_rate=np.inf, population=0)

    def add_graph_from_csv(self, filepath, limiting_flow_walkway=3.3, limiting_flow_rate_doorway=0.7, free_speed_walkway=1.25):
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
                    _, start, end, length = row
                    self.add_walkway(start, end, float(length), limiting_flow=limiting_flow_walkway, free_speed=free_speed_walkway)
                elif row[0] == "d":
                    _, location, width = row
                    self.add_doorway(location, float(width), limiting_flow_rate=limiting_flow_rate_doorway)
                elif row[0] == "o":
                    _, location, _ = row
                    self.add_open_space(location)
