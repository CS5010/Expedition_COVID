import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# Apply the default theme
sns.set_theme()
sns.set(font_scale = 1.5)

class PlotResults:
    def __init__(
        self, actuals, preds, start_date, locs, 
        figPath, show=False, save=True
    ):
        self.actuals = actuals
        self.Nloc = len(locs)
        self.preds = preds
        self.figPath = figPath
        self.locs = locs
        self.start_date = start_date

        self.show = show
        self.save = save

    def plot(self, y_true, y_preds, title, figure_name, figsize=(24,8)):
        dates = [self.start_date + np.timedelta64(days, 'D') for days in range(y_true.shape[0])]

        fig, ax = plt.subplots(figsize=figsize)
        plt.title(title)

        plt.plot(dates, y_true, color='blue', label='Observation')
        plt.plot(dates, y_preds, color='green', label='Prediction')
        ax.set_ylim(bottom=0)

        label_text = [f'{int(cases/1000)}k' for cases in plt.yticks()[0]]
        
        ax.set_yticks(plt.yticks()[0])
        ax.set_yticklabels(label_text)

        plt.xlabel('Date')
        plt.ylabel('Daily Cases')
        plt.legend()
        fig.tight_layout()

        if self.save:
            path = os.path.join(self.figPath, f'{figure_name}.png')
            plt.savefig(path)
            print(f'Saving {path}')

        if self.show:
            plt.show()

    def makeSummedPlot(self, title, figure_name, figsize=(24,8)):
        actuals_sum = np.sum(self.actuals, axis=0)
        preds_sum = np.sum(self.preds, axis=0)
        self.plot(actuals_sum, preds_sum, title, figure_name, figsize)

    
    def makeIndividualPlot(self, index, title, figure_name, figsize=(18,8)):
        self.plot(self.actuals[index, :], self.preds[index, :], title, figure_name, figsize)


class PlotWeights:
    def __init__(
        self, col_mappings, attention, 
        figPath, show=False, save=True
    ):
        self.col_mappings = col_mappings
        self.attention = attention
        self.figPath = figPath

        self.show = show
        self.save = save

    def plot_weights(self, key, feature_list, title, figsize=(16, 8)):
        ff = np.concatenate(self.attention[key], axis=0)
        if 'static' not in key:
            ff = ff.mean(axis=1)

        N = len(feature_list)
        X = np.arange(N)
       
        fig, ax = plt.subplots(figsize=figsize)

        quantiles = [.3, .5, .7]
        ff_qt = np.quantile(ff, quantiles, axis=0)
        width = 0.25
        ax.bar(X - width, ff_qt[0], width, label='0.3 quantile')
        ax.bar(X, ff_qt[1], width, label='0.5 quantile')
        ax.bar(X + width, ff_qt[2], width, label='0.7 quantile')

        ax.set_ylabel('Variable Selection Network Weight')
        ax.set_xlabel('Weight by Quantile and Feature')
        ax.set_title(title)

        ax.set_xticks(X)
        ax.set_xticklabels(feature_list)

        ax.tick_params(axis='x', labelrotation=45)
        fig.tight_layout()
        plt.legend()

        if self.save:
            path = os.path.join(self.figPath, f'{title}.png')
            plt.savefig(path)
            print(f'Saving {path}')

        if self.show:
            plt.show()


    def plot_future_weights(self, figsize=(16,8)):
        self.plot_weights('future_flags', self.col_mappings['Future'], title='Future known input selection weights by variable', figsize=figsize)

    def plot_static_weights(self, figsize=(16,8)):
        self.plot_weights('static_flags', self.col_mappings['Static'], title='Static input selection weights by variable', figsize=figsize)

    def plotObservedWeights(self, figsize=(16,8)):
        feature_list = self.col_mappings['Known Regular'] + self.col_mappings['Future'] + self.col_mappings['Target']
        feature_list = [f for f in feature_list if f not in self.col_mappings['Static']]

        self.plot_weights('historical_flags', feature_list, title='Observed input selection weights by variable', figsize=figsize)