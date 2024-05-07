
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score


def plot_st_sample_size_distribution(X_train, X_test, path_to_file: str):
    """Plotting the distribution of fire and no-fire samples for train and test set"""

    fractions_train = X_train.groupby("year").fire.value_counts().unstack()
    fractions_test = X_test.groupby("year").fire.value_counts().unstack()

    plt.style.use('ggplot')
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), sharey="row")

    fractions_train.plot(kind='bar', stacked=True,
                         ax=axs[0][0], color=["blue", "red"])
    axs[0][0].set_xlabel('Year')
    axs[0][0].set_ylabel('Fraction')
    axs[0][0].set_title('Training Dataset')
    axs[0][0].legend(title='Fire', labels=['No Fire', 'Fire'])
    axs[0][0].tick_params(axis='x', rotation=45)

    fractions_test.plot(kind='bar', stacked=True,
                        ax=axs[0][1], color=["blue", "red"])
    axs[0][1].set_xlabel('Year')
    axs[0][1].set_ylabel('Fraction')
    axs[0][1].set_title('Testing Dataset')
    axs[0][1].legend(title='Fire', labels=['No Fire', 'Fire'])
    axs[0][1].tick_params(axis='x', rotation=45)

    gdf_fire_train = X_train[X_train['fire'] == 1]
    gdf_no_fire_train = X_train[X_train['fire'] == 0]

    gdf_fire_test = X_test[X_test['fire'] == 1]
    gdf_no_fire_test = X_test[X_test['fire'] == 0]

    axs[1][0].set_title('Training Dataset')
    gdf_fire_train.plot(ax=axs[1][0], color='red', label='Fire')
    gdf_no_fire_train.plot(ax=axs[1][0], color='blue', label='No Fire')

    axs[1][1].set_title('Testing Dataset')
    gdf_fire_test.plot(ax=axs[1][1], color='red', label='Fire')
    gdf_no_fire_test.plot(ax=axs[1][1], color='blue', label='No Fire')

    axs[1][0].legend()
    axs[1][1].legend()

    plt.tight_layout()
    plt.savefig(path_to_file)
    plt.show()


def plot_performance_over_test_years(preds_models: list, X_test, y_test, path_to_plot: str):
    """plot performance over test years"""

    years = ["2016", "2017", "2018", "2019", "2020"]
    result_dic = {}

    for preds_df, model in preds_models:

        preds = preds_df.copy()
        preds["year"] = X_test.year.values
        preds["y_true"] = y_test.values

        result_dic[model] = {}

        for year in years:
            data = preds[preds["year"] == year]
            result_dic[model][year] = {}
            result_dic[model][year]["accuracy"] = accuracy_score(
                data["y_true"], data["y_pred"])
            result_dic[model][year]["f1"] = f1_score(
                data["y_true"], data["y_pred"])

    patterns = ['', '////', '...', 'xxx']
    metrics = ["accuracy", "f1"]

    fig, axs = plt.subplots(1, 2, figsize=(15, 6))
    fig.subplots_adjust(hspace=0.5)

    for i, metric in enumerate(metrics):
        dic = {
            "blr": [round(result_dic["blr"][year][metric], 2) for year in result_dic["blr"]],
            "st_intercept_blr": [round(result_dic["st_intercept_blr"][year][metric], 2) for year in result_dic["st_intercept_blr"]],
            "st_blr": [round(result_dic["st_blr"][year][metric], 2) for year in result_dic["st_blr"]],
            "bnn": [round(result_dic["bnn"][year][metric], 2) for year in result_dic["bnn"]]
        }

        x = np.arange(len(years))  
        width = 0.20 
        multiplier = 0

        for j, (attribute, measurement) in enumerate(dic.items()):
            offset = width * multiplier
            rects = axs[i].bar(x + offset, measurement, width,
                               label=attribute, hatch=patterns[j])
            axs[i].bar_label(rects, padding=1, fontsize='x-small')
            multiplier += 1

        axs[i].set_ylabel(metric)
        axs[i].set_xlabel('Year')
        axs[i].set_xticks(x + width * 1.5)
        axs[i].set_xticklabels(years)
        if metric != "mean_hdi_width":
            axs[i].set_ylim(0.5, 1)
        else:
            axs[i].set_ylabel("mean hdi width")

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower right')
    plt.suptitle(f'Comparison of model performance over years')

    plt.tight_layout()
    plt.savefig(path_to_plot)
    plt.show()


def plot_performance_over_seasons(preds_models: list, X_test, y_test, path_to_plot: str):
    """plot performance over test seasons"""

    # Define seasons
    seasons = [0, 1, 2, 3]
    result_dic = {}

    for preds_df, model in preds_models:

        preds = preds_df.copy()
        preds["season"] = X_test.season.values
        preds["y_true"] = y_test.values

        result_dic[model] = {}

        for season in seasons:
            data = preds[preds["season"] == season]
            result_dic[model][season] = {}
            result_dic[model][season]["accuracy"] = accuracy_score(data["y_true"], data["y_pred"])
            result_dic[model][season]["f1"] = f1_score(data["y_true"], data["y_pred"])


    patterns = ['', '////', '...', 'xxx']
    metrics = ["accuracy", "f1"]

    fig, axs = plt.subplots(1, 2, figsize=(15, 6))
    fig.subplots_adjust(hspace=0.5)

    for i, metric in enumerate(metrics):
        dic = {
            "blr": [round(result_dic["blr"][season][metric], 2) for season in result_dic["blr"]],
            "st_intercept_blr": [round(result_dic["st_intercept_blr"][season][metric], 2) for season in result_dic["st_intercept_blr"]],
            "st_blr": [round(result_dic["st_blr"][season][metric], 2) for season in result_dic["st_blr"]],
            "bnn": [round(result_dic["bnn"][season][metric], 2) for season in result_dic["bnn"]]
        }

        x = np.arange(len(seasons))  # the label locations
        width = 0.20  # the width of the bars
        multiplier = 0

        ax = axs[i]  # Correctly accessing subplot

        for j, (attribute, measurement) in enumerate(dic.items()):
            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, label=attribute, hatch=patterns[j])
            ax.bar_label(rects, padding=1, fontsize='x-small')  # Adjust font size here
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(metric)
        ax.set_xlabel('Season')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(seasons)
        if metric != "mean_hdi_width":
            ax.set_ylim(0.5, 1)
        else:
            ax.set_ylabel("mean hdi width")

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower right')
    plt.suptitle(f'Comparison of model performance over seasons')

    plt.tight_layout()
    plt.savefig(path_to_plot)
    plt.show()





# TODO Score against HDI width

# TODO HDI width per season and per year for each model (2 plots)

# TODO HDI width per Naturregion for each model (4 maps → 1 per model)

# TODO Training Sample Size per Naturregion (Map) & Season (Graph)

# TODO Location Uncertainty Training Sample per Naturregion (Map) & Season (Graph)

# TODO Plot Intercept of ST Intercept BLR model per Naturraum $ season; evl. 2 Dimensional Colour Map (Value & Uncertainty)

# TODO Plot FFMC of ST BLR model per Naturraum & season
