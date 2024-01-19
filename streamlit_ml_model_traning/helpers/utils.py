import pandas as pd
from sklearn.metrics import median_absolute_error


def print_dataframe(filtered_cv_results):
    """Pretty print for filtered dataframe"""
    for mean_r2, std_r2, mean_negmedae, std_negmedae, params in zip(
        filtered_cv_results["mean_test_R2"],
        filtered_cv_results["std_test_R2"],
        filtered_cv_results["mean_test_negMedAE"],
        filtered_cv_results["std_test_negMedAE"],
        filtered_cv_results["params"],
    ):
        print(
            f"R2: {mean_r2:0.3f} (±{std_r2:0.03f}),"
            f" negMedAE: {mean_negmedae:0.3f} (±{std_negmedae:0.03f}),"
            f" for {params}"
        )
    print()

def refit_strategy(cv_results):
    """Define the strategy to select the best estimator.

    The strategy defined here is to identify the best R2,
    set the R2 threshold at 0.1 below that,
    and filter-out all results below that.
    Then rank the remaining by MedAE and keep best one.

    Parameters
    ----------
    cv_results : dict of numpy (masked) ndarrays
        CV results as returned by the `GridSearchCV`.

    Returns
    -------
    best_index : int
        The index of the best estimator as it appears in `cv_results`.
    """
    
    cv_results_ = pd.DataFrame(cv_results)
    print("All grid-search results:")
    print_dataframe(cv_results_)

    # get the top 10 % or the top 3 by R2
    high_r2_cv_results = cv_results_.loc[cv_results_["mean_test_R2"].isin(cv_results_["mean_test_R2"].nlargest(n=max(int(len(cv_results_) / 10), 3)))]

    print(f"Models in the top 10% by R2:")
    print_dataframe(high_r2_cv_results)

    high_r2_cv_results = high_r2_cv_results[
        [
            "mean_score_time",
            "mean_test_R2",
            "std_test_R2",
            "mean_test_negMedAE",
            "std_test_negMedAE",
            "rank_test_R2",
            "rank_test_negMedAE",
            "params",
        ]
    ]

    # Select the most performant models in terms of negMedAE
    best_negmedae_high_r2_index = high_r2_cv_results["mean_test_negMedAE"].idxmax()

    
    print(
        "\nThe selected final model is the best negMedAE out of the previously\n"
        "selected subset of best models based on R2\n"
        "Its details are:\n\n"
        f"{high_r2_cv_results.loc[best_negmedae_high_r2_index]}"
    )

    return best_negmedae_high_r2_index

def neg_median_absolute_error(y_true, y_pred):
    medae = median_absolute_error(y_true, y_pred)
    return -medae