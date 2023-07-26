import matplotlib.pyplot as plt
import pandas as pd
from pyprojroot import here
import pypsa

plt.rc("figure", figsize=(8, 4))


def pre_bypass_network():
    wind_resources = pd.read_csv(here('timeseries_data/wind_resource.csv'), index_col=0, parse_dates=True)
    wind_max_capacity = wind_resources['windlocation'].max()
    wind_capacity_factors = wind_resources['windlocation'] / wind_max_capacity

    n = pypsa.Network()
    n.set_snapshots(wind_resources.index)

    n.add("Bus", "Bus 1", x=9.11321, y=52.543853, v_nom=220.0)
    n.add("Bus", "Bus 2", x=9.522576, y=52.360409, v_nom=220.0)
    n.add("Line", 'Line1-2', bus0='Bus 1', bus1='Bus 2', s_nom=400,
          type='Al/St 240/40 2-bundle 220.0', length=43.379, num_parallel=1)

    n.add(
        'Generator', "Offwind",
        bus='Bus 1',
        carrier='Offwind',
        efficiency=1,
        marginal_cost=5,  # 5 euro/MWh
        p_max_pu=wind_capacity_factors,
        p_nom=wind_max_capacity,  # 1447.20 MW
    )

    n.add(
        'Generator', 'Gas',
        bus='Bus 2',
        carrier='Gas',
        efficiency=0.58,
        p_nom=460,  # 460 MW
        marginal_cost=40,  # 40 euro/MWh
    )

    # demand is stored as negative values for calliope, but PyPSA expects positive
    demand = pd.read_csv(here('timeseries_data/demand.csv'), index_col=0, parse_dates=True)['city'] * -1
    demand.name = None
    n.add("Load", 'electricity demand', bus='Bus 2', p_set=demand)

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


def simulate_pre_bypass():
    n1 = pre_bypass_network()
    n1.optimize(solver_name='glpk')
    plot_pre_bypass_power(n1)


def plot_pre_bypass_power(n):
    fig, ax = plt.subplots()
    barplot = n.generators_t.p.plot.bar(stacked=True, ax=ax)

    # naive plotting does not work: plot and barplot via pandas cause conflicting x-axis
    # n1.loads_t.p_set.plot(ylabel='MW', ax=ax)
    ax.plot(barplot.xaxis.major.locator.locs, n.loads_t.p_set['electricity demand'], label='electricity demand')
    ax.set_ylabel('MW')
    ax.legend(loc=0)
    fig.savefig('pre-bypass-power.png', bbox_inches='tight')


def simulate_bypass():
    n2 = bypass_network()
    n2.optimize(solver_name='glpk')

    plot_bypass_power(n2)
    plot_hydrogen_storage(n2)


def plot_bypass_power(n):
    """Plot power production/consumption"""
    fig, ax = plt.subplots()
    to_plot = n.generators_t.p.copy()
    to_plot['fuel cell'] = -n.links_t.p1['fuel cell']  # plot provided power to city as positive
    to_plot['electrolysis'] = -n.links_t.p0['electrolysis']  # plot consumed power from wind as negative
    # reorder columns to match calliope
    barplot = to_plot[["Gas", "fuel cell", "Offwind", "electrolysis"]].plot.bar(stacked=True, ax=ax, legend=False)

    # naive plotting does not work: plot and barplot via pandas cause conflicting x-axis
    # n2.loads_t.p_set.plot(ylabel='MW', ax=ax)
    ax.plot(barplot.xaxis.major.locator.locs, n.loads_t.p_set['electricity demand'], color='black', label='electricity demand')
    ax.set_ylabel('MW')
    ax.legend(loc=0)
    fig.savefig('bypass-power.png', bbox_inches='tight')


def plot_hydrogen_storage(n):
    """Plot hydrogen production/storage/consumption"""
    fig, ax = plt.subplots()
    to_plot = (-n.links_t.p0['fuel cell']) - n.links_t.p1['electrolysis']
    barplot = to_plot.plot.bar(label='net storage (dis)charge', ax=ax, legend=False)

    ax.plot(barplot.xaxis.major.locator.locs, n.stores_t.e, label='hydrogen storage')
    ax.axhline(y=0, color='black', linewidth=.5)
    ax.set_ylabel('Storage')
    ax.legend(loc=0)
    fig.savefig('bypass-storage.png', bbox_inches='tight')


if __name__ == '__main__':
    simulate_pre_bypass()
    simulate_bypass()
