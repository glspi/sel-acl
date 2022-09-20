import correct_asserts
from rich.pretty import pprint

from sel_acl.utils import (
    create_contract_file,
    get_acl_from_file,
    get_initial_data,
    ns_ew_combined,
)


def test_regex():
    filename = "./tests/acl_tests.txt"
    test_acl = get_acl_from_file(filename, "From-Vlan1")
    test_acl.acl = None
    correct_acl = correct_asserts.test_acl
    assert test_acl == correct_acl


def test_test():
    t = get_acl_from_file("huh.txt", "test")
    t.acl = None
    pprint(t)


def test_groups():
    filename = "./tests/acl_tests.txt"
    test_acl = get_acl_from_file(filename, "From-Vlan1")
    test_acl.acl = None
    assert test_acl.groups() == correct_asserts.correct_groups


def test_eastwest():
    correct_contracts = []
    contracts = []

    #for num in [1]:
    for num in [1, 2, 3, 4, 5, 6, 7]:
        filename = "./tests/acl_tests.txt"
        test_acl = get_acl_from_file(filename, f"From-Vlan{num}")
        test_acl.acl = None

        # TEST DATA
        ws, mig_data, addr_groups, _ = get_initial_data(
            excel_filename="./tests/mig_data_test.xlsx",
            vlan=num,
            obj_groups="./tests/objects_test.ios",
        )

        ew_aces, ew_contracts = ns_ew_combined(
            ws=ws,
            mig_data=mig_data,
            addr_groups=addr_groups,
            acl=test_acl,
            direction="in",
        )

        correct_contract = getattr(correct_asserts, f"vlan{num}_contracts")
        correct_contracts.append(correct_contract)
        contracts.append(ew_contracts)

    assert contracts == correct_contracts

    #UNCOMMENT AND RUN MANUALLY TO GET CONTRACT OUTPUT
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
    #test_groups()
    #test_eastwest()
    test_test()
