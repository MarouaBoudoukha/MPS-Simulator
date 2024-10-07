# smart-bi-directional-simulation.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from mps_class import MPS

# Constants
TYPE_STD = 0
TYPE_HUB = 1

# Simulation Function
def run_simulation(iterations, mps_configs, hub_config):
    # Initialize multiple MPS systems based on user configurations.
    mps_systems = []
    for config in mps_configs:
        mps = MPS(
            max_power=config['max_power'],
            max_battery=config['max_battery'],
            max_solar=config['max_solar'],
            peak_sun_hours=config['peak_sun_hours'],
            init_soc=config['init_soc'],
            load_power=config['load_power'],
            load_hours=config['load_hours'],
            mps_type=TYPE_STD,
            name=config['name']
        )
        mps_systems.append(mps)

    # Initialize a central hub.
    hub = MPS(
        max_power=hub_config['max_power'],
        max_battery=hub_config['max_battery'],
        max_solar=hub_config['max_solar'],
        peak_sun_hours=hub_config['peak_sun_hours'],
        init_soc=hub_config['init_soc'],
        load_power=hub_config['load_power'],
        load_hours=hub_config['load_hours'],
        mps_type=TYPE_HUB,
        name=hub_config['name']
    )

    # Run simulation for the specified number of iterations, updating each MPS and the hub.
    for iteration in range(iterations):
        for mps in mps_systems:
            mps.update(iteration)
        hub.update(iteration)

        # Link MPS outputs to hub inputs
        hub.power_in = sum(mps.power_out for mps in mps_systems)
        hub.power_out = sum(mps.power_in for mps in mps_systems)

    # Collect results for each system
    results = {'hub': hub.get_results()}
    for mps in mps_systems:
        results[mps.name] = mps.get_results()

    return results

# Matplotlib Plotting Function
def plot_results(results, iterations):

    fig, axs = plt.subplots(len(results), 1, figsize=(10, 5 * len(results)))

    if len(results) == 1:
        axs = [axs]  # Make it iterable

    # Create subplots for each MPS and the hub.
    for ax, (name, data) in zip(axs, results.items()):
        df = pd.DataFrame(data)
        df['iteration'] = range(iterations)

        #Plots various metrics like SOC, remaining battery, charge/discharge rates, solar input, local load, power in/out.
        ax.plot(df['iteration'], df['soc'], label='SOC (%)')
        ax.plot(df['iteration'], df['remaining_battery'], label='Remaining Battery (kWh)')
        ax.plot(df['iteration'], df['bat_charge'], label='Battery Charge (kW)')
        ax.plot(df['iteration'], df['bat_discharge'], label='Battery Discharge (kW)')
        ax.plot(df['iteration'], df['solar_input'], label='Solar Input (kW)')
        ax.plot(df['iteration'], df['local_load'], label='Local Load (kW)')
        ax.plot(df['iteration'], df['power_in'], label='Power In (kW)')
        ax.plot(df['iteration'], df['power_out'], label='Power Out (kW)')

        ax.set_title(f'Results for {name}')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Values')
        ax.legend()
        ax.grid(True)

    # Display the plots in the Streamlit app.
    plt.tight_layout()
    st.pyplot(fig)

# Plotly Plotting Function
def plot_results_plotly(results, iterations):
    for name, data in results.items():
        df = pd.DataFrame(data)
        df['iteration'] = range(iterations)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['soc'], mode='lines', name='SOC (%)'))
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['remaining_battery'], mode='lines', name='Remaining Battery (kWh)'))
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['bat_charge'], mode='lines', name='Battery Charge (kW)'))
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['bat_discharge'], mode='lines', name='Battery Discharge (kW)'))
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['solar_input'], mode='lines', name='Solar Input (kW)'))
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['local_load'], mode='lines', name='Local Load (kW)'))
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['power_in'], mode='lines', name='Power In (kW)'))
        fig.add_trace(go.Scatter(x=df['iteration'], y=df['power_out'], mode='lines', name='Power Out (kW)'))

        fig.update_layout(title=f'Results for {name}', xaxis_title='Iteration', yaxis_title='Values', legend_title='Metrics')
        st.plotly_chart(fig)

def plot_results_plotly2(name, data, iterations):
    df = pd.DataFrame(data)
    df['iteration'] = range(iterations)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['soc'], mode='lines', name='SOC (%)'))
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['remaining_battery'], mode='lines', name='Remaining Battery (kWh)'))
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['bat_charge'], mode='lines', name='Battery Charge (kW)'))
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['bat_discharge'], mode='lines', name='Battery Discharge (kW)'))
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['solar_input'], mode='lines', name='Solar Input (kW)'))
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['local_load'], mode='lines', name='Local Load (kW)'))
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['power_in'], mode='lines', name='Power In (kW)'))
    fig.add_trace(go.Scatter(x=df['iteration'], y=df['power_out'], mode='lines', name='Power Out (kW)'))

    fig.update_layout(title=f'Results for {name}', xaxis_title='Iteration', yaxis_title='Values', legend_title='Metrics')
    st.plotly_chart(fig, use_container_width=True)

def plot_results_separated2(results, iterations):
    """
    For each MPS, plot its metrics separately using the provided plot_results_plotly function.
    Also, create a global plot aggregating key metrics across all systems.
    """
    # Create an expander for Per-MPS Plots
    with st.expander("View Per-MPS Detailed Plots"):
        for system_name, data in results.items():
            st.subheader(f"Results for {system_name}")
            plot_results_plotly2(system_name, data, iterations)

    # Create a separate section for Global Metrics
    st.subheader("Global Metrics Across All Systems")
    fig_global = go.Figure()

    # Aggregate Total SOC across all systems
    total_soc = None
    for system_name, data in results.items():
        df = pd.DataFrame(data)
        if total_soc is None:
            total_soc = df['soc']
        else:
            total_soc += df['soc']

    if total_soc is not None:
        fig_global.add_trace(go.Scatter(
            x=list(range(iterations)),
            y=total_soc,
            mode='lines',
            name='Total SOC'
        ))

    # Aggregate Total Power In and Power Out
    total_power_in = 0
    total_power_out = 0
    for system_name, data in results.items():
        df = pd.DataFrame(data)
        total_power_in += df['power_in']
        total_power_out += df['power_out']

    fig_global.add_trace(go.Scatter(
        x=list(range(iterations)),
        y=total_power_in,
        mode='lines',
        name='Total Power In'
    ))

    fig_global.add_trace(go.Scatter(
        x=list(range(iterations)),
        y=total_power_out,
        mode='lines',
        name='Total Power Out'
    ))

    # Calculate and plot Average SOC
    average_soc = total_soc / len(results) if len(results) > 0 else 0
    fig_global.add_trace(go.Scatter(
        x=list(range(iterations)),
        y=[average_soc] * iterations,
        mode='lines',
        name='Average SOC'
    ))

    fig_global.update_layout(
        title='Global Metrics Across All Systems',
        xaxis_title='Iteration',
        yaxis_title='Values',
        legend_title='Metrics',
        hovermode='closest'
    )

    st.plotly_chart(fig_global, use_container_width=True)

def plot_results_separated(results, iterations):
    # Create an expander for Per-MPS Plots
    with st.expander("View Per-MPS Detailed Plots"):
        for system_name, data in results.items():
            st.subheader(f"Results for {system_name}")
            plot_results_plotly2(system_name, data, iterations)

    # Define metric groups
    metric_groups = {
        'Battery Metrics': ['soc', 'remaining_battery'],
        'Power Metrics': ['power_in', 'power_out'],
        'Energy Flow Metrics': ['solar_input', 'local_load', 'bat_charge', 'bat_discharge']
    }

    # Select systems to include in global metrics
    #system_names = list(results.keys())
    #selected_systems = st.multiselect("Select Systems for Global Metrics", options=system_names, default=system_names)

    # Iterate through each MPS and create separate plots
    for system_name, data in results.items():
        st.subheader(f"Results for {system_name}")

        # Create tabs for different metric groups within each MPS
        tabs = st.tabs(list(metric_groups.keys()))

        for tab, (group_name, metrics) in zip(tabs, metric_groups.items()):
            with tab:
                fig = go.Figure()
                df = pd.DataFrame(data)
                df['iteration'] = range(iterations)

                for metric in metrics:
                    fig.add_trace(go.Scatter(
                        x=df['iteration'],
                        y=df[metric],
                        mode='lines',
                        name=metric
                    ))

                fig.update_layout(
                    title=f'{group_name} for {system_name}',
                    xaxis_title='Iteration',
                    yaxis_title='Values',
                    legend_title='Metrics',
                    hovermode='closest'
                )

                st.plotly_chart(fig, use_container_width=True)
_ ="""
    # Global Metrics Plot
    st.subheader("Global Metrics Across Selected Systems")
    fig_global = go.Figure()

    # Example Global Metric: Total SOC across selected systems
    total_soc = None
    for system_name, data in results.items():
        if system_name not in selected_systems:
            continue
        df = pd.DataFrame(data)
        if total_soc is None:
            total_soc = df['soc']
        else:
            total_soc += df['soc']

    if total_soc is not None:
        fig_global.add_trace(go.Scatter(
            x=list(range(iterations)),
            y=total_soc,
            mode='lines',
            name='Total SOC'
        ))

    # Example Global Metrics: Total Power In and Power Out
    total_power_in = 0
    total_power_out = 0
    for system_name, data in results.items():
        if system_name not in selected_systems:
            continue
        df = pd.DataFrame(data)
        total_power_in += df['power_in']
        total_power_out += df['power_out']

    fig_global.add_trace(go.Scatter(
        x=list(range(iterations)),
        y=total_power_in,
        mode='lines',
        name='Total Power In'
    ))

    fig_global.add_trace(go.Scatter(
        x=list(range(iterations)),
        y=total_power_out,
        mode='lines',
        name='Total Power Out'
    ))

    # Calculate and plot Average SOC
    average_soc = total_soc / len(selected_systems) if len(selected_systems) > 0 else 0
    fig_global.add_trace(go.Scatter(
        x=list(range(iterations)),
        y=[average_soc] * iterations,
        mode='lines',
        name='Average SOC'
    ))

    fig_global.update_layout(
        title='Global Metrics Across Selected Systems',
        xaxis_title='Iteration',
        yaxis_title='Values',
        legend_title='Metrics',
        hovermode='closest'
    )

    st.plotly_chart(fig_global, use_container_width=True)
"""
def main():
    st.title("MPS Simulator Dashboard")
    st.markdown("""
    This dashboard allows you to configure and run simulations for multiple Mobile Power Systems (MPS) and a central hub.
    Adjust the parameters, run the simulation, and visualize the results.
    """)

    st.sidebar.header("Simulation Parameters")

    # Simulation parameters
    iterations = st.sidebar.number_input("Number of Iterations", min_value=1, max_value=1000, value=48, step=1)
    num_sys = st.sidebar.number_input("Number of MPS Systems", min_value=1, max_value=10, value=4, step=1)

    # MPS configurations
    mps_configs = []
    for i in range(num_sys):
        st.sidebar.subheader(f"MPS {i+1} Configuration")
        name = st.sidebar.text_input(f"MPS {i+1} Name", value=f"mps{i+1}")
        max_power = st.sidebar.number_input(f"MPS {i+1} Max Power (kW)", min_value=1.0, value=5.0, step=0.5)
        max_battery = st.sidebar.number_input(f"MPS {i+1} Max Battery (kWh)", min_value=10.0, value=40.0, step=5.0)
        max_solar = st.sidebar.number_input(f"MPS {i+1} Max Solar (kW)", min_value=1.0, value=4.0, step=0.5)
        peak_sun_hours = st.sidebar.number_input(f"MPS {i+1} Peak Sun Hours", min_value=1, max_value=12, value=4, step=1)
        init_soc = st.sidebar.slider(f"MPS {i+1} Initial SOC (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        load_power = st.sidebar.number_input(f"MPS {i+1} Load Power (kW)", min_value=0.0, value=8.0, step=0.5)
        load_hours = st.sidebar.number_input(f"MPS {i+1} Load Hours", min_value=0, max_value=24, value=10, step=1)

        config = {
            'name': name,
            'max_power': max_power,
            'max_battery': max_battery,
            'max_solar': max_solar,
            'peak_sun_hours': peak_sun_hours,
            'init_soc': init_soc,
            'load_power': load_power,
            'load_hours': load_hours
        }
        mps_configs.append(config)

    # Hub configuration
    st.sidebar.subheader("Hub Configuration")
    hub_name = st.sidebar.text_input("Hub Name", value="hub")
    hub_max_power = st.sidebar.number_input("Hub Max Power (kW)", min_value=10.0, value=50.0, step=5.0)
    hub_max_battery = st.sidebar.number_input("Hub Max Battery (kWh)", min_value=50.0, value=200.0, step=10.0)
    hub_max_solar = st.sidebar.number_input("Hub Max Solar (kW)", min_value=0.0, value=0.0, step=1.0)
    hub_peak_sun_hours = st.sidebar.number_input("Hub Peak Sun Hours", min_value=0, max_value=24, value=0, step=1)
    hub_init_soc = st.sidebar.slider("Hub Initial SOC (%)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
    hub_load_power = st.sidebar.number_input("Hub Load Power (kW)", min_value=0.0, value=0.0, step=0.5)
    hub_load_hours = st.sidebar.number_input("Hub Load Hours", min_value=0, max_value=24, value=0, step=1)

    hub_config = {
        'name': hub_name,
        'max_power': hub_max_power,
        'max_battery': hub_max_battery,
        'max_solar': hub_max_solar,
        'peak_sun_hours': hub_peak_sun_hours,
        'init_soc': hub_init_soc,
        'load_power': hub_load_power,
        'load_hours': hub_load_hours
    }

    if st.sidebar.button("Run Simulation"):
        with st.spinner("Running simulation..."):
            results = run_simulation(iterations, mps_configs, hub_config)
        st.success("Simulation completed!")

        # Display results
        st.header("Simulation Results")
        #plot_results(results, iterations)
        #plot_results_plotly(results, iterations)
        plot_results_separated(results, iterations)

        # Optionally, provide download option for CSV
        for name, data in results.items():
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Download {name} Results as CSV",
                data=csv,
                file_name=f"{name}_results.csv",
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
