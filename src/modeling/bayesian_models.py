import pandas as pd
import pymc as pm
import numpy as np


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

    with pm.Model(coords=coords) as model:  # type: ignore

        aspect_groups_idx = pm.MutableData("aspect_groups_idx", X["aspect"])
        treetype_groups_idx = pm.MutableData(
            "foresttype_groups_idx", X["foresttype"])

        ffmc = pm.MutableData('ffmc', X.ffmc)
        fire_labels = pm.MutableData('fire', y)

        # Hyperpriors of features
        mu_b1, sigma_b1 = pm.Cauchy(
            "mu_b1", mu=0.0, sigma=1.0), pm.Exponential("sigma_b1", 1)

        # specify priors for the features
        intercept = pm.Cauchy('intercept', 0, 1)
        beta_ffmc = pm.Cauchy('beta_ffmc', mu_b1, sigma_b1,
                              dims=("aspect_groups", "foresttype_groups"))
        error_var = pm.Cauchy("error_beta", 0, 1)

        # Transform random variables into vector of probabilities p(y_i=1)
        # according to logistic regression model specification.
        mean = intercept + \
            beta_ffmc[aspect_groups_idx, treetype_groups_idx] * ffmc + \
            error_var
        p = pm.Deterministic('p', pm.math.invlogit(mean))  # type: ignore

        # Bernoulli random vector with probability of fire = 1
        # given by sigmoid function and actual data as observed
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model


def create_st_blr(X: pd.DataFrame,
                  y: pd.Series,
                  coords: dict,
                  spatial_grouping_variable: str,
                  temporal_grouping_variable: str) -> pm.Model:
    """function creates bayesian logistic regression with spatio-temporal subgroups for uncertainty quantification paper
    Args:
        X (pd.DataFrame): features
        y (pd.Series): labels
        coord (dict): key is name of grouping variable or categorical feature and values are unique classes
    Returns:
        pm.Model: bayesian model, which can be used for analysis and prediction
    """

    with pm.Model(coords=coords) as model:  # type: ignore

        # data containers
        elevation = pm.MutableData("elevation", X.elevation)
        slope = pm.MutableData("slope", X.slope)
        aspect = pm.MutableData("aspect", X.aspect_encoded)
        forestroad_density = pm.MutableData(
            "forestroad_density", X.forestroad_density)
        railway_density = pm.MutableData("railway_density", X.railway_density)
        hikingtrail_density = pm.MutableData(
            "hikingtrail_density", X.hikingtrail_density)
        farmyard_density = pm.MutableData(
            "farmyard_density", X.farmyard_density)
        population = pm.MutableData("population", X.population_density)
        forest_type = pm.MutableData("forest_type", X.forest_type)
        ffmc = pm.MutableData("ffmc", X.ffmc)
        fire_labels = pm.MutableData("fire", y)
        spatial_groups_idx = pm.MutableData(
            "spatial_groups_idx", X[spatial_grouping_variable])
        temporal_groups_idx = pm.MutableData(
            "temporal_groups_idx", X[temporal_grouping_variable])

        # Hyperpriors of features
        mu_b1, sigma_b1 = pm.Cauchy(
            "mu_b1", 0.0, 1.0), pm.Exponential("sigma_b1", 1)
        mu_b2, sigma_b2 = pm.Cauchy(
            "mu_b2", 0.0, 1.0), pm.Exponential("sigma_b2", 1)
        mu_b3, sigma_b3 = pm.Cauchy(
            "mu_b3", 0.0, 1.0), pm.Exponential("sigma_b3", 1)
        mu_b4, sigma_b4 = pm.Cauchy(
            "mu_b4", 0.0, 1.0), pm.Exponential("sigma_b4", 1)
        mu_b5, sigma_b5 = pm.Cauchy(
            "mu_b5", 0.0, 1.0), pm.Exponential("sigma_b5", 1)
        mu_b6, sigma_b6 = pm.Cauchy(
            "mu_b6", 0.0, 1.0), pm.Exponential("sigma_b6", 1)
        mu_b7, sigma_b7 = pm.Cauchy(
            "mu_b7", 0.0, 1.0), pm.Exponential("sigma_b7", 1)
        mu_b8, sigma_b8 = pm.Cauchy(
            "mu_b8", 0.0, 1.0), pm.Exponential("sigma_b8", 1)
        mu_b9, sigma_b9 = pm.Cauchy(
            "mu_b9", 0.0, 1.0), pm.Exponential("sigma_b9", 1)
        mu_b10, sigma_b10 = pm.Cauchy(
            "mu_b10", 0.0, 1.0), pm.Exponential("sigma_b10", 1)

        # specify priors for the features
        intercept = pm.Cauchy('intercept', 0, 1)
        beta_elevation = pm.Cauchy('beta_elevation', mu_b1, sigma_b1,
                                   dims=("spatial_groups", "temporal_groups"))
        beta_slope = pm.Cauchy('beta_slope', mu_b2, sigma_b2, dims=(
            "spatial_groups", "temporal_groups"))
        beta_aspect = pm.Cauchy('beta_aspect', mu_b3, sigma_b3, dims=(
            "aspect_classes", "spatial_groups", "temporal_groups"))
        beta_forestroad_density = pm.Cauchy('beta_forestroad_density', mu_b4, sigma_b4, dims=(
            "spatial_groups", "temporal_groups"))
        beta_railway_density = pm.Cauchy('beta_railway_density', mu_b5, sigma_b5, dims=(
            "spatial_groups", "temporal_groups"))
        beta_hikingtrail_density = pm.Cauchy('beta_hikingtrail_density', mu_b6, sigma_b6, dims=(
            "spatial_groups", "temporal_groups"))
        beta_farmyard_density = pm.Cauchy('beta_farmyard_density', mu_b7, sigma_b7, dims=(
            "spatial_groups", "temporal_groups"))
        beta_population = pm.Cauchy('beta_population', mu_b8, sigma_b8, dims=(
            "spatial_groups", "temporal_groups"))
        beta_forest_type = pm.Cauchy('beta_forest_type', mu_b9, sigma_b9, dims=(
            "forest_type_classes", "spatial_groups", "temporal_groups"))
        beta_ffmc = pm.Cauchy('beta_ffmc', mu_b10, sigma_b10, dims=(
            "spatial_groups", "temporal_groups"))
        error_var = pm.Cauchy("error_beta", 0, 1)

        mean = intercept + \
            beta_elevation[spatial_groups_idx, temporal_groups_idx] * elevation + \
            beta_slope[spatial_groups_idx, temporal_groups_idx] * slope + \
            beta_aspect[aspect, spatial_groups_idx, temporal_groups_idx] + \
            beta_forestroad_density[spatial_groups_idx, temporal_groups_idx] * forestroad_density + \
            beta_railway_density[spatial_groups_idx, temporal_groups_idx] * railway_density + \
            beta_hikingtrail_density[spatial_groups_idx, temporal_groups_idx] * hikingtrail_density + \
            beta_farmyard_density[spatial_groups_idx, temporal_groups_idx] * farmyard_density + \
            beta_population[spatial_groups_idx, temporal_groups_idx] * population + \
            beta_forest_type[forest_type, spatial_groups_idx, temporal_groups_idx] + \
            beta_ffmc[spatial_groups_idx, temporal_groups_idx] * ffmc + \
            error_var

        p = pm.Deterministic('p', pm.math.invlogit(mean))  # type: ignore
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model


def create_st_blr_v2(X: pd.DataFrame,
                     y: pd.Series,
                     coords: dict,
                     spatial_grouping_variable: str,
                     temporal_grouping_variable: str) -> pm.Model:

    with pm.Model(coords=coords) as model:  # type: ignore

        # data containers
        elevation = pm.MutableData("elevation", X.elevation_encoded)
        slope = pm.MutableData("slope", X.slope_encoded)
        aspect = pm.MutableData("aspect", X.aspect_encoded)
        forestroad_density = pm.MutableData(
            "forestroad_density", X.forestroad_density_bin)
        railway_density = pm.MutableData("railway_density", X.railway_density_bin)
        hikingtrail_density = pm.MutableData(
            "hikingtrail_density", X.hikingtrail_density_bin)
        farmyard_density = pm.MutableData(
            "farmyard_density", X.farmyard_density_bin)
        population = pm.MutableData("population", X.population_encoded)
        forest_type = pm.MutableData("forest_type", X.forest_type)
        ffmc = pm.MutableData("ffmc", X.ffmc)
        fire_labels = pm.MutableData("fire", y)
        spatial_groups_idx = pm.MutableData(
            "spatial_groups_idx", X[spatial_grouping_variable])
        temporal_groups_idx = pm.MutableData(
            "temporal_groups_idx", X[temporal_grouping_variable])

        # Hyperpriors of features
        mu_b1, sigma_b1 = pm.Cauchy(
            "mu_b1", 0.0, 1.0), pm.Exponential("sigma_b1", 1)
        mu_b2, sigma_b2 = pm.Cauchy(
            "mu_b2", 0.0, 1.0), pm.Exponential("sigma_b2", 1)
        mu_b3, sigma_b3 = pm.Cauchy(
            "mu_b3", 0.0, 1.0), pm.Exponential("sigma_b3", 1)
        mu_b4, sigma_b4 = pm.Cauchy(
            "mu_b4", 0.0, 1.0), pm.Exponential("sigma_b4", 1)
        mu_b5, sigma_b5 = pm.Cauchy(
            "mu_b5", 0.0, 1.0), pm.Exponential("sigma_b5", 1)
        mu_b6, sigma_b6 = pm.Cauchy(
            "mu_b6", 0.0, 1.0), pm.Exponential("sigma_b6", 1)
        mu_b7, sigma_b7 = pm.Cauchy(
            "mu_b7", 0.0, 1.0), pm.Exponential("sigma_b7", 1)
        mu_b8, sigma_b8 = pm.Cauchy(
            "mu_b8", 0.0, 1.0), pm.Exponential("sigma_b8", 1)
        mu_b9, sigma_b9 = pm.Cauchy(
            "mu_b9", 0.0, 1.0), pm.Exponential("sigma_b9", 1)
        mu_b10, sigma_b10 = pm.Cauchy(
            "mu_b10", 0.0, 1.0), pm.Exponential("sigma_b10", 1)

        # specify priors for the features
        intercept = pm.Cauchy('intercept', 0, 1)
        beta_elevation = pm.Cauchy('beta_elevation', mu_b1, sigma_b1, dims=("elevation_classes", "spatial_groups", "temporal_groups"))
        beta_slope = pm.Cauchy('beta_slope', mu_b2, sigma_b2, dims=("slope_classes", "spatial_groups", "temporal_groups"))
        beta_aspect = pm.Cauchy('beta_aspect', mu_b3, sigma_b3, dims=("aspect_classes", "spatial_groups", "temporal_groups"))
        beta_forestroad_density = pm.Cauchy('beta_forestroad_density', mu_b4, sigma_b4, dims=("forestroad_density_classes", "spatial_groups", "temporal_groups"))
        beta_railway_density = pm.Cauchy('beta_railway_density', mu_b5, sigma_b5, dims=("railway_density_classes", "spatial_groups", "temporal_groups"))
        beta_hikingtrail_density = pm.Cauchy('beta_hikingtrail_density', mu_b6, sigma_b6, dims=("hikingtrail_density_classes", "spatial_groups", "temporal_groups"))
        beta_farmyard_density = pm.Cauchy('beta_farmyard_density', mu_b7, sigma_b7, dims=("farmyard_density_classes", "spatial_groups", "temporal_groups"))
        beta_population = pm.Cauchy('beta_population', mu_b8, sigma_b8, dims=("population_classes", "spatial_groups", "temporal_groups"))
        beta_forest_type = pm.Cauchy('beta_forest_type', mu_b9, sigma_b9, dims=("forest_type_classes", "spatial_groups", "temporal_groups"))
        beta_ffmc = pm.Cauchy('beta_ffmc', mu_b10, sigma_b10, dims=("spatial_groups", "temporal_groups"))
        error_var = pm.Cauchy("error_beta", 0, 1)

        mean = intercept + \
            beta_elevation[elevation, spatial_groups_idx, temporal_groups_idx] + \
            beta_slope[slope, spatial_groups_idx, temporal_groups_idx] + \
            beta_aspect[aspect, spatial_groups_idx, temporal_groups_idx] + \
            beta_forestroad_density[forestroad_density, spatial_groups_idx, temporal_groups_idx] + \
            beta_railway_density[railway_density, spatial_groups_idx, temporal_groups_idx] + \
            beta_hikingtrail_density[hikingtrail_density, spatial_groups_idx, temporal_groups_idx] + \
            beta_farmyard_density[farmyard_density, spatial_groups_idx, temporal_groups_idx] + \
            beta_population[population, spatial_groups_idx, temporal_groups_idx] + \
            beta_forest_type[forest_type, spatial_groups_idx, temporal_groups_idx] + \
            beta_ffmc[spatial_groups_idx, temporal_groups_idx] * ffmc + \
            error_var

        p = pm.Deterministic('p', pm.math.invlogit(mean))  # type: ignore
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model

def create_blr(X: pd.DataFrame,
               y: pd.Series,
               coords: dict) -> pm.Model:
    """function creates bayesian logistic regression for uncertainty quantification paper
    Args:
        X (pd.DataFrame): features
        y (pd.Series): labels
        coord (dict): key is name of grouping variable or categorical feature and values are unique classes
    Returns:
        pm.Model: bayesian model, which can be used for analysis and prediction
    """

    with pm.Model(coords=coords) as model:  # type: ignore

        # data containers
        elevation = pm.MutableData("elevation", X.elevation)
        slope = pm.MutableData("slope", X.slope)
        aspect = pm.MutableData("aspect", X.aspect_encoded)
        forestroad_density = pm.MutableData(
            "forestroad_density", X.forestroad_density)
        railway_density = pm.MutableData("railway_density", X.railway_density)
        hikingtrail_density = pm.MutableData(
            "hikingtrail_density", X.hikingtrail_density)
        farmyard_density = pm.MutableData(
            "farmyard_density", X.farmyard_density)
        population = pm.MutableData("population", X.population_density)
        forest_type = pm.MutableData("forest_type", X.forest_type)
        ffmc = pm.MutableData("ffmc", X.ffmc)
        fire_labels = pm.MutableData("fire", y)

        # specify priors for the features
        intercept = pm.Cauchy('intercept', 0, 1)
        beta_elevation = pm.Cauchy('beta_elevation', 0, 1)
        beta_slope = pm.Cauchy('beta_slope', 0, 1)
        beta_aspect = pm.Cauchy('beta_aspect', 0, 1, dims=("aspect_classes"))
        beta_forestroad_density = pm.Cauchy('beta_forestroad_density', 0, 1)
        beta_railway_density = pm.Cauchy('beta_railway_density', 0, 1)
        beta_hikingtrail_density = pm.Cauchy('beta_hikingtrail_density', 0, 1)
        beta_farmyard_density = pm.Cauchy('beta_farmyard_density', 0, 1)
        beta_population = pm.Cauchy('beta_population', 0, 1)
        beta_forest_type = pm.Cauchy(
            'beta_forest_type', 0, 1, dims=("forest_type_classes"))
        beta_ffmc = pm.Cauchy('beta_ffmc', 0, 1)
        error_var = pm.Cauchy("error_beta", 0, 1)

        mean = intercept + \
            beta_elevation * elevation + \
            beta_slope * slope + \
            beta_aspect[aspect] + \
            beta_forestroad_density * forestroad_density + \
            beta_railway_density * railway_density + \
            beta_hikingtrail_density * hikingtrail_density + \
            beta_farmyard_density * farmyard_density + \
            beta_population * population + \
            beta_forest_type[forest_type] + \
            beta_ffmc * ffmc + \
            error_var

        p = pm.Deterministic('p', pm.math.invlogit(mean))  # type: ignore
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model
    

def create_blr_v2(X: pd.DataFrame,
                  y: pd.Series,
                  coords: dict) -> pm.Model:

    with pm.Model(coords=coords) as model:  # type: ignore

        # data containers
        elevation = pm.MutableData("elevation", X.elevation_encoded)
        slope = pm.MutableData("slope", X.slope_encoded)
        aspect = pm.MutableData("aspect", X.aspect_encoded)
        forestroad_density = pm.MutableData(
            "forestroad_density", X.forestroad_density_bin)
        railway_density = pm.MutableData("railway_density", X.railway_density_bin)
        hikingtrail_density = pm.MutableData(
            "hikingtrail_density", X.hikingtrail_density_bin)
        farmyard_density = pm.MutableData(
            "farmyard_density", X.farmyard_density_bin)
        population = pm.MutableData("population", X.population_encoded)
        forest_type = pm.MutableData("forest_type", X.forest_type)
        ffmc = pm.MutableData("ffmc", X.ffmc)
        fire_labels = pm.MutableData("fire", y)

        # specify priors for the features
        intercept = pm.Cauchy('intercept', 0, 1)
        beta_elevation = pm.Cauchy('beta_elevation', 0, 1, dims=("elevation_classes"))
        beta_slope = pm.Cauchy('beta_slope', 0, 1, dims=("slope_classes"))
        beta_aspect = pm.Cauchy('beta_aspect', 0, 1, dims=("aspect_classes"))
        beta_forestroad_density = pm.Cauchy('beta_forestroad_density', 0, 1, dims=("forestroad_density_classes"))
        beta_railway_density = pm.Cauchy('beta_railway_density', 0, 1, dims=("railway_density_classes"))
        beta_hikingtrail_density = pm.Cauchy('beta_hikingtrail_density', 0, 1, dims=("hikingtrail_density_classes"))
        beta_farmyard_density = pm.Cauchy('beta_farmyard_density', 0, 1, dims=("farmyard_density_classes"))
        beta_population = pm.Cauchy('beta_population', 0, 1, dims=("population_classes"))
        beta_forest_type = pm.Cauchy('beta_forest_type', 0, 1, dims=("forest_type_classes"))
        beta_ffmc = pm.Cauchy('beta_ffmc', 0, 1)
        error_var = pm.Cauchy("error_beta", 0, 1)

        mean = intercept + \
            beta_elevation[elevation] + \
            beta_slope[slope] + \
            beta_aspect[aspect] + \
            beta_forestroad_density[forestroad_density] + \
            beta_railway_density[railway_density] + \
            beta_hikingtrail_density[hikingtrail_density] + \
            beta_farmyard_density[farmyard_density] + \
            beta_population[population] + \
            beta_forest_type[forest_type] + \
            beta_ffmc * ffmc + \
            error_var

        p = pm.Deterministic('p', pm.math.invlogit(mean))  # type: ignore
        y_pred = pm.Bernoulli("y_pred", p, observed=fire_labels)

        return model


def create_bnn(X: np.array,
               y: np.array,
               random_seed: int = 42):

    rng = np.random.default_rng(random_seed)
    n_hidden = 2

    # Initialize random weights between each layer
    init_1 = rng.standard_normal(size=(X.shape[1], n_hidden)).astype("float32")
    init_2 = rng.standard_normal(size=(n_hidden, n_hidden)).astype("float32")
    init_out = rng.standard_normal(size=n_hidden).astype("float32")

    coords = {
        "hidden_layer_1": np.arange(n_hidden),
        "hidden_layer_2": np.arange(n_hidden),
        "train_cols": np.arange(X.shape[1]),
    }
    with pm.Model(coords=coords) as bayesian_neural_network:  # type: ignore
        ann_input = pm.Data("ann_input", X, mutable=True,
                            dims=("obs_id", "train_cols"))
        ann_output = pm.Data("ann_output", y, mutable=True, dims="obs_id")

        # Weights from input to hidden layer
        weights_in_1 = pm.Normal(
            "w_in_1", 0, sigma=1, initval=init_1, dims=("train_cols", "hidden_layer_1")
        )

        # Weights from 1st to 2nd layer
        weights_1_2 = pm.Normal(
            "w_1_2", 0, sigma=1, initval=init_2, dims=("hidden_layer_1", "hidden_layer_2")
        )

        # Weights from hidden layer to output
        weights_2_out = pm.Normal(
            "w_2_out", 0, sigma=1, initval=init_out, dims="hidden_layer_2")

        # Build neural-network using tanh activation function
        act_1 = pm.math.tanh(pm.math.dot(ann_input, weights_in_1))
        act_2 = pm.math.tanh(pm.math.dot(act_1, weights_1_2))
        act_out = pm.math.sigmoid(pm.math.dot(act_2, weights_2_out))

        act_out = pm.Deterministic("p", act_out)

        # Binary classification -> Bernoulli likelihood
        out = pm.Bernoulli(
            "y_pred",
            act_out,
            observed=ann_output,
            total_size=y.shape[0],  # IMPORTANT for minibatches
            dims="obs_id",
        )
    return bayesian_neural_network
