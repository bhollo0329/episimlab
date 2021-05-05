"""Infrastructure for fitting using linear least squares."""

import os
import attr
import xarray as xr
import pandas as pd
from pandas.core.indexes.datetimes import DatetimeIndex
from scipy.optimize import least_squares
from episimlab import EPISIMLAB_HOME
from episimlab.models import basic as basic_models
import xsimlab as xs
from xsimlab.model import Model


@attr.s
class LeastSqFitter:
    """Base wrapper class for running episimlab models with
    scipy.optimize.least_squares
    """
    data = attr.ib(type=xr.DataArray, repr=False)
    guess = attr.ib(type=float)
    model = attr.ib(type=Model)

    dep_var = attr.ib(type=str, default='beta')
    step_clock = attr.ib(type=DatetimeIndex, default=pd.date_range(start='2/1/2020', end='4/1/2020', freq='12H'), repr=False)
    verbosity = attr.ib(type=int, default=0)
    # extra kwargs to pass to least_squares
    ls_kwargs = attr.ib(type=dict, default=attr.Factory(dict), repr=False)

    # TODO: move to child
    config_fp = attr.ib(type=str, default=os.path.join(EPISIMLAB_HOME, 'tests', 'config', 'example_v1.yaml'), repr=True)

    def get_in_ds(self):
        return xs.create_setup(
            model=self.model,
            clocks={
                'step': self.step_clock
            },
            input_vars={
                'read_config__config_fp': self.config_fp,
                'foi__beta': beta
            },
            output_vars={
                'apply_counts_delta__counts': 'step'
            }
        )

    def fit(self):
        self.soln = least_squares(
            fun=self.calc_residual,
            x0=self.guess,
            xtol=1e-8,
            verbose=self.verbosity,
            args=(self.data,),
            # bounds=bounds,
            **self.ls_kwargs
        )
        return self.soln
    
    def get_in_ds(self, dep_vars) -> xr.Dataset:
        """Generate an input Dataset for the model"""
        beta = dep_vars[0]
        return xs.create_setup(
            model=self.model,
            clocks={'step': self.step_clock},
            input_vars={
                'read_config__config_fp': self.config_fp,
                'foi__beta': beta
            },
            output_vars={'apply_counts_delta__counts': 'step'}
        )
    
    def get_out_ds(self, dep_vars) -> xr.Dataset:
        """Run model, returning output Dataset"""
        return (self 
                .get_in_ds(dep_vars) 
                .xsimlab 
                .run(model=self.model, decoding=dict(mask_and_scale=False)))
    
    def calc_residual(self, dep_vars, ih_actual) -> float:
        # Run model and pull out counts of Ih compartment over time
        ih_pred = (self
                   .get_out_ds(dep_vars) 
                   .apply_counts_delta__counts 
                   .loc[dict(compartment='Ih')] 
                   .sum(dim=['age_group', 'risk_group', 'vertex']))
        assert len(ih_pred.shape) == 1, (ih_pred.shape, "!= 1")
        assert 'step' in ih_pred.dims, f"'step' is not in {ih_pred.dims}"

        # Calculate residual
        resi = ih_pred - ih_actual
        return resi