from network_simulation import NetworkModel, Simulation
import networkx as nx
import matplotlib.pyplot as plt

huxley = NetworkModel()

huxley.add_graph_from_csv("./network_simulation/edges.csv")
huxley.add_graph_from_csv("./network_simulation/nodes1.csv")

huxley_sim = Simulation(["./network_simulation/edges.csv", "./network_simulation/nodes1.csv"])

pos = {"1": (0, 0), "2": (0, 1), "3": (1, 2), "4": (2, 2), "5": (3, 2), "6": (4, 3), "7": (2, 3), "8": (0, 3), "9": (2, 4), "10": (0, 4), "11": (0, 5), "12": (1, 5), "13": (0, 6), "14": (-1, 7), "15": (-1, 8), "16": (0, 9), "17": (1, 10), "18": (-1, 10), "19": (0, 11), "20": (-1, 12), "21": (0, 12), "22": (1, 10), "23": (1, 11), "24": (2, 12), "25": (3, 11), "26": (3, 10), "27": (4, 11), "28": (5, 12), "29": (6, 11), "30": (5, 10), "31": (7, 9), "32": (6, 8), "33": (6, 9), "34": (7, 6), "35": (7, 4), "36": (6, 4), "37": (5, 4), "38": (6, 4), "39": (4, 4), "40": (3, 4), "41": (2, 4), "42": (3, 5)}
for i in range(1, 10):
    print("\nProcessing simulation %s" % str(i))
    huxley_sim.set_initial_populations("./network_simulation/simulation_csvs/simulation%s.csv" % str(i))
    huxley_sim.animation(pos, filepath="./network_simulation/animations/animation%s.mp4" % str(i))
