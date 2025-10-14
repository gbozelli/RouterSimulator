# M/M/1/K Queueing System Simulator for a Network Router

This project provides a Python-based, event-driven simulation of a network router modeled as an **M/M/1/K queueing system**. The goal is to analyze the router's performance under various traffic conditions by calculating key metrics and comparing the results with established queueing theory.

## What is an M/M/1/K System?

The Kendall notation (M/M/1/K) describes a specific queueing model:
-   **M (Markovian/Memoryless):** The time between packet arrivals follows an exponential distribution (a Poisson process).
-   **M (Markovian/Memoryless):** The packet processing (service) time also follows an exponential distribution.
-   **1:** There is a single server (the router's processor).
-   **K:** The system has a finite capacity of **K**. This includes the packet being serviced and those waiting in the queue. If a packet arrives when the system already holds K packets, it is dropped (lost).

This model is widely used to analyze the performance of communication systems and computer networks.

## 🚀 Features

-   **Event-Driven Simulation:** The system evolves through discrete events (packet arrival, processing completion), providing an accurate model of the queue dynamics.
-   **Comprehensive Statistical Analysis:** Automatically calculates and displays key performance metrics:
    -   **Packet Drop Probability:** The percentage of packets lost because the buffer was full.
    -   **Server Utilization:** The percentage of time the router was busy processing packets.
    -   **Average Waiting Time:** The average time a packet spends in the queue before being served.
    -   **Throughput:** The rate at which packets are successfully processed and delivered by the system.
-   **Theoretical Comparison:** Compares the simulated packet loss probability with the theoretical value from the M/M/1/K formula to validate the simulation's accuracy.
-   **Graphical Visualization:** Generates two plots for easier analysis:
    1.  **Queue Evolution:** Shows the number of packets in the system over time.
    2.  **State Distribution:** Displays the probability of the system being in each state (from 0 to K packets).

## 📋 How to Use

### 1. Prerequisites

Ensure you have `numpy` and `matplotlib` installed. If not, you can install them using pip:

```bash
pip install numpy matplotlib
```

### 2. Running the Code

Copy the Router class code into a Python file (e.g., simulator.py) and add the following snippet to configure and run the simulation.

```python
# [PASTE THE ROUTER CLASS CODE HERE]

# --- Example Usage ---

if __name__ == "__main__":
    # --- Simulation Parameters ---
    
    # Arrival rate (λ): packets per second
    arrival_rate = 5.0

    # Processing rate (μ): packets per second
    process_rate = 6.0

    # System capacity (K): 1 in service + (K-1) in the queue
    system_capacity = 10

    # --- Setup and Execution ---
    
    # 1. Create a router instance
    router = Router(
        arrival_rate=arrival_rate,
        process_rate=process_rate,
        K=system_capacity
    )

    # 2. Run the simulation
    # Simulates for 2000 seconds, generating up to 10,000 packets
    router.simulation(time=2000, n_packets=10000)

    # 3. Display the statistics
    router.statistics()

    # 4. Plot the results
    router.plot_results()
```

### 3. Analyzing the Output

When you run the script, a statistical summary will be printed to the console, and a new window will display the plots.

**Example Console Output:**
```
==================================================
Statistics
==================================================
Simulation Time: 2000.00 seconds
Packets delivered: 9950
Packets lost: 50
Drop probability: 0.50%
Server utilization: 82.95%
Average waiting time in queue: 0.4532 seconds
Throughput: 4.9750 packets/second

-------------------- Theoretical Comparison ------------------
Rho (traffic intensity): 0.8333
Theoretical loss probability (M/M/1/K): 0.45%
==================================================
```

## 🛠️ Code Structure

The simulation is encapsulated within the `Router` class, which has the following main methods:

- `__init__(self, arrival_rate, process_rate, K)`: Initializes the router with the parameters λ (arrival), μ (processing), and K (capacity).
- `simulation(self, time, n_packets)`: Runs the event-driven simulation, collecting data on the system's behavior.
- `statistics(self)`: Calculates and prints the performance metrics, including a comparison with theoretical results.
- `plot_results(self)`: Generates the visualization plots using matplotlib.
