from typing import Mapping

from pbcm.cost_items.Facility import Facility
from pbcm.cost_items.Consumable import Consumable
from pbcm.cost_items.Machine import Machine
from pbcm.cost_items.Overhead import Overhead
from pbcm.cost_items.Process import ProcessStep
from parts.Part import Part
from tools.json_tools import object_from_json, objects_from_dir
from pathlib import Path
import json


def create_hx(join_method: str = "Laser Welding", level: str = 'base'):
    # parts from JSON file
    model_hx = object_from_json('../input_data/parts/mphx_sabic/mphx.json', Part, level=level)
    all_parts: Mapping[str, Part] = objects_from_dir('../input_data/parts/mphx_sabic/', Part, level=level)
    # Only include subparts that belong to the MPHX parent
    subparts: Mapping[str, Part] = {k: v for k, v in all_parts.items() if getattr(v, 'parent_part', None) == 'MPHX'}
    model_hx.add_subparts(subparts)

    # MACHINES from JSON files
    im_machine = object_from_json('../input_data/equipment/injection_molding_machine_SABIC.json', Machine, level=level)
    lw_machine = object_from_json('../input_data/equipment/laser_welding_machine.json', Machine, level=level)
    as_machine = object_from_json('../input_data/equipment/assembly_machine.json', Machine, level=level)
    gl_machine = object_from_json('../input_data/equipment/gluing_machine.json', Machine, level=level)
    dc_machine = object_from_json('../input_data/equipment/die_cutting_machine.json', Machine, level=level)
    lifting_machine = object_from_json('../input_data/equipment/lifting_machine.json', Machine, level=level)

    # CONSUMABLES from JSON files
    consumables: Mapping[str, Consumable] = objects_from_dir('../input_data/consumables', Consumable, level=level)
    im_machine.add_consumables(consumables)
    lw_machine.add_consumables(consumables)
    as_machine.add_consumables(consumables)
    gl_machine.add_consumables(consumables)
    dc_machine.add_consumables(consumables)
    lifting_machine.add_consumables(consumables)


    # Load process parameter files (time_cycle, batch_size) from input_data/processes
    processes_dir = Path('../input_data/processes')
    process_defs = {}
    if processes_dir.exists():
        for fp in processes_dir.glob('*.json'):
            try:
                with open(fp, 'r') as f:
                    pdata = json.load(f)
                name = pdata.get('name')
                if name:
                    process_defs[name] = pdata
            except Exception:
                # ignore malformed files
                continue

    # helper to get time_cycle (in hours) and batch_size for a given process name
    def _get_proc_params(proc_name: str, default_cycle_sec: float = 0, default_batch: int = 1):
        pdata = process_defs.get(proc_name, {})
        tc = pdata.get('time_cycle', default_cycle_sec)
        # If time_cycle is a dict with levels, pick requested level
        if isinstance(tc, dict):
            tc_val = tc.get(level, tc.get('base', default_cycle_sec))
        else:
            tc_val = tc
        # time_cycle is in seconds; convert to hours
        try:
            tc_seconds = float(tc_val)
        except Exception:
            tc_seconds = float(default_cycle_sec)
        tc_hours = tc_seconds / 3600.0

        bs = pdata.get('batch_size', default_batch)
        try:
            bs_val = int(bs)
        except Exception:
            bs_val = default_batch
        return tc_hours, bs_val

    # PROCESS
    im_plate_subpart = next(sp for sp in model_hx.subs.values() if sp.name == "IM Plate")
    tc_plate, bs_plate = _get_proc_params("Injection Molding Plate")
    inj_mold_plate = ProcessStep("Injection Molding Plate", im_machine, tc_plate, bs_plate, part=im_plate_subpart, mat_use=1, parts_per_unit= im_plate_subpart.count)

    header_subpart = next(sp for sp in model_hx.subs.values() if sp.name == "Header")
    tc_header, bs_header = _get_proc_params("Injection Molding Header")
    inj_mold_header = ProcessStep("Injection Molding Header", im_machine, tc_header, bs_header, part=header_subpart, mat_use=1, parts_per_unit=header_subpart.count)

    endcap_subpart = next(sp for sp in model_hx.subs.values() if sp.name == "Endcap")
    tc_endcap, bs_endcap = _get_proc_params("Injection Molding Endcap")
    inj_mold_endcap = ProcessStep("Injection Molding Endcap", im_machine, tc_endcap, bs_endcap, part=endcap_subpart, mat_use=1, parts_per_unit=endcap_subpart.count)

    tc_die_cut_film, bs_die_cut_film = _get_proc_params("Die Cutting Film")
    die_cut_film = ProcessStep("Die Cutting Film", dc_machine, tc_die_cut_film, bs_die_cut_film, part=im_plate_subpart, mat_use=0, parts_per_unit= im_plate_subpart.count)

    tc_las_weld, bs_las_weld = _get_proc_params("Laser Welding")
    las_weld = ProcessStep("Laser Welding", lw_machine, tc_las_weld, bs_las_weld, part=im_plate_subpart, mat_use=0, parts_per_unit= im_plate_subpart.count)

    tc_gluing, bs_gluing = _get_proc_params("Gluing")
    gluing = ProcessStep("Gluing", gl_machine, tc_gluing, bs_gluing, part=im_plate_subpart, mat_use=0, parts_per_unit= im_plate_subpart.count)

    tc_fs_assembly, bs_fs_assembly = _get_proc_params("Fin Stack Assembly")
    fs_assembly = ProcessStep("Fin Stack Assembly",as_machine, tc_fs_assembly, bs_fs_assembly, mat_use=0, parts_per_unit= 1)

    tc_mod_assembly, bs_mod_assembly = _get_proc_params("Module Assembly")
    mod_assembly = ProcessStep("Module Assembly",as_machine, tc_mod_assembly, bs_mod_assembly, mat_use=0, parts_per_unit= 1)

    tc_rack_assembly, bs_rack_assembly = _get_proc_params("Rack Assembly")
    rack_assembly = ProcessStep("Rack Assembly",lifting_machine, tc_rack_assembly, bs_rack_assembly, mat_use=0, parts_per_unit= 1/14)

    mfg_process = {
        "Injection Molding Plate": inj_mold_plate,
        "Injection Molding Header": inj_mold_header,
        "Injection Molding Endcap": inj_mold_endcap,
        "Die Cutting Film": die_cut_film,
        "Fin Stack Assembly" : fs_assembly,
        "Module Assembly": mod_assembly,
        "Rack Assembly": rack_assembly,
    }

    # Include only the selected join step
    jm = (join_method or "").strip().lower()
    if jm == "laser welding":
        mfg_process["Laser Welding"] = las_weld
    elif jm == "gluing":
        mfg_process["Gluing"] = gluing
    else:
        # Default to gluing if unrecognized
        mfg_process["Gluing"] = gluing

    # FACILITY-WIDE INPUTS/ASSUMPTIONS
    over = object_from_json('../input_data/facility_wide/overhead_inputs.json', Overhead, level=level)
    fac = object_from_json('../input_data/facility_wide/facility_inputs.json', Facility, level=level)
    return model_hx, mfg_process, over, fac
