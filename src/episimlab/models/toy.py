import xsimlab as xs
import xarray as xr
import attr
from .. import seir, setup, apply_counts_delta, graph


def slow_seir():
    return xs.Model(dict(
        init_epi=setup.InitDefaultEpis,
        init_counts=setup.InitDefaultCounts,
        init_coords=setup.InitDefaultCoords,
        init_phi=setup.InitPhi,
        init_phi_grp_mapping=setup.InitPhiGrpMapping,
        foi=seir.brute_force_foi.BruteForceFOI,
        seir=seir.brute_force.BruteForceSEIR,
        apply_counts_delta=apply_counts_delta.ApplyCountsDelta
    ))

def cy_adj_slow_seir():
    return xs.Model(dict(
        init_epi=setup.InitDefaultEpis,
        init_counts=setup.InitDefaultCounts,
        init_coords=setup.InitDefaultCoords,
        init_adj=setup.InitToyAdj,
        init_adj_grp_mapping=setup.InitAdjGrpMapping,
        travel=graph.cython.CythonGraph,

        # WITH slow SEIR
        init_phi=setup.InitPhi,
        init_phi_grp_mapping=setup.InitPhiGrpMapping,
        foi=seir.brute_force_foi.BruteForceFOI,
        seir=seir.brute_force.BruteForceSEIR,

        apply_counts_delta=apply_counts_delta.ApplyCountsDelta
    ))

def cy_adj():
    return xs.Model(dict(
        init_epi=setup.InitDefaultEpis,
        init_counts=setup.InitDefaultCounts,
        init_coords=setup.InitDefaultCoords,
        init_adj=setup.InitToyAdj,
        init_adj_grp_mapping=setup.InitAdjGrpMapping,
        travel=graph.cython.CythonGraph,

        # without SEIR
        foi=seir.brute_force_foi.BaseFOI,
        seir=seir.base.BaseSEIR,

        apply_counts_delta=apply_counts_delta.ApplyCountsDelta
    ))
