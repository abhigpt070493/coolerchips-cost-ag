# File Structure

- **analyses**: Classes & functions for analyses and iterations
  - _iterations_: initialization files for various iterations


- **inputs**: Input data defining the specifications of various manufacturing inputs in json format
    - _consumables_: Consumable materials/items/equipment for manufacturing processes
	- _equipment_: Machinery and equipment specifications
	- _facility_wide_: Inputs (like facility rent, work hours, etc.) shared between multiple processes
	- _materials_: Materials used in manufacturing processes
    - _parts_: Specifications of different manufactured parts of the cooling system


- **parts**: Classes & functions to define and modify manufactured parts


- **pbcm**: Classes & functions for process based cost model (PBCM) calculations
    - _cost_items_: Classes & functions to define and modify different cost categories
    - _cost_functions_: Functions for calculations of cost for cost categories


- **tools**: Classes & functions supporting operations that are not part of main calculations


- **workspace**: Run files for iterations & output files
    - _outputs_: output files (img, csv, etc.) for iterations


# Code Structure

The code follows a bottom-up approach to calculate the manufacturing cost for each part considering 
including the cost of inputs like material, equipment, consumables, manufacturing facility, and overhead expenses.

Below is a step-by-step guide to run and modify the model:
- Define the scenario for the iteration by creating/modifying a file in analyses/iterations
  -	For each part that needs to be modeled, define the manufacturing processes involved including machines,consumables 