from FA.FA_helper import FAHelper

# max of n_factors is the number of columns used in factor analysis
# n_factors < len(combined_df.columns)
n_factors = 5

FA_helper = FAHelper(n_factors)
FA_helper.normalise_datetimes()
FA_helper.factor_analysis()
#FA_helper.show_results() # - not ready yet



