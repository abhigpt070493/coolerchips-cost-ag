# CoolerChips HOMEDUCS Cost Analysis Tool

This repository provides a cost modeling tool for components of the CoolerChips HOMEDUCS system. It includes modular scripts to define cost items, scale parameters, perform sensitivity analysis, and visualize results.

## Setup

1. **Clone the repository**:
   ```bash
   git clone <https://github.com/abhigpt070493/coolerchips-cost-ag>
   cd coolerchips-cost-ag
   
2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

## File Structure

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


## Running the model

The code follows a bottom-up approach to calculate the manufacturing cost for each part, accounting for materials, equipment, consumables, facility expenses, and overhead.

### Step-by-Step Guide

1. **Define the cost modeling scenario**  
   Create or modify a Python script in the `/analyses/iterations` directory. This script:
   - Specifies which parts to model
   - Sets up manufacturing steps and parameters (batch size, process time, etc.)
   - Loads input definitions for materials, machines, consumables, facility settings, and overhead

2. **Prepare input files**  
   Input specifications must be stored as JSON files under the `/inputs` directory:
   - `/inputs/parts/`: defines the geometry and manufacturing steps of each part
   - `/inputs/materials/`, `/inputs/equipment/`, `/inputs/consumables/`: specify technical and cost parameters
   - `/inputs/facility_wide/`: includes shared facility-level inputs like rent, shifts per day, etc.

3. **Run a modeling iteration**  
   Run the appropriate script from the `/workspace` directory.
   ```bash
   python workspace/<file_name>.py
   ```

4. **Review the output**  
   Outputs (e.g., detailed cost breakdowns, sensitivity plots) will be saved in the `/workspace/outputs/` directory. These may include:
   - `.csv` files: tabulated cost breakdowns
   - `.png` or `.pdf` files: cost comparison or sensitivity plots

5. **Customize for new scenarios**  
   To analyze a new component or modify assumptions:
   - Create a new input JSON under `/inputs`
   - Create a new iteration script or modify an existing one in `/analyses/iterations`
   - Adjust operational assumptions as needed (e.g., energy prices, machine utilization)