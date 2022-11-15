"""
Play matches between 2 trained models and see how they compare to each other.
This code produces a matrix of matches between all fully trained nets.

Pairs played are: all combinations sharing a copy number, and all combinations sharing a size number.

Change all paths to the desired paths.
"""

from absl import app
import numpy as np
from itertools import combinations
import os
from shutil import copyfile
from open_spiel.python.utils import spawn
import AZ_helper_lib as AZh
import utils

# Specify the game:
game = 'pentago'

# Save all logs to:
path_logs = '/path/to/logs/directory/' + game + '/'
# Create the directory, then copy a config.json file into it: (otherwise crashes)
if not os.path.exists(path_logs):
    os.makedirs(path_logs)
    copyfile('./config.json', path_logs + '/config.json')


def mat2str(matrix):
    return np.array2string(matrix, separator=',', max_line_width=np.inf)


def set_config(model_1, model_2):
    path_model_1 = './models/' + game + '/' + model_1 + '/'
    path_model_2 = './models/' + game + '/' + model_2 + '/'

    config = AZh.Config(
        game=game,
        MC_matches=False,
        path=path_logs,
        path_model_1=path_model_1,
        path_model_2=path_model_2,
        checkpoint_number_1=None,
        checkpoint_number_2=None,
        use_solver=False,
        use_two_solvers=False,
        solver_1_temp=None,
        solver_2_temp=None,
        logfile='matches',
        learning_rate=0,
        weight_decay=0,

        temperature=0.25,
        evaluators=80,
        uct_c=2,
        max_simulations=300,
        policy_alpha=0.5,
        evaluation_games=10,
        evaluation_window=10,

        nn_model=None,
        nn_width=None,
        nn_depth=None,
        observation_shape=None,
        output_size=None,

        quiet=True,
    )
    return config


def main(unused_argv):
    # Choose which models to load. 'use_f_models' should be set to False
    # if there are no 'f' models trained, for example for Pentago.
    use_f_models = False
    max_q = 6
    min_f = 0
    max_f = 6
    n_copies = 6
    nets = []
    # Enumerate all models. The order is: First by size, then by copy number.
    for i in range(max_q + 1):
        for j in range(n_copies):
            nets.append('q_' + str(i) + '_' + str(j))

        if (min_f <= i <= max_f) and use_f_models:
            for j in range(n_copies):
                nets.append('f_' + str(i) + '_' + str(j))

    n = len(nets)
    matches = np.zeros([n, n])
    timer = utils.Timer()
    timer.go()

    for pair in combinations(range(n), 2):  # Loop over pairs of nets
        net_1 = nets[pair[0]]
        net_2 = nets[pair[1]]
        config = set_config(net_1, net_2)
        AZh.run_matches(config)
        n_evaluators = config.evaluators
        score = 0
        for ev in range(n_evaluators):
            with open(config.path + 'log-' + config.logfile + '-' + str(ev) + '.txt') as f:
                lines = f.readlines()
            score += float(lines[-2][-7:-2])
        score = score / n_evaluators
        matches[pair] += (float(score) + 1) / 2
    timer.stop()

    # Calculate the mean matrix (averaging over copies with same sizes):
    m = int(len(matches[0, :]) / n_copies)
    mean_mat = np.zeros([m, m])
    for i in range(m):
        for j in range(m):
            x = i * n_copies
            y = j * n_copies
            mat = matches[x:x + n_copies, y:y + n_copies]
            if i == j:
                continue
            mean_mat[i, j] = mat.mean()

    matches = matches + np.tril(np.ones([n, n]) - matches.transpose(), -1)
    print('Matches matrix: ', matches)
    mean_mat = mean_mat + np.tril(np.ones([m, m]) - mean_mat.transpose(), -1)
    print('Averaged matches matrix: ', mean_mat)

    # Save matrix to file.
    with open(path_logs + "/matrix.npy", 'wb') as f:
        np.save(f, matches)
    with open(path_logs + "/mean_matrix.txt", "w") as f:
        f.write(mat2str(mean_mat))


if __name__ == "__main__":
    with spawn.main_handler():
        app.run(main)
