import json
import sys

from sel_aci.aci import ACI
from sel_aci.objs import AciContract, AciSubject, AciTenant, CustomWorksheet, set_j2_env


def get_aci_objects(aci: str, username: str, password: str, tenant: str) -> None:
    aci = ACI(aci=aci, username=username, password=password)
    aci.login()

    # Create Filters file
    filters = aci.get_object_names(tenant=tenant, obj_type="filters")
    filename = f"existing-filter-names--{tenant}.txt"
    with open(filename, "w") as fout:
        for name in filters:
            fout.write(f"{name}\n")
    print(f"Filters created at: {filename}")

    # Create Contracts file
    contracts = aci.get_object_names(tenant=tenant, obj_type="contracts")
    filename = f"existing-contracts--{tenant}.txt"
    with open(filename, "w") as fout:
        fout.write(json.dumps(contracts))
    print(f"Contracts created at: {filename}")


def parse_aci_data(aci_data, existing_filter_names, existing_contracts):
    new_filters = []
    new_contracts_dict = {}

    # Begin Parsing
    for line in aci_data:
        my_filter = line.filters()
        contract_name = line.contract_name

        # Create filter
        if my_filter.name not in existing_filter_names:
            new_filters.append(my_filter)
            existing_filter_names.append(my_filter.name)

        # Create Subject
        new_subject = AciSubject(
            filter_name=my_filter.name,
            action=line.action,
            protocol=line.protocol,
            description=line.subject_description,
        )
        # Check it doesn't already exist for this contract
        if contract_name in existing_contracts.keys():
            if new_subject.name in existing_contracts[contract_name]:
                # Don't need to create it
                continue
        else:
            # Add to newly created or create now
            if contract_name not in new_contracts_dict.keys():
                rg_new_contract = AciContract(
                    name=contract_name, subjects=[new_subject]
                )
                new_contracts_dict[contract_name] = rg_new_contract
            else:
                if new_subject not in new_contracts_dict[contract_name]:
                    new_contracts_dict[contract_name].subjects.append(new_subject)
    # Turn the dict into list of AciContract's
    new_contracts = [contract for contract in new_contracts_dict.values()]
    return new_filters, new_contracts


def main(excel_filename, filter_names, contract_names, output_file, version):

    # Create File
    ws = CustomWorksheet(excel_filename=excel_filename)
    # Jinja Environment
    set_j2_env(version)

    aci_data = ws.get_contracts()

    if aci_data:
        tenant = aci_data[0].tenant
    else:
        print("Error pulling contracts from file.")
        sys.exit()

    new_filters, new_contracts = parse_aci_data(aci_data, filter_names, contract_names)

    # Begin output
    print("\n")
    if not output_file:
        filename = f"{tenant}-new-objects.json"
    else:
        filename = f"{output_file}"
    output = AciTenant(name=tenant, filters=new_filters, contracts=new_contracts)
    output.to_file(filename)

    print("Done.\n")
