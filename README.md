# 20-second-swarm-intelligence
entry to 20 second game jam (if i get it finished in time lol ( edit: i didnt) )

alright, this is just a lil swarm intelligence implemented after the example of Evolve 1.0
i tried to do my own Sweep and Prune algorithm for calculating neighbours but i'm not shure if its strickly correct. it does work though so ¯\_(ツ)_/¯

Evolve 1.0 calculates the velocity vectors as a weightes sum of these:
 v_1: points away from neighbors in vicinity
 v_2: points to world center
 v_3: mean vector of neighbours
 v_4: points to center of weight of all agents
 v_5: random vector
 v_6: points away from neighbours of different species
 v_7: points to energy source
 
you can ajust the weights of these vectors and observe how the swarm behaves differently. 
here is an example with two species:

https://user-images.githubusercontent.com/75081082/206029556-b07b14ae-06f8-4e8c-be93-a9da82c18c33.mp4


I'm planning on 1) redoing this in Unity bc I know how to do a good user interface there (and this code has become a bit of a mess)
and 2) implement an evolutionary algorithm to adjust the weights
