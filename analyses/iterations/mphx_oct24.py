from typing import Mapping

from pbcm.cost_items.Facility import Facility
from pbcm.cost_items.Consumable import Consumable
from pbcm.cost_items.Machine import Machine
from pbcm.cost_items.Material import Material
from pbcm.cost_items.Overhead import Overhead
from pbcm.cost_items.Process import ProcessStep
from parts.Mphx import Mphx
from tools.json_tools import object_from_json, objects_from_dir


def create_hx_oct24():
    # parts from JSON file
    model_hx = object_from_json('../input_data/parts/mphx.json', Mphx, level='base')

    # MATERIAL from JSON file
    model_material = object_from_json('../input_data/materials/polycarbonate.json', Material)

    # MACHINES from JSON files
    im_machine = object_from_json('../input_data/equipment/injection_molding_machine.json', Machine)
    lw_machine = object_from_json('../input_data/equipment/laser_welding_machine.json', Machine)
    as_machine = object_from_json('../input_data/equipment/assembly_machine.json', Machine)
    # gl_machine = object_from_json('../input_data/equipment/gluing_machine.json', Machine)
    dc_machine = object_from_json('../input_data/equipment/die_cutting_machine.json', Machine,  level='base')

    # CONSUMABLES from JSON files
    consumables: Mapping[str, Consumable] = objects_from_dir('../input_data/consumables', Consumable)
    im_machine.add_consumables(consumables)


    # PROCESS
    inj_mold = ProcessStep("Injection Molding", im_machine, 14/3600, 1, model_hx.n_fins)
    die_cut_im = ProcessStep("Die Cutting IM Plate", dc_machine, 22/3600, 2, model_hx.n_fins)
    die_cut_film = ProcessStep("Die Cutting Film", dc_machine, 22/3600, 2, model_hx.n_fins)
    las_weld = ProcessStep("Laser Welding", lw_machine, 49/3600, 4, model_hx.n_fins)
    # gluing = ProcessStep("IM plate and film gluing", gl_machine, 49 / 3600, 4)
    assembly = ProcessStep("Assembly",as_machine, 2/3600, 1, model_hx.n_fins)

    mfg_process = {
        "Injection Molding": inj_mold,
        "Die Cutting IM Plate": die_cut_im,
        "Die Cutting Film": die_cut_film,
        "Laser Welding": las_weld,
        "Assembly" : assembly
    }

    # FACILITY-WIDE INPUTS/ASSUMPTIONS
    over = object_from_json('../input_data/facility_wide/overhead_inputs.json', Overhead, level='base')
    fac = object_from_json('../input_data/facility_wide/facility_inputs.json', Facility, level='base')
    return model_hx, model_material, mfg_process, over, fac

