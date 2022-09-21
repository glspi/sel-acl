import correct_asserts
from rich.pretty import pprint

from sel_acl.utils import (
    get_acl_from_file,
    get_addrgroups_from_file,
    get_initial_data,
    get_portgroups_from_file,
    ns_ew_combined,
)


def test_regex():
    filename = "./tests/acl_tests.txt"
    test_acl = get_acl_from_file(filename, "From-Vlan1")
    test_acl.acl = None
    correct_acl = correct_asserts.test_acl
    assert test_acl == correct_acl


def test_groups():
    filename = "./tests/acl_tests.txt"
    test_acl = get_acl_from_file(filename, "From-Vlan1")
    test_acl.acl = None
    assert test_acl.obj_groups() == correct_asserts.correct_groups


def test_compare_with():
    acl_1 = get_acl_from_file("./tests/acl_tests.txt", "Overlaps-Acl1")
    acl_2 = get_acl_from_file("./tests/acl_tests.txt", "Overlaps-Acl2")
    addr_groups = get_addrgroups_from_file("./tests/objects_test.ios")
    port_groups = get_portgroups_from_file("./tests/objects_test.ios")

    acl_1.set_cidrs_ports(addr_groups=addr_groups, port_groups=port_groups)
    acl_2.set_cidrs_ports(addr_groups=addr_groups, port_groups=port_groups)

    overlaps = acl_1.compare_with(acl_2)

    test_overlaps = []
    for overlap in overlaps:
        test_overlaps.append((overlap[0].output_cidr(), overlap[1].output_cidr()))
    assert test_overlaps == correct_asserts.correct_overlaps


def test_east_west():
    correct_contracts = []
    contracts = []

    # for num in [1]:
    for num in [1, 2, 3, 4, 5, 6, 7]:
        filename = "./tests/acl_tests.txt"
        test_acl = get_acl_from_file(filename, f"From-Vlan{num}")
        if test_acl:
            test_acl.acl = None

            # TEST DATA
            dict = get_initial_data(
                excel_filename="./tests/mig_data_test.xlsx",
                vlan=num,
                obj_groups="./tests/objects_test.ios",
            )

            ew_aces, ew_contracts = ns_ew_combined(
                ws=dict["ws"],
                mig_data=dict["mig_data"],
                addr_groups=dict["addr_groups"],
                acl=test_acl,
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
    # pprint(contracts)
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
    # test_groups()
    # test_eastwest()
    # test_compare()
    test_cidrs_ports()
