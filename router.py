import numpy as np
import matplotlib.pyplot as plt

class Router:

  def __init__(self, arrival_rate, process_rate, K):
    '''
    The router follows an M/M/1/K model.
    Arrival and processing times follow an exponential distribution.
    
    arrival_rate: arrival rate (lambda)
    process_rate: base processing rate (mu)
    K: system capacity (1 in service + K-1 in buffer)
    '''
    self.arrival_rate = arrival_rate
    self.process_rate = process_rate # Current processing rate
    self.min_p_rate = process_rate   # Base processing rate
    self.max_p_rate = process_rate * 2 # "Turbo" processing rate
    self.K = K
    self.threshold_history = []
    # some interesting statistics
    self.queue_history = []
    self.time_history = []
    self.stats = {}

  def threshold(self, queue):
    '''
    Sets the processing rate based on a simple threshold.
    The threshold is half of the total system capacity K.
    
    Note: len(queue) is the buffer size (max K-1).
    '''
    # We compare the buffer length to a threshold
    if len(queue) > self.K / 2:
        self.process_rate = self.max_p_rate
    else:
        self.process_rate = self.min_p_rate
    self.threshold_history.append(self.process_rate)

  def simulation(self, time=1000, n_packets=100):
    '''
    The simulation is event-based.
    It runs for a user-defined time, with a set number of packets to be generated.
    
    time: simulation time
    n_packets: number of packets
    '''
    # statistics collected for each simulation. 
    # They are always reset to avoid conflicts.
    self.stats = {'waiting_time': 0.0, 'busy_time': 0.0}
    self.time_history = [0.0]
    self.queue_history = [0]
    self.threshold_history = [] # Also reset threshold history
    packets_delivered = 0
    packets_lost = 0

    processing = False # we always start with an idle queue
    packet_queue = [] # each waiting packet will be stored in this queue

    arrival_intervals = np.random.exponential(scale=1/self.arrival_rate, size=n_packets)
    arrival_times = np.cumsum(arrival_intervals)
    events = [['arrival', event_time] for event_time in arrival_times] # all arrivals

    while events: # while there are still events
      # Set the service rate for this event loop
      # based on the queue state *before* the event
      self.threshold(packet_queue) 
      
      events.sort(key=lambda e: e[1]) # sort events by time
      event = events.pop(0) # get the first event and remove it from the list
      event_type = event[0]

      # jump to this event's time
      t = event[1]

      # if the event occurs after the end time, the simulation stops
      if t > time:
          break
      
      # there are two types of events: arrival and processing. 
      # each one is analyzed differently
      if event_type == 'arrival':
        if not processing:
          processing = True # server starts working
          # Use the process_rate set at the start of the loop
          service_duration = np.random.exponential(scale=1/self.process_rate)
          t_processing_ends = t + service_duration
          # processing is an event, and it will be added to the event list
          # this is why we need the sort at the start of the loop
          events.append(['processing', t_processing_ends])
          self.stats['busy_time'] += service_duration
        else:
          # System is busy, check buffer (K-1)
          if len(packet_queue) < self.K - 1:
            packet_queue.append(t) # store the arrival time
          else:
            packets_lost += 1
      
      elif event_type == 'processing':
        packets_delivered += 1

        if len(packet_queue) > 0:
          # we process the queue
          arrival_time_of_next = packet_queue.pop(0)
          wait = t - arrival_time_of_next
          self.stats['waiting_time'] += wait

          # Use the process_rate set at the start of the loop
          service_duration = np.random.exponential(scale=1/self.process_rate)
          t_processing_ends = t + service_duration
          events.append(['processing', t_processing_ends])
          self.stats['busy_time'] += service_duration
        else:
          # if there's nothing to do, the channel becomes idle
          processing = False

      # history logging
      current_packets_in_system = len(packet_queue) + (1 if processing else 0)
      self.time_history.append(t)
      self.queue_history.append(current_packets_in_system)

    # some statistics
    self.stats['packets_delivered'] = packets_delivered
    self.stats['packets_lost'] = packets_lost
    # Truncate time_history to match simulation end time
    if self.time_history[-1] > time:
        self.time_history[-1] = time


  def statistics(self):
    '''
    Calculates and prints the final statistics of the simulation.
    '''

    total_packets = self.stats['packets_delivered'] + self.stats['packets_lost']
    
    # Avoid division by zero if no packets were processed
    if total_packets > 0:
        self.stats['drop_probability'] = self.stats['packets_lost'] / total_packets
    else:
        self.stats['drop_probability'] = 0.0

    simulation_duration = self.time_history[-1]
    if simulation_duration > 0:
        self.stats['utilization'] = self.stats['busy_time'] / simulation_duration
        self.stats['throughput'] = self.stats['packets_delivered'] / simulation_duration
    else:
        self.stats['utilization'] = 0.0
        self.stats['throughput'] = 0.0

    if self.stats['packets_delivered'] > 0:
      self.stats['avg_waiting_time'] = self.stats['waiting_time'] / self.stats['packets_delivered']
    else:
      self.stats['avg_waiting_time'] = 0.0
    
    if self.threshold_history:
        self.stats['process_rate_med'] = np.mean(self.threshold_history)
        self.stats['process_rate_dev'] = np.std(self.threshold_history) # std is sqrt(var)
    else:
        self.stats['process_rate_med'] = 0.0
        self.stats['process_rate_dev'] = 0.0


    print("\n" + "="*50)
    print("Statistics")
    print("="*50)
    print(f"Simulation Time: {simulation_duration:.4f} seconds")
    print(f"Packets delivered: {self.stats['packets_delivered']}")
    print(f"Packets lost: {self.stats['packets_lost']}")
    print(f"Average service rate: {self.stats['process_rate_med']:.4f}")
    print(f"Service rate std dev: {self.stats['process_rate_dev']:.4f}")
    print(f"Loss probability: {self.stats['drop_probability']*100:.2f}%")
    print(f"Server utilization: {self.stats['utilization']*100:.2f}%")
    print(f"Average waiting time in queue: {self.stats['avg_waiting_time']:.4f} seconds")
    print(f"Throughput: {self.stats['throughput']:.4f} packets/second")


  def plot_results(self):
    '''
    Plots the queue evolution over time and the steady-state
    probability for each state.
    '''
    if not self.time_history or not self.queue_history:
        print("No data to plot. Run the simulation first.")
        return

    plt.figure(figsize=(14, 10)) # Increased figure height

    # --- Plot 1: Packet Evolution ---
    plt.subplot(2, 2, 1)
    plt.step(self.time_history, self.queue_history, where='post')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Packets in System')
    plt.title('System Packet Evolution')
    plt.grid(True, linestyle='--', alpha=0.6)

    # --- Plot 2: State Distribution ---
    plt.subplot(2, 2, 2)
    # calculation of probability based on time spent in each state
    time_in_state = {}
    for i in range(len(self.time_history) - 1):
        state = self.queue_history[i]
        duration = self.time_history[i+1] - self.time_history[i]
        time_in_state[state] = time_in_state.get(state, 0) + duration

    total_time_sim = self.time_history[-1]
    if total_time_sim > 0:
        # Ensure all states from 0 to K are plotted
        all_states = list(range(self.K + 1))
        probabilities = [time_in_state.get(s, 0) / total_time_sim for s in all_states]
        plt.bar(all_states, probabilities, alpha=0.75, edgecolor='black', width=0.8)
        plt.xticks(all_states)

    plt.xlabel('Packets in System (State n)')
    plt.ylabel('Probability P(n)')
    plt.title('System State Distribution')
    plt.grid(True, linestyle='--', alpha=0.6)

    
    # --- Plot 3: Service Rate Evolution ---
    plt.subplot(2, 1, 2) # Use 2,1,2 to span the full width
    # Plot rate against the time the event *occurred*
    # time_history has N+1 elements, threshold_history has N elements
    if self.threshold_history:
        plt.step(self.time_history[1:], self.threshold_history, where='pre', color='r')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Service Rate')
    plt.title('Service Rate Evolution')
    plt.grid(True, linestyle='--', alpha=0.6)
    # Set y-axis limits to clearly show the two rates
    plt.ylim(self.min_p_rate * 0.9, self.max_p_rate * 1.1) 
    
    plt.tight_layout()
    plt.show() 

# --- Main execution ---
print("--- Starting Test 1: System with Moderate Load ---")
sim_time = 49
n_packets = 200
router_1 = Router(arrival_rate=5, process_rate=3, K=10)
router_1.simulation(time=sim_time, n_packets=n_packets)
router_1.statistics()
router_1.plot_results()
