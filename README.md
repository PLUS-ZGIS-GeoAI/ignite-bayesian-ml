# Bayesian Framework for Wildfire Risk Estimation

## Overview

This repository contains code for a study aimed at advancing Explainable AI (xAI) in Disaster Risk Reduction (DRR) for wildfire risk estimation in Austria. The study employs a Bayesian framework to enhance the transparency of machine learning models by quantifying uncertainty and effectively communicating risk scores.

## Research Objectives

The study focuses on the following key areas:
- **Model Comparison:** Comparing the performance of various Bayesian machine learning models for wildfire ignition prediction, including Spatio-Temporal Bayesian Logistic Regression (BLR), Basic Bayesian Logistic Regression, and Bayesian Neural Networks (BNN).
- **Uncertainty Analysis:** Analyzing uncertainties associated with features and risk estimates using the spatio-temporal BLR model.
- **Effective Communication:** Proposing methods to clearly convey risk estimates and their uncertainties to stakeholders.


## Repository Contents

- **`/src`**: Contains critical function and classes for setting for creating the models, make predictions, preprocessing utility functions.
machine learning models and uncertainty analysis.
- **`/scripts`**: Folder contains python scripts to create input layers for features covering whole Austria. Those layers can be used for creating a training dataset and to run inference on whole of Austria.  
- **`/data`**: Includes data needed to conduct study (please reach out to contact)
- **`/notebooks`**: This folder contains two groups of notebooks, notebooks for some special data-preprocessing and notebooks for bayesian model training and model execution. The notebook uncertainty_quantification\uncertainty_quantification_study.ipynb contains all steps of the study in focus. 
- **`/config`**: Contains configuration options and paths to source data. 


## Setup and Installation

1. **Create a Conda Environment:**

```bash
conda env create -f env.yml
```

Activate the Environment:

```bash
conda activate ignite_pymc_env
```

## Contact
For any questions or further information, please contact davidsam.roebl@gmail.com.