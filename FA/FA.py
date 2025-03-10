from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
import numpy as np
import pandas as pd
import os


class FactorAnalyzer():
    
    
    def __init__(self, FA_data_dict, n_factors):
        self.FA_data_dict = FA_data_dict
        self.n_components = n_factors


    def factor_analysis(self):
        combined_df = pd.concat(self.FA_data_dict.values(), axis=1)
        
        if combined_df.isnull().values.any():
            print("Warning: NaN values detected.")
            
        if np.isinf(combined_df.values).any():
            print("Warning: Infinite values detected.")
            combined_df.replace([np.inf, -np.inf], np.nan, inplace=True)

        if not combined_df.select_dtypes(include=[np.number]).shape[1] == combined_df.shape[1]:
            print("Warning: Data contains non-numeric values.")
            combined_df = combined_df.select_dtypes(include=[np.number]) 

        if combined_df.empty:
            print("Error: The combined DataFrame is empty.")
            return None
        
        print(f"Number of columns included for factor analysis (and MAX number of factors): {combined_df.shape[1]}")
        print(f"Columns included are: {combined_df.columns.tolist()}")


        combined_df = combined_df.dropna(axis=1, how='all')
        imputer = SimpleImputer(strategy='mean')
        combined_df_imputed = pd.DataFrame(imputer.fit_transform(combined_df), columns=combined_df.columns)
        scaler = StandardScaler()
        standardized_data = scaler.fit_transform(combined_df_imputed)
        factor_analysis = FactorAnalysis(n_components=self.n_components)
        factors = factor_analysis.fit_transform(standardized_data)
        factor_loadings = factor_analysis.components_  # factor loadings (coefficients)
        explained_variance = factor_analysis.noise_variance_  # noise variance (explained variance)
        factor_columns = [f"Factor_{i+1}" for i in range(self.n_components)]
        factors_df = pd.DataFrame(factors, index=combined_df_imputed.index, columns=factor_columns)

        self.results = {
            'factors': factors_df,  # factors (new time series)
            'factor_loadings': factor_loadings,  # factor loadings
            'explained_variance': explained_variance,  # explained variance
            'columns': combined_df_imputed.columns  # original columns
        }
        
        self.combined_df = combined_df

        return self.results

    def save_experiment_data(self):
        folder_path = "Saved data"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, "Input_FA_data.csv")
        self.combined_df.to_csv(file_path, index=False)

        print(f"DataFrame saved to {file_path}")

        with open(os.path.join(folder_path, "factor_loadings_and_variance.txt"), "w") as f:
            if 'factor_loadings' in self.results:
                f.write("Factor Loadings:\n")
                f.write(str(self.results['factor_loadings']) + "\n\n")
            else:
                f.write("Factor Loadings: Not Available\n")
                
            if 'explained_variance' in self.results:
                f.write("Explained Variance:\n")
                f.write(str(self.results['explained_variance']) + "\n")
            else:
                f.write("Explained Variance: Not Available\n")

        if 'factors' in self.results:
            factors_df = self.results['factors']
            factors_df.to_csv(os.path.join(folder_path, "factors.csv"), index=False)
            print("Factors saved to factors.csv")
        else:
            print("Factors: Not Available")
