import pandas as pd
import numpy as np

class Transformer:
    def __init__(self, df:pd.DataFrame):
        self.df = df

    def transform_data(self):
        # changing all blank values to NaN
        self.df = self.df.replace({None: np.nan})

        # rename column names
        self.df = self.df.rename(columns={
                'Additional Collateral Property':'additional_collateral_property',
                'State':'state',
                'Zip':'zip',        
            })
        return
