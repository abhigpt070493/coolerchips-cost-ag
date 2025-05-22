from analyses.Scenario import Scenario
from analyses.cost_output import calc_cost_obj, conv_cost_to_df
import pandas as pd
import copy

def sensitivity_analysis_cont(scenario:Scenario, process_params_dict, sensitivity_range, sensitivity_interval):
    """
    Conducts a sensitivity analysis by varying specified attributes of the 'ProcessStep' or 'Machine' classes
    within a Scenario instance.

    :param scenario: An instance of the Scenario class containing mfg_process.
    :param process_params_dict: Dictionary with process names as keys and lists of parameter names to vary as values.
    :param sensitivity_range: Tuple (min_percentage, max_percentage) specifying the range of percentage changes.
    :param sensitivity_interval: Integer specifying the interval of percentage changes.
    :return: DataFrame containing the results of all iterations with additional columns for process name,
             parameter name, and percentage change.
    """
    results = []

    for process_name, process_step in scenario.mfg_process.items():
        del process_step.fac_config
        del process_step.proc_cost
        params_to_vary = process_params_dict.get(process_name, [])

        for param in params_to_vary:
            for percentage in range(sensitivity_range[0], sensitivity_range[1] + 1, sensitivity_interval):
                # Create a deep copy of the Scenario instance
                scenario_copy = copy.deepcopy(scenario)

                # Determine if the parameter belongs to ProcessStep or Machine
                if hasattr(process_step, param):
                    # Parameter is an attribute of ProcessStep
                    modified_process_step = process_step.create_variant([param], percentage)
                    modified_process_step.mach = process_step.mach  # Retain original Machine
                elif hasattr(process_step.mach, param):
                    # Parameter is an attribute of Machine
                    modified_machine = process_step.mach.create_variant([param], percentage)
                    modified_process_step = process_step.create_variant([], 0)  # Create a base variant
                    modified_process_step.mach = modified_machine
                else:
                    raise AttributeError(f"Parameter '{param}' does not exist in ProcessStep or Machine.")

                # Update the mfg_process dictionary in the copied Scenario
                scenario_copy.mfg_process[process_name] = modified_process_step

                # Apply the function to the modified Scenario and get the resulting DataFrame
                cost_bd = calc_cost_obj(scenario_copy)
                df = conv_cost_to_df(scenario_copy.mfg_process, cost_bd)

                # Add columns for process name, parameter name, and percentage change
                df['Process Name'] = process_name
                df['Parameter Name'] = param
                df['Percentage Change'] = percentage

                results.append(df)

    final_df = pd.concat(results, ignore_index=True)
    return final_df


def sensitivity_analysis_disc(scenario:Scenario, process_params_dict):
    """
    Conducts a sensitivity analysis by varying specified attributes of the 'ProcessStep' or 'Machine' classes
    within a Scenario instance.

    :param scenario: An instance of the Scenario class containing mfg_process.
    :param process_params_dict: Dictionary with process names as keys and lists of parameter values to vary as values.
    :param func: Function that takes a Scenario instance as input and returns a DataFrame.
    :return: DataFrame containing the results of all iterations with additional columns for process name,
             parameter name, and parameter value used.
    """
    results = []

    for process_name, process_step in scenario.mfg_process.items():
        params_to_vary = process_params_dict.get(process_name, [])

        for param, values in params_to_vary.items():
            for value in values:
                # Create a deep copy of the Scenario instance
                scenario_copy = copy.deepcopy(scenario)

                # Determine if the parameter belongs to ProcessStep or Machine
                if hasattr(process_step, param):
                    # Parameter is an attribute of ProcessStep
                    modified_process_step = process_step.create_variant([param], value)
                    modified_process_step.mach = process_step.mach  # Retain original Machine
                elif hasattr(process_step.mach, param):
                    # Parameter is an attribute of Machine
                    modified_machine = process_step.mach.create_variant([param], value)
                    modified_process_step = process_step.create_variant([], 0)  # Create a base variant
                    modified_process_step.mach = modified_machine
                else:
                    raise AttributeError(f"Parameter '{param}' does not exist in ProcessStep or Machine.")

                # Update the mfg_process dictionary in the copied Scenario
                scenario_copy.mfg_process[process_name] = modified_process_step

                # Apply the function to the modified Scenario and get the resulting DataFrame
                cost_bd = calc_cost_obj(scenario_copy)
                df = conv_cost_to_df(scenario_copy.mfg_process, cost_bd)

                # Add columns for process name, parameter name, and percentage change
                df['Process Name'] = process_name
                df['Parameter Name'] = param
                df['Parameter Value'] = value

                results.append(df)

    final_df = pd.concat(results, ignore_index=True)
    return final_df