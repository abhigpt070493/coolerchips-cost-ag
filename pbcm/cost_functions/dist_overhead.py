def distribute_overhead(proc_cost_bd, overhead, mfg_process):
    """
    Distributes overhead across process steps proportional to each steps' portion of non-overhead & non-materials costs.

    Parameters
    ----------
    proc_cost_bd: dict
        Dict of cost_functions for each process step [process step name: process step cost_functions].

    overhead: int or float
        Total cost_functions of overhead expenses.

    mfg_process: dict
        Dict of ProcessSteps for all steps in manufacturing process [process step name: ProcessStep].

    Returns
    -------

    """
    # Get total cost_functions for all process steps (without material cost_functions).
    tot = 0
    for k, v in proc_cost_bd.items():
        tot = tot + v

    # Distribute overhead across process steps.
    for k, v in proc_cost_bd.items():
        over = v / tot * overhead
        proc_cost_bd[k] = v + over
        # Update process step cost_functions attribute
        mfg_process[k].proc_cost['overhead'] = over
        mfg_process[k].proc_cost['total'] = mfg_process[k].proc_cost['total'] + over
    return proc_cost_bd
