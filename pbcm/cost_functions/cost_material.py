from pathlib import Path
import json
from pbcm.cost_items.Process import ProcessStep


def _load_material(mat_choice: str) -> dict:
    mats_dir = Path(__file__).resolve().parents[2] / 'input_data' / 'materials'
    if not mat_choice or not mats_dir.exists():
        return {}
    wanted = mat_choice.lower()
    for p in mats_dir.iterdir():
        if not p.is_file() or p.suffix.lower() != '.json':
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        name = str(data.get('name_mat', '')).lower()
        if p.stem.lower() == wanted or name == wanted:
            return data
    return {}


def calc_mat_cost(annual_prod_vol: float, eff_prod_vol: float, ps: ProcessStep) -> float:
    """Per-step material cost per accepted unit based on ps.part and ps.mach.
    - If ps.mat_use == 0: return 0
    - weight_per_part = volume*density (if volume>0) else wt (if wt>0)
    - scrap_rate from ps.mach.scrap_rate; material from ../input_data/materials
    - eff_part_vol = eff_prod_vol * ps.parts_per_unit
    - mat_cost_tot = eff_part_vol* weight_per_part * (1 + scrap_rate*(1-recycling_rate)) * price_mat
    - mat_cost_unit = mat_cost_tot / annual_prod_vol
    """
    if not ps or getattr(ps, 'mat_use', 0) == 0:
        return 0.0

    part = getattr(ps, 'part', None)
    if part is None:
        return 0.0

    mat = _load_material(getattr(part, 'mat_choice', None))
    price_node = mat.get('price_mat', {}) if isinstance(mat, dict) else {}
    price_mat = (price_node.get('base', 0.0) if isinstance(price_node, dict) else float(price_node or 0.0)) or 0.0
    density = float(mat.get('density', 0.0) or 0.0)
    recycling_rate = float(mat.get('recycling_rate', 0.0) or 0.0)

    volume = float(getattr(part, 'volume', 0.0) or 0.0)
    wt = float(getattr(part, 'wt', 0.0) or 0.0)
    weight_per_part = volume * density if volume > 0 else (wt if wt > 0 else 0.0)
    scrap_rate = float(getattr(getattr(ps, 'mach', None), 'scrap_rate', 0.0) or 0.0)

    eff_part_vol = eff_prod_vol * float(getattr(ps, 'parts_per_unit', 1) or 1)
    mat_cost_tot = eff_part_vol * weight_per_part * (1 + scrap_rate * (1 - recycling_rate)) * price_mat
    mat_cost_unit = mat_cost_tot / float(annual_prod_vol)
    return mat_cost_unit
