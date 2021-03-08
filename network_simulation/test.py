from network_simulation import NetworkModel, Simulation
import networkx as nx
import matplotlib.pyplot as plt

huxley = NetworkModel()

huxley.add_graph_from_csv("./network_simulation/edges.csv")
huxley.add_graph_from_csv("./network_simulation/nodes1.csv")
print(huxley.nodes())
print(huxley.edges())

huxley_sim = Simulation(["./network_simulation/edges.csv", "./network_simulation/nodes1.csv"])
print(huxley_sim.network_model.nodes())
print(huxley_sim.network_model.edges())

huxley_sim.set_initial_populations("./network_simulation/populations.csv")
huxley_sim._update_drawing_to_current_state()

nx.draw(huxley)
plt.show()