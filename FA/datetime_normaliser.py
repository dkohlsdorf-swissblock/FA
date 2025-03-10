from pathlib import Path
import pandas as pd

class DatetimeNormaliser():
    
    
    def __init__(self):
        self.FA_data_path = Path(__file__).parent.parent / 'FA Data'
        self.FA_data_dict = {}
        
        if self.FA_data_path.exists() and self.FA_data_path.is_dir():
            for file in self.FA_data_path.glob('*.csv'):
                df = pd.read_csv(file)
                self.FA_data_dict[file.stem] = df
        else:
            print(f"Directory not found: {self.FA_data_path}")
            

    def find_datetime_columns(self, df, file_name):
        threshold = 0.95  
        datetime_columns = []
        found_datetime_col = 0
        
        for col in df.columns:

            if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
                try:
                    converted = pd.to_datetime(df[col], errors='coerce', utc=True, format='%Y-%m-%dT%H:%M:%S.%fZ')
                    non_na_ratio = converted.notna().mean()
                    
                    if non_na_ratio <= threshold:
                        converted = pd.to_datetime(df[col], errors='coerce', utc=True, format='%Y-%m-%dT%H:%M:%SZ')
                        non_na_ratio = converted.notna().mean()
                    
                    if non_na_ratio <= threshold:
                        converted = pd.to_datetime(df[col], errors='coerce', utc=True, format='%Y-%m-%d %H:%M:%S')
                        non_na_ratio = converted.notna().mean()
                    
                    if non_na_ratio > threshold:
                        datetime_columns.append(col)
                        found_datetime_col += 1
                
                except Exception as e:
                    print(f"Error occurred while parsing column '{col}': {e}")
                    continue
        
        if found_datetime_col > 0:
            print(f"Found {found_datetime_col} datetime column(s) in file {file_name}")
        else:
            print(f"No datetime columns found in file {file_name}")
        
        return datetime_columns
    
    
    def normalise_datetime_format(self):
        for key in self.FA_data_dict:
            datetime_columns = self.find_datetime_columns(self.FA_data_dict[key], key)
            
            if datetime_columns:
                datetime_column = datetime_columns[0]
                
                self.FA_data_dict[key][datetime_column] = pd.to_datetime(
                    self.FA_data_dict[key][datetime_column], errors='coerce', utc=True
                )
                
                df_normalised = self.FA_data_dict[key].set_index(datetime_column)
                self.FA_data_dict[key] = df_normalised
                
                print(f"Normalised datetime column and set as index for file {key}")
            else:
                print(f"No datetime column to normalise in file {key}")
                
              
    def match_timeseries_granularity(self):
        granularities = {}

        for key, df in self.FA_data_dict.items():
            time_diff = df.index.to_series().diff().dropna()

            granularities[key] = time_diff.mean().total_seconds()

        least_granular_key = min(granularities, key=granularities.get)
        least_granular_df = self.FA_data_dict[least_granular_key]
        
        print(f"Least granular time series: {least_granular_key}, Granularity: {granularities[least_granular_key]} seconds")

        least_granular_index = least_granular_df.index

        for key, df in self.FA_data_dict.items():
            if key == least_granular_key:
                continue
            
            df = df[~df.index.duplicated(keep='first')]
            df_resampled = df.reindex(df.index.intersection(least_granular_index), method='ffill')
            self.FA_data_dict[key] = df_resampled
                        
            print(f"Resampled {key} to match the granularity of {least_granular_key}")
        
    
    def match_timeseries_subsets(self):
        common_index = self.FA_data_dict[next(iter(self.FA_data_dict))].index

        for key, df in self.FA_data_dict.items():
            common_index = common_index.intersection(df.index)
        
        if len(common_index) > 0:
            min_datetime = common_index.min()
            max_datetime = common_index.max()
            print(f"Largest common datetime range: {min_datetime} to {max_datetime}")

            for key, df in self.FA_data_dict.items():
                trimmed_df = df.loc[min_datetime:max_datetime]
                self.FA_data_dict[key] = trimmed_df
                print(f"Trimmed {key} to the common datetime range")
        else:
            print("No common datetime range found between the datasets")

        
    def keep_numeric(self):
        
        for key, df in self.FA_data_dict.items():
            df_numeric = df.select_dtypes(include=['number'])
            self.FA_data_dict[key] = df_numeric
            print(f"Kept only numeric columns for file {key}")
            
    
    def print_check(self):
        for key, df in self.FA_data_dict.items():
            print(key)
            print(df)