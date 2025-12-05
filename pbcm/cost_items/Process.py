from copy import copy

from pbcm.cost_items.Machine import Machine
from parts.Part import Part


class ProcessStep:
    """Describes characteristics of a manufacturing process step."""

    def __init__(self, name_process_step=None, mach: Machine=None, time_cycle=0, batch_size=1, parts_per_unit=1, part: Part=None, mat_use=0):
        """Initializes a process step with supplied process characteristics"""
        self.name_process_step = name_process_step
        self.mach = mach
        self.time_cycle = time_cycle
        self.batch_size = batch_size
        self.parts_per_unit = parts_per_unit
        self.fac_config = {}
        self.proc_cost = {}
        self.part = part
        self.mat_use = mat_use

    def set_time_cycle(self, time_cycle):
        """This method sets cycle time for the process step"""
        self.time_cycle = time_cycle
        return self

    def add_fac_config(self, fac_config):
        self.fac_config = fac_config
        return self

    def add_proc_cost(self, proc_cost):
        self.proc_cost = proc_cost
        return self

    def copy(self, **kwargs) -> "ProcessStep":
        res = copy(self)
        for k, v in kwargs.items():
            setattr(res, k, v)
        return res

    def create_variant(self, attributes_to_modify, percentage):
        """
        Creates a new ProcessStep instance by adjusting specified attributes by a given percentage.

        :param attributes_to_modify: List of attribute names to modify.
        :param percentage: Percentage to adjust the attributes (positive for increase, negative for decrease).
        :return: A new ProcessStep instance with adjusted attributes.
        """
        # Create a copy of the current instance's attributes
        new_attributes = vars(self).copy()

        # Adjust the specified attributes by the given percentage
        for attr in attributes_to_modify:
            if attr in new_attributes:
                original_value = new_attributes[attr]
                if isinstance(original_value, (int, float)):
                    adjustment = original_value * (percentage / 100)
                    new_attributes[attr] = original_value + adjustment
                else:
                    raise ValueError(f"Attribute '{attr}' is not numeric and cannot be adjusted by percentage.")
            else:
                raise AttributeError(f"Attribute '{attr}' does not exist in the ProcessStep class.")

        # Create a new ProcessStep instance with the adjusted attributes
        return ProcessStep(**new_attributes)
