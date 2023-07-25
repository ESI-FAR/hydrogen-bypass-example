import pypsa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rc("figure", figsize=(8, 4))


def pre_bypass_network():
    # TODO: factor out example network k
    # import timesteps from existing model (24 snapshots)
    k = pypsa.examples.scigrid_de(from_master=True)
    timestep = k.snapshots

    n = pypsa.Network()
    n.set_snapshots(timestep)

    n.add("Bus", "Bus 1", x=9.11321, y=52.543853, v_nom=220.0)
    n.add("Bus", "Bus 2", x=9.522576, y=52.360409, v_nom=220.0)
    n.add("Line", 'Line1-2', bus0='Bus 1', bus1='Bus 2', s_nom=400, type='Al/St 240/40 2-bundle 220.0', length=43.379, num_parallel=1)

    cost_variable = k.generators.marginal_cost['218 Wind Offshore'] + 5
    capacity_factors = np.array(k.generators_t.p_max_pu.loc[:,'218 Wind Offshore'])
    capacity = k.generators.groupby('carrier').p_nom.max()['Wind Offshore']
    n.add(
        'Generator', "Offwind",
        bus='Bus 1',
        carrier='Offwind',
        efficiency=1,
        marginal_cost=cost_variable,  # 5 euro/MWh
        p_max_pu=capacity_factors,
        p_nom=capacity,  # 1447.20 MW
    )

    capacity_gas = k.generators.groupby('carrier').p_nom.max().loc['Gas']/5
    cost_gas = k.generators.marginal_cost['1 Gas'] - 10
    n.add(
        'Generator', 'Gas',
        bus='Bus 2',
        carrier='Gas',
        efficiency=0.58,
        p_nom=capacity_gas,  # ~460 MW
        marginal_cost=cost_gas,  # 40 euro/MWh
    )

    # TODO: factor out example network k
    loads = k.loads_t.p_set.sum(axis=1)/100  # peak of  684.2480 at 17:00:00
    # We modify the load time series such that there is a mismatch between peak generation (from wind) and peak demand
    loads.iloc[0:15] -= 50
    loads.iloc[15:] += 100
    n.add("Load", 'electricity demand', bus='Bus 2', p_set=loads)

    return n


def add_hydrogen_bypass(n):
    # First, add a bus for hydrogen carrier (different from electricity bus)
    n.add("Bus", "hydrogen", x=9.21321, y=52.743853)
    # Add hydrogen storage with storage capacity of 1,000,000 MWh
    n.add("Store", "hydrogen storage", bus="hydrogen", carrier='hydrogen storage', e_nom=1e6)
    # Add electrolyzer as link (P2G) with power capacity of 500 MW
    n.add("Link", "electrolysis", bus0="Bus 1", bus1="hydrogen", carrier='electrolyzer', p_nom=500, efficiency=0.7)
    # Add fuell cell as link (G2P)
    n.add("Link", "fuel cell", bus0="hydrogen", bus1="Bus 2", carrier='fuel cell', p_nom=500, efficiency=0.5)

    return n


def bypass_network():
    network = pre_bypass_network()
    network = add_hydrogen_bypass(network)
    return network


n1 = pre_bypass_network()
n1.optimize(solver_name='glpk')
n1.generators_t.p.plot.bar(stacked=True)
plt.savefig('pre-bypass.png', bbox_inches='tight')
