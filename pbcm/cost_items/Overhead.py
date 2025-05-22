from copy import copy


class Overhead:

    def __init__(self, mgmt_ratio=0, mgmt_salary=0, qa_inspect_frac=0, qa_time=0, qa_salary=0, cp_cost=0, legal_frac=0,
                 legal_price=0, insure_price=0, hr_price=0, clean_price=0, admin_ratio=0, admin_salary=0, acct_price=0,
                 space_emp=0, crate_price=0, inventory_time=0, inventory_stack_height=0, misc_space_frac=0, office_life=0, office_build_price=0,
                 supply_price=0, it_price=0, building_util=0, raw=None):
        """
        Initializes an object to hold input_data used to calculate Overhead cost_functions.

        Parameters
        ----------
        mgmt_ratio: float
            Ratio of managers to laborers. Values must be in [0,1].

        mgmt_salary: float or int
            Manager annual salary ($).

        qa_inspect_frac: float
            Fraction of completed parts that are subjected to a non-destructive QA inspection. Values must be in [0,1].

        qa_time: float or int
            Time (hrs) required to complete non-destructive QA inspection of one parts.

        qa_salary: float or int
            QA inspector annual salary ($).

        cp_cost: float or int
            Annual cost_functions ($) of regulatory compliance.

        legal_frac: float or int
            Legal services (hrs) required per parts.

        legal_price: float or int
            Cost for legal services ($/hr).

        insure_price: float or int
            Annual cost_functions ($) for insurance.

        hr_price: float or int
            Annual cost_functions ($/employee) for HR services.

        clean_price: float or int
            Monthly cost_functions ($/m^2) for cleaning services.

        admin_ratio: float
            Ratio of administrative employees to laborers. Values must be in [0,1].

        admin_salary: float or int
            Administrative employee annual salary ($).

        acct_price: float or int
            Annual cost_functions ($) for accounting services.

        space_emp: float or int
            Office space (m^2/employee) required for each employee.

        crate_price: float or int
            Cost ($) for parts packing crate.

        inventory_time: float or int
            Inventory (days) of completed parts stored in facility.

        misc_space_frac: : float or int
            Ratio of miscellaneous space (hallways, storage, bathrooms, etc.) to shop floor space.

        office_life: float or int
            Depreciation lifetime (yrs) for office space buildout (furnishings, interior walls, cubicles, etc.).

        office_build_price: float or int
            Cost ($/m^2) to build out office space.

        supply_price: float or int
            Cost per employee ($/employee) for office supplies and equipment.

        it_price: float or int
            Cost per employee ($/employee) for IT equipment and software.

        building_util: float or int
            Cost ($/m^2) for general utilities (lighting, water, trash, etc.).

        raw: dict
            Dictionary of raw data for objects created from an external data file.

        """
        # management
        self.mgmt_ratio = mgmt_ratio
        self.mgmt_salary = mgmt_salary

        # quality assurance
        self.qa_inspect_frac = qa_inspect_frac
        self.qa_time = qa_time
        self.qa_salary = qa_salary

        # administrative staff
        self.admin_ratio = admin_ratio
        self.admin_salary = admin_salary

        # human resources
        self.hr_price = hr_price

        # compliance
        self.cp_cost = cp_cost

        # legal
        self.legal_frac = legal_frac
        self.legal_price = legal_price

        # insurance
        self.insure_price = insure_price

        # accounting
        self.acct_price = acct_price

        # office space
        self.space_emp = space_emp
        self.office_life = office_life
        self.office_build_price = office_build_price

        # inventory space
        self.inventory_time = inventory_time
        self.inventory_stack_height = inventory_stack_height

        # misc space
        self.misc_space_frac = misc_space_frac

        # cleaning
        self.clean_price = clean_price

        # office supplies
        self.supply_price = supply_price

        # IT equipment
        self.it_price = it_price

        # packaging
        self.crate_price = crate_price

        # building general utilities
        self.building_util = building_util


        self.raw = raw

    def copy(self, **kwargs) -> "Overhead":
        """Creates a copy of the object, updates attributes for specified kwargs, and returns updated object."""

        res = copy(self)
        for k, v in kwargs:
            setattr(res, k, v)
        return res
