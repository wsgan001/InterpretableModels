import datetime
import argparse

import numpy as np

import models
import stability
import datamanager
import preprocessing as prep

import warnings
warnings.filterwarnings("ignore")


fit_predict_model = {
    ('DT', 'sklearn'): models.fit_predict_sklearn_decision_tree,
    ('LM', 'linear_regression'): models.fit_predict_linear_regression,
    ('LM', 'lasso'): models.fit_predict_lasso,
    ('LM', 'ridge'): models.fit_predict_ridge,
}

analyze_model = {
    ('DT', 'sklearn'): models.analyze_sklearn_decision_tree,
    ('LM', 'linear_regression'): models.analyze_sklearn_linear_models,
    ('LM', 'lasso'): models.analyze_sklearn_linear_models,
    ('LM', 'ridge'): models.analyze_sklearn_linear_models,
}

compare_models = {
    ('DT', 'sklearn'): models.compare_sklearn_decision_trees,
    ('LM', 'linear_regression'): models.compare_sklearn_linear_models,
    ('LM', 'lasso'): models.compare_sklearn_linear_models,
    ('LM', 'ridge'): models.compare_sklearn_linear_models,
}

aggregation_functions = {
    'mean': np.mean,
    'std': np.std,
    'median': np.median,
}


def set_argparser():
    parser = argparse.ArgumentParser(description='Evaluate interpretable models stability.')
    parser.add_argument('-d', dest='dataset_name', help='Dataset name')
    parser.add_argument('-m', dest='model_name', help='Model name')
    parser.add_argument('-dp', dest='datasets_path', help='Datasets path', default='')
    parser.add_argument('-mp', dest='models_path', help='Models path', default='')
    parser.add_argument('-rp', dest='results_path', help='Results path', default='')
    parser.add_argument('-s', dest='nbr_splits', help='Number of splits', default=10, type=int)
    parser.add_argument('-i', dest='nbr_iter', help='Number of iterations', default=5, type=int)
    parser.add_argument('-l', dest='load_model', help='Load model', default=False, action='store_true')
    parser.add_argument('-g', dest='log', help='Show log', default=False, action='store_true')
    parser.add_argument('-sd', dest='sd', help='Show available datasets', default=False, action='store_true')
    parser.add_argument('-sm', dest='sm', help='Show available models', default=False, action='store_true')

    return parser


def run_evaluate_stability(dataset_name, model_name, datasets_path='', models_path='', results_path='',
                           nbr_splits=10, nbr_iter=5, load_model=False, log=False):

    # nbr_splits = 10
    # nbr_iter = 5
    # load_model = False
    # log = False

    if log:
        print(datetime.datetime.now(), 'Loading %s dataset' % dataset_name)
    X, y = datamanager.get_dataset(dataset_name, datasets_path)

    if log:
        print(datetime.datetime.now(), 'Building preprocessing pipe')
    preprocessing_pipe = prep.build_preprocessing_pipe()[:5]

    if not load_model:
        if log:
            nbr_models = nbr_splits * nbr_iter * len(preprocessing_pipe)
            print(datetime.datetime.now(), 'Training and testing %d models' % nbr_models)
        trained_model = stability.train_model(X, y, model_name, preprocessing_pipe, fit_predict_model,
                                              nbr_splits, nbr_iter)

        if log:
            print(datetime.datetime.now(), 'Storing models')
        stability.store_model(trained_model, model_name, dataset_name, models_path)
    else:
        if log:
            print(datetime.datetime.now(), 'loading models')
        trained_model = stability.load_model(model_name, dataset_name, models_path)

    if log:
        print(datetime.datetime.now(), 'Evaluating models stability')
    model_stability = stability.evaluate_model_stability(model_name, trained_model,
                                                         analyze_model, aggregation_functions)

    if log:
        print(datetime.datetime.now(), 'Evaluating and comparing models stability')
    model_stability_comparison = stability.evaluate_model_stability_comparison(model_name, trained_model,
                                                                               compare_models, aggregation_functions)

    if log:
        print(datetime.datetime.now(), 'Storing results')
    stability.store_model_stability(model_stability, model_stability_comparison, aggregation_functions,
                                    model_name, dataset_name, results_path)

    if log:
        print(datetime.datetime.now(), 'Evaluation completed')


def main():

    parser = set_argparser()
    args = parser.parse_args()

    if args.sd:
        for d in sorted(datamanager.datasets):
            print(d)
        return 0

    if args.sm:
        for m in sorted(fit_predict_model):
            print(m)
        return 0

    dataset_name = args.dataset_name
    model_name = eval(str(args.model_name))
    datasets_path = args.datasets_path
    models_path = args.models_path
    results_path = args.results_path

    if dataset_name is None or model_name is None:
        print(parser.print_help())
        return 1

    nbr_splits = args.nbr_splits
    nbr_iter = args.nbr_iter
    load_model = args.load_model
    log = args.log

    run_evaluate_stability(dataset_name, model_name, datasets_path, models_path, results_path,
                           nbr_splits, nbr_iter, load_model, log)

    #print(models.brackets_repository.keys())


if __name__ == "__main__":
    main()
