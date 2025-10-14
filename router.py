import numpy as np
import matplotlib.pyplot as plt

class Router:

  def __init__(self, arrival_rate, process_rate, K):
    '''
    O roteador segue um modelo M/M/1/K. Os tempos
    de chegada e de processamento seguem uma distribuição
    exponencial. 
    arrival_rate: taxa de chegada
    process_rate: taxa de processamento
    K: capacidade da fila
    '''
    self.arrival_rate = arrival_rate
    self.process_rate = process_rate
    self.K = K 
    #algumas estatísticas interessantes
    self.queue_history = []
    self.time_history = []
    self.stats = {}

  def simulation(self, time=1000, n_packets=100):
    '''
    A simulação é baseada em eventos. Ocorre durante o
    tempo definido pelo usuário, com um número de pacotes 
    a serem gerados
    time: tempo de simulação
    n_packets: número de pacotes
    '''
    #estatísticas assimiladas a cada simulação. São sempre 
    #redefinidas para evitar conflito
    self.stats = {'waiting_time': 0.0, 'busy_time': 0.0}
    self.time_history = [0.0]
    self.queue_history = [0]
    packets_delivered = 0
    packets_lost = 0

    processing = False #sempre começamos com a fila ociosa
    packet_queue = [] #cada pacote em espera será guardado nessa fila
 
    arrival_intervals = np.random.exponential(scale=1/self.arrival_rate, size=n_packets)
    arrival_times = np.cumsum(arrival_intervals)
    events = [['arrival', event_time] for event_time in arrival_times] #todas as chegadas

    while events: #enquanto os eventos não acabam
      
      events.sort(key=lambda e: e[1]) #ordenação será explicada em breve
      event = events.pop(0) #pega o primeiro evento e o descarta
      event_type = event[0] 
      
      #pula para o tempo desse evento
      t = event[1]

      #se o evento ocorre depois do tempo final, a simulação para
      if t > time:
          break
      #existem dois tipos de evento: chegada e processamento. cada um
      #deles é analisado de forma distinta
      if event_type == 'arrival':
        if not processing:
          processing = True #servidor começa a trabalhar
          service_duration = np.random.exponential(scale=1/self.process_rate)
          t_processing_ends = t + service_duration
          #processamento é um evento, e será adicionado à lista de eventos
          #por isso precisamos do sort no início do loop, para ordenar corretamente
          events.append(['processing', t_processing_ends]) 
          self.stats['busy_time'] += service_duration
        else:
          if len(packet_queue) < self.K - 1:
            packet_queue.append(t) #guarda o tempo de chegada
          else:
            packets_lost += 1
      
      elif event_type == 'processing':
        packets_delivered += 1
        
        if len(packet_queue) > 0:
          #processamos a fila
          arrival_time_of_next = packet_queue.pop(0)
          wait = t - arrival_time_of_next
          self.stats['waiting_time'] += wait
          
          service_duration = np.random.exponential(scale=1/self.process_rate)
          t_processing_ends = t + service_duration
          events.append(['processing', t_processing_ends])
          self.stats['busy_time'] += service_duration
        else:
          #se não tem nada pra fazer, canal fica ocioso
          processing = False

      #registro do histórico
      current_packets_in_system = len(packet_queue) + (1 if processing else 0)
      self.time_history.append(t)
      self.queue_history.append(current_packets_in_system)

    #algumas estatísticas
    self.stats['packets_delivered'] = packets_delivered
    self.stats['packets_lost'] = packets_lost
    

  def statistics(self):
    '''
    Calcula e imprime as estatísticas finais da simulação.
    '''

    total_packets = self.stats['packets_delivered'] + self.stats['packets_lost']

    self.stats['drop_probability'] = self.stats['packets_lost'] / total_packets
    self.stats['utilization'] = self.stats['busy_time'] / self.time_history[-1]

    if self.stats['packets_delivered'] > 0:
      self.stats['avg_waiting_time'] = self.stats['waiting_time'] / self.stats['packets_delivered']
    else:
      self.stats['avg_waiting_time'] = 0

    self.stats['throughput'] = self.stats['packets_delivered'] / self.time_history[-1]
    
    print("\n" + "="*50)
    print("Estatísticas")
    print("="*50)
    print(f"Tempo de Simulação: {self.time_history[-1]} segundos")
    print(f"Pacotes entregues: {self.stats['packets_delivered']}")
    print(f"Pacotes perdidos: {self.stats['packets_lost']}")
    print(f"Probabilidade de perda: {self.stats['drop_probability']*100:.2f}%")
    print(f"Utilização do servidor: {self.stats['utilization']*100:.2f}%")
    print(f"Tempo médio de espera na fila: {self.stats['avg_waiting_time']:.4f} segundos")
    print(f"Throughput: {self.stats['throughput']:.4f} pacotes/segundo")

    #Comparações teóricas
    rho = self.arrival_rate / self.process_rate
    if rho != 1:
      p_loss = (rho**self.K) * (1 - rho) / (1 - rho**(self.K + 1))
    else:
      p_loss = 1 / (self.K + 1)

    print("\n" + "-"*20 + " Comparação Teórica " + "-"*18)
    print(f"Rho (intensidade de tráfego): {rho:.4f}")
    print(f"Probabilidade de perda teórica (M/M/1/K): {p_loss*100:.2f}%")
    print("="*50)

  def plot_results(self):
    '''
    Plota a evolução da fila no tempo e a probabilidade de permanência
    em cada estado
    '''
    if not self.time_history or not self.queue_history:
        print("Não há dados para plotar. Rode a simulação primeiro.")
        return

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.step(self.time_history, self.queue_history, where='post')
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Nº de Pacotes no Sistema')
    plt.title('Evolução do Nº de Pacotes no Sistema')
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.subplot(1, 2, 2)
    #calculo da probabilidade baseada no tempo em cada estado
    time_in_state = {}
    for i in range(len(self.time_history) - 1):
        state = self.queue_history[i]
        duration = self.time_history[i+1] - self.time_history[i]
        time_in_state[state] = time_in_state.get(state, 0) + duration
    
    total_time_sim = self.time_history[-1]
    if total_time_sim > 0:
        states = sorted(time_in_state.keys())
        probabilities = [time_in_state[s] / total_time_sim for s in states]
        plt.bar(states, probabilities, alpha=0.75, edgecolor='black', width=0.8)

    plt.xlabel('Nº de Pacotes no Sistema')
    plt.ylabel('Probabilidade')
    plt.title('Distribuição de Estado do Sistema')
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.show()
