import correct_asserts
from openpyxl.workbook.workbook import Workbook
from rich.pretty import pprint

from sel_acl.objs import ACE, ACL, CustomWorksheet
from sel_acl.utils import (
    create_contract_file,
    ew_checker,
    get_acl_from_file,
    get_addrgroups_from_file,
    get_initial_data,
    remove_self,
)

# test_acl_regex = correct_asserts.test_acl


def test_regex():
    filename = "./tests/acl_tests.txt"
    test_acl = get_acl_from_file(filename, "From-Vlan1")
    test_acl.acl = None
    correct_acl = correct_asserts.test_acl

    # print(correct_asserts.test_acl)
    assert test_acl == correct_acl


def test_eastwest():
    correct_contracts = []
    contracts = []

    #for num in [1]:
    for num in [1, 2, 3, 4, 5, 6, 7]:
        filename = "./tests/acl_tests.txt"
        test_acl = get_acl_from_file(filename, f"From-Vlan{num}")
        test_acl.acl = None

        # TEST DATA
        ws, mig_data = get_initial_data(
            excel_filename="./tests/test_mig_data.xlsx", vlan=num
        )
        ew_mig_data = ws.get_tenant_rows(tenant=mig_data.tenant)
        ew_mig_data = remove_self(vlan_name=mig_data.vlan_name, ew_mig_data=ew_mig_data)
        addr_groups = get_addrgroups_from_file("./tests/objects_test.ios")

        ew_aces, ew_contracts, _ = ew_checker(
            ew_mig_data=ew_mig_data,
            acl=test_acl,
            addr_groups=addr_groups,
            my_mig_data=mig_data,
        )

        correct_contract = getattr(correct_asserts, f"vlan{num}_contracts")
        correct_contracts.append(correct_contract)
        contracts.append(ew_contracts)

    assert contracts == correct_contracts

    # UNCOMMENT AND RUN MANUALLY TO GET CONTRACT OUTPUT
    # print("\nACES:")
    # print("------")
    # for ace in ew_aces:
    #     print(ace.output_cidr())
    #
    # # If manually running, contracts will be [[]]
    # if not contracts[0]:
    #     contracts = None
    # else:
    #     contracts = contracts[0]
    #
    # if contracts:
    #     print(contracts)
    #     create_contract_file(
    #         contracts=contracts, filename=f"contracts-{mig_data.vlan_name}.xlsx"
    #     )


if __name__ == "__main__":
    # test_regex()
    test_eastwest()
