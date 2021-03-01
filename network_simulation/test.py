from network import NetworkModel
import networkx as nx
import matplotlib.pyplot as plt

huxley = NetworkModel()

huxley.add_graph_from_csv("./network_simulation/edges.csv")
huxley.add_graph_from_csv("./network_simulation/nodes1.csv")
print(huxley.nodes())
print(huxley.edges())

nx.draw(huxley)
plt.show()