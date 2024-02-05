import pandas as pd
import pymc as pm


'''
Bayesian Logistic Regression with full pooling:
That means the full data is used to estimate the coefficients for  the whole area (no subgrouping)
'''


def create_blr_full_pooling(X: pd.DataFrame,
                            y: pd.Series,
                            coords: dict) -> pm.Model:
    """Normal Bayesian Logistic Regression Model, with categorized variables and uniform priors"""

    with pm.Model(coords=coords) as log_reg:

        # create data containers for all the features
        exposition = pm.MutableData('exposition', X.exposition)
        tree_type = pm.MutableData('tree_type', X.tree_type)
        canopy_closure = pm.MutableData('canopy_closure', X.canopy_closure)
        ffmc = pm.MutableData('ffmc', X.ffmc)
        fire_labels = pm.MutableData('fire', y)

        # specify priors for the features
        intercept = pm.Normal('intercept', 0, 1)
        beta_1 = pm.Normal('beta_expo', 0, 1, dims="exposition")
        beta_2 = pm.Normal('beta_tree', 0, 1, dims="tree_type")
        beta_3 = pm.Normal('beta_canopy', 0, 1, dims="canopy_closure")
        beta_4 = pm.Normal('beta_ffmc', 0, 1)
        error_var = pm.Normal("error_beta", 0, 1)

        #  Logistic Regression
        mean = intercept + \
            beta_1[exposition] + \
            beta_2[tree_type] + \
            beta_3[canopy_closure] + \
            beta_4 * ffmc + \
            error_var

        p = pm.Deterministic('p', pm.math.invlogit(mean))
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return log_reg


'''
Bayesian logistic regression with partial pooling (spatial subgroups):
The model estimates the coefficients per spatial subgroup and for the full population. 
Each subgroup is informed by the "full population"-estimates.
E.g. if there is no data for a subgroup - the coefficient will be the full population mean. 
If there is much data, the subgroup will have the same value are in the no pooling version. (Coefficient is only estimated based on group data)
'''


def create_blr_partial_pooling_spatial(X: pd.DataFrame,
                                       y: pd.Series,
                                       coords: dict,
                                       spatial_grouping_variable: str) -> pm.Model:

    with pm.Model(coords=coords) as model:

        # create data containers for all the features
        exposition = pm.MutableData('exposition', X.exposition)
        tree_type = pm.MutableData('tree_type', X.tree_type)
        canopy_closure = pm.MutableData('canopy_closure', X.canopy_closure)
        ffmc = pm.MutableData('ffmc', X.ffmc)
        fire_labels = pm.MutableData('fire', y)
        spatial_groups_idx = pm.MutableData(
            "spatial_groups_idx", X[spatial_grouping_variable])

        # Hyperpriors of features
        mu_b1, sigma_b1 = pm.Normal(
            "mu_b1", mu=0.0, sigma=1.0), pm.Exponential("sigma_b1", 1)
        mu_b2, sigma_b2 = pm.Normal(
            "mu_b2", mu=0.0, sigma=1.0), pm.Exponential("sigma_b2", 1)
        mu_b3, sigma_b3 = pm.Normal(
            "mu_b3", mu=0.0, sigma=1.0), pm.Exponential("sigma_b3", 1)
        mu_b4, sigma_b4 = pm.Normal(
            "mu_b4", mu=0.0, sigma=1.0), pm.Exponential("sigma_b4", 1)

        # specify priors for the features
        intercept = pm.Normal('intercept', 0, 1)
        beta_1 = pm.Normal('beta_expo', mu_b1, sigma_b1,
                           dims=("exposition", "spatial_groups"))
        beta_2 = pm.Normal('beta_tree', mu_b2, sigma_b2,
                           dims=("tree_type", "spatial_groups"))
        beta_3 = pm.Normal('beta_canopy', mu_b3, sigma_b3,
                           dims=("canopy_closure", "spatial_groups"))
        beta_4 = pm.Normal('beta_ffmc', mu_b4, sigma_b4, dims="spatial_groups")
        error_var = pm.Normal("error_beta", 0, 1)

        # Transform random variables into vector of probabilities p(y_i=1)
        # according to logistic regression model specification.
        mean = intercept + \
            beta_1[exposition, spatial_groups_idx] + \
            beta_2[tree_type, spatial_groups_idx] + \
            beta_3[canopy_closure, spatial_groups_idx] + \
            beta_4[spatial_groups_idx] * ffmc + \
            error_var
        p = pm.Deterministic('p', pm.math.invlogit(mean))

        # Bernoulli random vector with probability of fire = 1
        # given by sigmoid function and actual data as observed
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model


'''
Bayesian Logistic Regression with partial pooling (temporal and spatial groups):
Basically, the same as above but instead of grouping data by spatial location alone, the data is also grouped by time (e.g. season)
This means we get temporal groups x spatial groups subgroups. For each of the subgroups the feature coefficients are estimated. 
'''


def create_blr_partial_pooling_spatiotemporal(X: pd.DataFrame,
                                              y: pd.Series,
                                              coords: dict,
                                              spatial_grouping_variable: str,
                                              temporal_grouping_variable: str) -> pm.Model:
    """create a hierachical bayesian logistic regression model, that groups the data by space and time and partially pools information --> we get different models for all groups, but each model is informed by the full data, not just the group data"""

    with pm.Model(coords=coords) as model:

        # create data containers for all the features
        exposition = pm.MutableData('exposition', X.exposition)
        tree_type = pm.MutableData('tree_type', X.tree_type)
        canopy_closure = pm.MutableData('canopy_closure', X.canopy_closure)
        ffmc = pm.MutableData('ffmc', X.ffmc)
        fire_labels = pm.MutableData('fire', y)
        spatial_groups_idx = pm.MutableData(
            "spatial_groups_idx", X[spatial_grouping_variable])
        temporal_groups_idx = pm.MutableData(
            "temporal_groups_idx", X[temporal_grouping_variable])

        # Hyperpriors of features
        mu_b1, sigma_b1 = pm.Normal(
            "mu_b1", mu=0.0, sigma=1.0), pm.Exponential("sigma_b1", 1)
        mu_b2, sigma_b2 = pm.Normal(
            "mu_b2", mu=0.0, sigma=1.0), pm.Exponential("sigma_b2", 1)
        mu_b3, sigma_b3 = pm.Normal(
            "mu_b3", mu=0.0, sigma=1.0), pm.Exponential("sigma_b3", 1)
        mu_b4, sigma_b4 = pm.Normal(
            "mu_b4", mu=0.0, sigma=1.0), pm.Exponential("sigma_b4", 1)

        # specify priors for the features
        intercept = pm.Normal('intercept', 0, 1)
        beta_1 = pm.Normal('beta_expo', mu_b1, sigma_b1,
                           dims=("exposition", "spatial_groups", "temporal_groups"))
        beta_2 = pm.Normal('beta_tree', mu_b2, sigma_b2,
                           dims=("tree_type", "spatial_groups", "temporal_groups"))
        beta_3 = pm.Normal('beta_canopy', mu_b3, sigma_b3,
                           dims=("canopy_closure", "spatial_groups", "temporal_groups"))
        beta_4 = pm.Normal('beta_ffmc', mu_b4, sigma_b4,
                           dims=("spatial_groups", "temporal_groups"))
        error_var = pm.Normal("error_beta", 0, 1)

        # Transform random variables into vector of probabilities p(y_i=1)
        # according to logistic regression model specification.
        mean = intercept + \
            beta_1[exposition, spatial_groups_idx, temporal_groups_idx] + \
            beta_2[tree_type, spatial_groups_idx, temporal_groups_idx] + \
            beta_3[canopy_closure, spatial_groups_idx, temporal_groups_idx] + \
            beta_4[spatial_groups_idx, temporal_groups_idx] * ffmc + \
            error_var
        p = pm.Deterministic('p', pm.math.invlogit(mean))

        # Bernoulli random vector with probability of fire = 1
        # given by sigmoid function and actual data as observed
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model


'''
Bayesian Logistic Regression with no pooling spatio temporal
Same as above, but without pooling. Coefficients for each subgroup are estimated by using the data from the subgroup alone
'''


def create_blr_no_pooling_spatiotemporal(X: pd.DataFrame,
                                         y: pd.Series,
                                         coords: dict,
                                         spatial_grouping_variable: str,
                                         temporal_grouping_variable: str):
    """Creating a hierachical model that groups the data into spatial and temporal groups and creates an individual model for each group. The information of the full data is not shared between groups"""

    with pm.Model(coords=coords) as model:

        # create data containers for all the features
        exposition = pm.MutableData('exposition', X.exposition)
        tree_type = pm.MutableData('tree_type', X.tree_type)
        canopy_closure = pm.MutableData('canopy_closure', X.canopy_closure)
        ffmc = pm.MutableData('ffmc', X.ffmc)
        fire_labels = pm.MutableData('fire', y)
        spatial_groups_idx = pm.MutableData(
            "spatial_groups_idx", X[spatial_grouping_variable])
        temporal_groups_idx = pm.MutableData(
            "temporal_groups_idx", X[temporal_grouping_variable])

        # specify priors for the features
        intercept = pm.Normal('intercept', 0, 1)
        beta_1 = pm.Normal('beta_expo', 0, 1,
                           dims=("exposition", "spatial_groups", "temporal_groups"))
        beta_2 = pm.Normal('beta_tree', 0, 1,
                           dims=("tree_type", "spatial_groups", "temporal_groups"))
        beta_3 = pm.Normal('beta_canopy', 0, 1,
                           dims=("canopy_closure", "spatial_groups", "temporal_groups"))
        beta_4 = pm.Normal('beta_ffmc', 0, 1,
                           dims=("spatial_groups", "temporal_groups"))
        error_var = pm.Normal("error_beta", 0, 1)

        # Transform random variables into vector of probabilities p(y_i=1)
        # according to logistic regression model specification.
        mean = intercept + \
            beta_1[exposition, spatial_groups_idx, temporal_groups_idx] + \
            beta_2[tree_type, spatial_groups_idx, temporal_groups_idx] + \
            beta_3[canopy_closure, spatial_groups_idx, temporal_groups_idx] + \
            beta_4[spatial_groups_idx, temporal_groups_idx] * ffmc + \
            error_var
        p = pm.Deterministic('p', pm.math.invlogit(mean))

        # Bernoulli random vector with probability of fire = 1
        # given by sigmoid function and actual data as observed
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model
