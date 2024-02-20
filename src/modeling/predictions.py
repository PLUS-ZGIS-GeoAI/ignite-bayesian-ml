import pandas as pd
import numpy as np
import pymc as pm
import arviz as az


class BayesianPrediction:

    def __init__(self, model: object,
                 trace: object,
                 x_new: dict,
                 var_names_pred: list,
                 seed: int):

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
                trace_new, var_names=self.var_names_pred, random_seed=self.seed)
            trace_new.extend(ppc)

        self.trace_pred = trace_new


class BinaryClassification(BayesianPrediction):

    def __init__(self, model: object,
                 trace: object,
                 x_new: dict,
                 seed: int,
                 y_var_name: str,
                 p_var_name: str):

        super().__init__(model, trace, x_new, [y_var_name, p_var_name], seed)
        self.y_var_name = y_var_name
        self.p_var_name = p_var_name

    def get_predictions(self, threshold: float = 0.5):
        """return binary predictions based on the threshold"""

        p_pred = self.trace_pred.posterior_predictive[self.y_var_name].mean(dim=[
                                                                            "chain", "draw"])
        y_pred = (p_pred >= threshold).astype("int")
        return y_pred, p_pred

    def get_binary_entropy(self):
        """function calculates binary entropy"""

        arr = self.trace_pred.posterior_predictive[self.y_var_name]

        def binary_entropy(posterior: np.array):
            n1 = np.sum(posterior)
            n = len(posterior)
            p1 = n1 / n
            p0 = 1 - p1
            jitter = 1e-8  # small value to avoid taking log of 0
            entropy = - (p1 * np.log2(p1 + jitter) + p0 * np.log2(p0 + jitter))
            return entropy

        # TODO check if everything went right; changed from (2, 1) to 0
        entropy_all_traces = np.apply_along_axis(
            binary_entropy, axis=0, arr=arr)
        return np.mean(entropy_all_traces, axis=0)

    def get_hdi(self, prob: float = 0.95):
        """
        function calculates high density interval (interval with the biggest distribution mass) of predictions
        """

        hdi = az.hdi(self.trace_pred.posterior_predictive[self.p_var_name], hdi_prob=prob)[
            self.p_var_name].values
        hdi_width = hdi[:, 1] - hdi[:, 0]
        return hdi, hdi_width

    def predict(self, pred_threshold: float = 0.5, hdi_prob: float = 0.8):
        """
        combines y and p predictions, hdi and binary entropy into one dataframe
        """

        df = pd.DataFrame()
        y_pred, p_pred = self.get_predictions(pred_threshold)
        hdi, hdi_width = self.get_hdi(hdi_prob)
        binary_entropy = self.get_binary_entropy()
        df["y_pred"] = y_pred
        df["p_pred"] = p_pred
        df["hdi_lower"] = hdi[:, 0]
        df["hdi_upper"] = hdi[:, 1]
        df["hdi_width"] = hdi_width
        df["binary_entropy"] = binary_entropy
        return df


class BinaryClassificationBNN(BinaryClassification):

    def __init__(self, model: object,
                 trace: object,
                 x_new: np.array,
                 seed: int,
                 y_var_name: str,
                 p_var_name: str):
        super().__init__(model, trace, x_new, seed, y_var_name, p_var_name)

    def extend_trace(self):
        """
        add posterior predictive samples to trace
        """

        trace_new = self.trace.copy()

        with self.model:
            pm.set_data(new_data={"ann_input": self.x_new})
            ppc = pm.sample_posterior_predictive(
                trace_new, var_names=self.var_names_pred, random_seed=0)
            trace_new.extend(ppc)

        self.trace_pred = trace_new
