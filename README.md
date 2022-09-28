# AlphaZero-Scaling
Code and data for 'Scaling Laws for a Multi-Agent Reinforcement Learning Model'.

## Prerequisites
The code was run with Python (version 3.6.8) using open-spiel (version 1.0.0) tensorflow (version 2.6.0).

In order to run Connect Four matches against a solver, you must download the open source solver package seperately. See `solver_bot.py` documentation for detailed instructions.

In order to calculate Elo scores, you must download the open source program [BayesElo](https://www.remi-coulom.fr/Bayesian-Elo/).

## Code overview
`train_models.py` is the starting point. This code can be used to train AlphaZero agents with the same hyperparameters used in the paper.

There are two main codes needed to generate the match data required in order to calculate the Elo scores of all agents:
- `matches_fixed_checkpoint.py` is used to run matches on a training slice, running games between all pairs of agents trained for a specified number of training steps.
- `matches_self_checkpoint.py` is used to run matches on an agent slice, running games between all pairs of checkpoints of a single agent.

The Elo scores presented in the paper can be replicated by running matches on all training slices and all agent slices, then feeding all match results to BayesElo. We matched every player pair for 800 games.

## Data
All models trained on Connect Four and Pentago are available in an individual release.
Each agent folder contains all checkpoints used to generate the plots in the paper.
