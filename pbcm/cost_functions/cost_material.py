from pbcm.cost_items.Material import Material
from parts.Mphx import Mphx
# from parts.Socket import Socket
# from parts.Pipe import Pipe

def calc_mat_cost(apv, epv, mat: Material, hx: Mphx, scrap_rate_mat, recycle_rate_mat):
    """This function calcs the cost_functions of material used in each parts. This includes cost_functions for scrap material resulting from
    process steps and from rejected parts units. The function evenly distributes cost_functions for rejected parts across accepted parts produced
    in one year.
    """

    if hx.volume>0:
        mat_build_unit = mat.density * (hx.volume * (1 + scrap_rate_mat))
        mat_use_tot = epv * mat_build_unit
        mat_cost_tot = mat.price_mat * mat_use_tot
        mat_cost_unit = mat_cost_tot / apv
    elif hx.wt_plate>0:
        mat_build_unit = hx.wt_plate * hx.n_fins * 2 * (1 + scrap_rate_mat)
        mat_use_tot = epv * mat_build_unit
        mat_cost_tot = mat.price_mat * mat_use_tot
        mat_cost_unit = mat_cost_tot / apv

    return mat_cost_unit

# def calc_mat_cost(apv, epv, mat: Material, parts: Mphx, scrap_rate_mat, recycle_rate_mat):
#     """This function calcs the cost_functions of material used in each parts. This includes cost_functions for scrap material resulting from
#     process steps and from rejected parts units. The function evenly distributes cost_functions for rejected parts across accepted parts produced
#     in one year.
#     """
#     mat_build_unit = mat.density * (parts.volume * (1 + scrap_rate_mat))
#     mat_trapped_unit = mat.density * parts.pin_array_void_volume
#     mat_use_unit = (mat_build_unit + mat_trapped_unit * (1-recycle_rate_mat))
#     mat_use_tot = epv * mat_use_unit
#     mat_cost_tot = mat.price_mat * mat_use_tot
#     mat_cost_unit = mat_cost_tot / apv
#
#     return mat_cost_unit

# def calc_mat_cost_socket(apv, epv, mat: Material, sc: Socket, scrap_rate_mat, recycle_rate_mat):
#     """This function calcs the cost_functions of material used in each parts. This includes cost_functions for scrap material resulting from
#     process steps and from rejected parts units. The function evenly distributes cost_functions for rejected parts across accepted parts produced
#     in one year.
#     """
#     mat_build_unit = mat.density * (sc.volume * (1 + scrap_rate_mat))
#     mat_use_unit = mat_build_unit
#     mat_use_tot = epv * mat_use_unit
#     mat_cost_tot = mat.price_mat * mat_use_tot
#     mat_cost_unit = mat_cost_tot / apv
#
#     return mat_cost_unit
#
# def calc_mat_cost_pipe(apv, epv, mat: Material, pp: Pipe, scrap_rate_mat, recycle_rate_mat):
#     """This function calcs the cost_functions of material used in each parts. This includes cost_functions for scrap material resulting from
#     process steps and from rejected parts units. The function evenly distributes cost_functions for rejected parts across accepted parts produced
#     in one year.
#     """
#     mat_build_unit = mat.density * (pp.volume * (1 + scrap_rate_mat))
#     mat_use_unit = mat_build_unit
#     mat_use_tot = epv * mat_use_unit
#     mat_cost_tot = mat.price_mat * mat_use_tot
#     mat_cost_unit = mat_cost_tot / apv
#
#     return mat_cost_unit