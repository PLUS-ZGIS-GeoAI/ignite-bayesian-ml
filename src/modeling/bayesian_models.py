import pandas as pd
import pymc as pm


def create_blr_partial_pooling_for_ffmc_adjustment(X: pd.DataFrame,
                                                   y: pd.Series,
                                                   coords: dict) -> pm.Model:
    """Generates a probabilitstic bayesian logistic regression model, specifically for the FFMC adjustment use-case

    Args:
        X (pd.DataFrame): features
        y (pd.Series): labels
        coords (dict): contains unique values of grouping variables (values) and key name is used to access to values 

    Returns:
        pm.Model: bayesian model, which can be used for analysis and prediction
    """

    with pm.Model(coords=coords) as model:

        aspect_groups_idx = pm.MutableData("aspect_groups_idx", X["aspect"])
        treetype_groups_idx = pm.MutableData(
            "foresttype_groups_idx", X["foresttype"])

        ffmc = pm.MutableData('ffmc', X.ffmc)
        fire_labels = pm.MutableData('fire', y)

        # Hyperpriors of features
        mu_b1, sigma_b1 = pm.Normal(
            "mu_b1", mu=0.0, sigma=1.0), pm.Exponential("sigma_b1", 1)

        # specify priors for the features
        intercept = pm.Normal('intercept', 0, 1)
        beta_ffmc = pm.Normal('beta_ffmc', mu_b1, sigma_b1,
                              dims=("aspect_groups", "foresttype_groups"))
        error_var = pm.Normal("error_beta", 0, 1)

        # Transform random variables into vector of probabilities p(y_i=1)
        # according to logistic regression model specification.
        mean = intercept + \
            beta_ffmc[aspect_groups_idx, treetype_groups_idx] * ffmc + \
            error_var
        p = pm.Deterministic('p', pm.math.invlogit(mean))

        # Bernoulli random vector with probability of fire = 1
        # given by sigmoid function and actual data as observed
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model
