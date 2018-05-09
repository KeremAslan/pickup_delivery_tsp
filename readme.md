An implementation of the pick up and delivery traveling salesman problem with and without time-windows. 

For both problems, I used a tabu search/hill climbing technique as an optimization method. I refrained from implementing the problem as an Integer Programming problem due to my lack of knowledge/experience with implementing
this in Python and access to a good solver (Gurobi, CPLEX, etc.). Another choice is that in practice an IP model is not feasible due to the immense problem size. My choice for a tabu search is of a pragmatic reason: 
I have implemented this algorithm more than once and I know how it works. I also experimented with implementing a genetic algorithms but the  paper "The single vehicle pickup and delivery problem with time windows: 
intelligent operators for heuristic" by Hosny and Mumford (2008) (https://link.springer.com/content/pdf/10.1007%2Fs10732-008-9083-1.pdf) showed that a hill climbing algorithm produced usually better results. 

My tabu search implementation uses a basic hill climbing procedure that starts with a random initialized route. This route initialization is done by generating a pool of solutions and selecting the best 
one (i.e. one with lowest cost). This initial route almost always contains infeasibilities. 
I refrained from putting in too much work in generating an initial feasible solution as I view this as the task of the optimizing algorithm. 

Given an initial route, the hill climbing method is initiated that is run for a certain number of iterations (range 10-30). The best solution out of these number of iterations is then accepted as the best possible route. 
The hill climbing algorithm executes a simple local search algorith that employs two simple route altering procedures: 2-opt and random position swap. The procedure is chosen at random with both having an equal change of being chosen.
Implementing both and having the algorithm choose one at random seemed to produce consistently better result than implementing only one. The local search works by forming all possible pairs between nodes in the tour. It then checks
for each pair whether doing a two-opt swap or a position swap breeds a better solution, and if it does it accepts it as the current best solution. The solution returned at the end is the best out of x number of iteration the algorithm has run.

The algorithm could be further improved by different tabu list implementations.

Problem 1:
For this problem, analogous with the standard TSP, I have created a tour that is a closed loop and visits each location exactly once. The loop starts and ends with the driver's location.
The shortest distance I found is 23.94 KM. 

Problem 2:
For this problem, I relaxed the condition that a store can be visited only once. I did this because, the data showed that the time window for each pick-up corresponded with the time window of the corresponding delivery. Meaning,
some pick-ups, even though they are to be picked-up from the same store, can only be picked up at different times. Though unlikely, it is not unthinkable that given the scoring function the driver picks up one delivery first
and picks another up later. As in problem 1, I also considered that the driver needs to drive back to the depot.

The lowest score I found for this problem was 37454668 seconds. The square root value for this 6120 seconds, which is 102 minutes. So, the total wait time for all customers in this result is 102 minutes. 

Lastly, I have run the algorthm multiple times, the scoring I have saved in solution_statistics.csv in the same folder as the solutions for the problem.

