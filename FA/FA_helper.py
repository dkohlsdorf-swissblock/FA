from FA.datetime_normaliser import DatetimeNormaliser
from FA.FA import FactorAnalyzer
import matplotlib.pyplot as plt

class FAHelper():
    
    
    def __init__(self, n_factors):
        self.FA_data_dict = {}
        self.n_factors = n_factors
        
        
    def normalise_datetimes(self):
        datetime_normaliser = DatetimeNormaliser()
        datetime_normaliser.normalise_datetime_format()
        datetime_normaliser.match_timeseries_granularity()
        datetime_normaliser.match_timeseries_subsets()
        datetime_normaliser.keep_numeric()
        # datetime_normaliser.print_check()
        self.FA_data_dict = datetime_normaliser.FA_data_dict
        
        
    def factor_analysis(self):
        factor_analyzer = FactorAnalyzer(self.FA_data_dict, self.n_factors)
        factor_analyzer.factor_analysis()
        factor_analyzer.save_experiment_data()
        self.results = factor_analyzer.results
        
        
    def show_results(self):
        n_dataframes = len(self.FA_data_dict)
        n_factors = self.n_factors
        fig, axs = plt.subplots(n_dataframes, 1, figsize=(10, 5 * n_dataframes))
        
        for idx, (file_name, df) in enumerate(self.FA_data_dict.items()):
            axs[idx].plot(df.index, df)
            axs[idx].set_title(f"Time Series from {file_name}")
            axs[idx].set_xlabel("Datetime")
            axs[idx].set_ylabel("Value")
        
        if 'factors' in self.results:
            factors_df = self.results['factors']
            fig_factors, axs_factors = plt.subplots(n_factors, 1, figsize=(10, 5 * n_factors))
            
            for i in range(n_factors):
                axs_factors[i].plot(factors_df.index, factors_df.iloc[:, i])
                axs_factors[i].set_title(f"Factor {i + 1} Time Series")
                axs_factors[i].set_xlabel("Datetime")
                axs_factors[i].set_ylabel(f"Factor {i + 1}")
        
        else:
            print("No factors available to plot.")
        
        if 'factor_loadings' in self.results:
            print("Factor Loadings:")
            print(self.results['factor_loadings'])
        
        if 'explained_variance' in self.results:
            print("Explained Variance:")
            print(self.results['explained_variance'])
        
        plt.tight_layout()
        plt.show()        