import pandas as pd
import numpy as np
import pymc as pm
import arviz as az


class BayesianPrediction:
    def __init__(
        self, model: object, trace: object, x_new: dict, var_names_pred: list, seed: int
    ):
        self.seed = seed
        self.model = model
        self.trace = trace
        self.x_new = x_new
        self.var_names_pred = var_names_pred
        self.trace_pred = None

    def extend_trace(self):
        """add posterior predictive samples to trace"""

        trace_new = self.trace.copy()

        with self.model:
            pm.set_data(self.x_new)
            ppc = pm.sample_posterior_predictive(
                trace_new, var_names=self.var_names_pred, random_seed=self.seed
            )
            trace_new.extend(ppc)

        self.trace_pred = trace_new


class BinaryClassification(BayesianPrediction):
    def __init__(
        self,
        model: object,
        trace: object,
        x_new: dict,
        seed: int,
        y_var_name: str,
        p_var_name: str,
        z_var_name: str,
    ):
        super().__init__(
            model, trace, x_new, [y_var_name, p_var_name, z_var_name], seed
        )
        self.y_var_name = y_var_name
        self.p_var_name = p_var_name
        self.z_var_name = z_var_name

    def get_predictions(self, threshold: float = 0.5):
        """return binary predictions based on the threshold"""

        z_pred = self.trace_pred.posterior_predictive[self.z_var_name].mean(
            dim=["chain", "draw"]
        )
        p_pred = self.trace_pred.posterior_predictive[self.p_var_name].mean(
            dim=["chain", "draw"]
        )
        y_pred = (p_pred >= threshold).astype("int")
        return y_pred, p_pred, z_pred

    def get_hdi(self, var: str, prob: float):
        """
        function calculates high density interval (interval with the biggest distribution mass) of predictions
        """

        var_value = getattr(self, var)

        hdi = az.hdi(self.trace_pred.posterior_predictive[var_value], hdi_prob=prob)[
            var_value
        ].values
        hdi_width = hdi[:, 1] - hdi[:, 0]
        return hdi, hdi_width

    def predict(
        self,
        pred_threshold: float = 0.5,
        hdi_prob: float = 0.95,
        include_z: bool = True,
    ):
        """
        combines y and p predictions, hdi and binary entropy into one dataframe
        """

        df = pd.DataFrame()
        y_pred, p_pred, z_pred = self.get_predictions(pred_threshold)
        p_hdi, p_hdi_width = self.get_hdi("p_var_name", hdi_prob)
        df["y_pred"] = y_pred
        df["p_pred"] = p_pred
        df["z_pred"] = z_pred
        df["p_hdi_lower"] = p_hdi[:, 0]
        df["p_hdi_upper"] = p_hdi[:, 1]
        df["p_hdi_width"] = p_hdi_width

        if include_z:
            z_hdi, z_hdi_width = self.get_hdi("z_var_name", hdi_prob)
            df["z_hdi_lower"] = z_hdi[:, 0]
            df["z_hdi_upper"] = z_hdi[:, 1]
            df["z_hdi_width"] = z_hdi_width

        return df


class BinaryClassificationBNN:
    def __init__(
        self,
        model: object,
        trace: object,
        x_new: np.array,
        seed: int,
        y_var_name: str,
        p_var_name: str,
    ):
        self.seed = seed
        self.model = model
        self.trace = trace
        self.x_new = x_new
        self.y_var_name = y_var_name
        self.p_var_name = p_var_name
        self.trace_pred = None
        self.var_names_pred = [y_var_name, p_var_name]

    def extend_trace(self):
        """
        add posterior predictive samples to trace
        """

        trace_new = self.trace.copy()

        with self.model:
            pm.set_data(new_data={"ann_input": self.x_new})
            ppc = pm.sample_posterior_predictive(
                trace_new, var_names=self.var_names_pred, random_seed=0
            )
            trace_new.extend(ppc)

        self.trace_pred = trace_new

    def get_predictions(self, threshold: float = 0.5):
        """return binary predictions based on the threshold"""

        p_pred = self.trace_pred.posterior_predictive[self.p_var_name].mean(
            dim=["chain", "draw"]
        )
        y_pred = (p_pred >= threshold).astype("int")
        return y_pred, p_pred

    def get_hdi(self, var: str, prob: float):
        """
        function calculates high density interval (interval with the biggest distribution mass) of predictions
        """

        var_value = getattr(self, var)

        hdi = az.hdi(self.trace_pred.posterior_predictive[var_value], hdi_prob=prob)[
            var_value
        ].values
        hdi_width = hdi[:, 1] - hdi[:, 0]
        return hdi, hdi_width

    def predict(
        self,
        pred_threshold: float = 0.5,
        hdi_prob: float = 0.95,
    ):
        """
        combines y and p predictions, hdi and binary entropy into one dataframe
        """

        df = pd.DataFrame()
        y_pred, p_pred = self.get_predictions(pred_threshold)
        p_hdi, p_hdi_width = self.get_hdi("p_var_name", hdi_prob)
        df["y_pred"] = y_pred
        df["p_pred"] = p_pred
        df["p_hdi_lower"] = p_hdi[:, 0]
        df["p_hdi_upper"] = p_hdi[:, 1]
        df["p_hdi_width"] = p_hdi_width

        return df
