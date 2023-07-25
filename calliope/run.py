import calliope


def simulate_pre_bypass():
    """Simulate the model without the hydrogen bypass.

    equivalent to the following CLI command:
    `calliope run hydrogen_bypass.yaml --save_plots=pre_bypass.html`
    """
    pre_bypass = calliope.Model('hydrogen_bypass.yaml')
    pre_bypass.run()
    pre_bypass.plot.summary(to_file='pre_bypass.html')


def simulate_bypass():
    """Simulate the model with the hydrogen bypass.

    equivalent to the following CLI command:
    `calliope run hydrogen_bypass.yaml --scenario=hydrogen_bypass --save_plots=bypass.html`
    """
    bypass = calliope.Model('hydrogen_bypass.yaml', scenario='hydrogen_bypass')
    bypass.run()
    bypass.plot.summary(to_file='bypass.html')


if __name__ == '__main__':
    simulate_pre_bypass()
    simulate_bypass()
