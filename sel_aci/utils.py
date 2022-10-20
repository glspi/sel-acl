import sys
import os

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from rich.pretty import pprint

from sel_aci.aci import ACI
from sel_aci.objs import AciContract, AciSubject, CustomWorksheet

# def get_epg_provider_consumers(contract, contract_name, filter_name):
#     associations = {}
#     if "Dst" in filter_name:
#         associations["consumer"] = contract["src_epg"]
#         associations["provider"] = contract["dst_epg"]
#     elif "Src" in filter_name:
#         associations["consumer"] = contract["dst_epg"]
#         associations["provider"] = contract["src_epg"]
#
#     return associations


def get_aci_objects(aci: str, username: str, password: str, tenant: str) -> None:
    aci = ACI(aci=aci, username=username, password=password)
    aci.login()

    for obj_type in ("filters", "contracts"):
        objs = aci.get_object_names(tenant=tenant, obj_type=obj_type)
        filename = f"{obj_type}-{tenant}.txt"

        with open(filename, "w") as fin:
            for name in objs:
                fin.write(f"{name}\n")
        print(f"{obj_type.capitalize()} created at: {filename}")


def main(excel_filename, filter_names, contract_names):
    # Create File
    ws = CustomWorksheet(excel_filename=excel_filename)
    # Jinja Environment
    j2_env = Environment(
        loader=FileSystemLoader("sel_aci/templates"),
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=StrictUndefined,
    )

    aci_data = ws.get_contracts()

    if aci_data:
        tenant = aci_data[0].tenant
    else:
        print("Error pulling contracts from file.")
        sys.exit()

    new_filters = []
    new_contracts = []
    new_subjects = {}
    new_epg_associations = []
    for line in aci_data:
        my_filter = line.filters()
        contract_name = line.contract_name
        # Create filter
        if my_filter.name not in filter_names:
            new_filter = my_filter.to_json()
            new_filters.append(new_filter)
            filter_names.append(my_filter.name)

        # Create contract if needed
        if contract_name not in contract_names:
            new_contract = AciContract(name=contract_name, filter_name=my_filter.name)
            new_contracts.append(new_contract.to_json())
            contract_names.append(contract_name)

        # Create new subject

        new_subject = AciSubject(
            filter_name=my_filter.name,
            action=line.action,
            protocol=line.protocol,
            description=line.subject_description,
        )

        if not new_subjects.get(contract_name):
            new_subjects[contract_name] = {
                "subjects": [new_subject.to_json()],
                "names": [new_subject.name],
            }
        elif new_subject.name not in new_subjects[contract_name]["names"]:
            new_subjects[contract_name]["subjects"].append(new_subject.to_json())
            new_subjects[contract_name]["names"].append(new_subject.name)

        # association = get_epg_provider_consumers(contract, contract_name, filter_name)

    # Begin output
    print("\n")
    j2_tenant_base = j2_env.get_template("base_tenant.jinja2")
    os.makedirs("aci-json", exist_ok=True)

    # Create JSON for Filters
    if new_contracts:
        filename = f"aci-json/new-filters-{tenant}.json"
        print(f"New filters found, creating at: {filename}")
        with open(filename, "w") as fout:
            fout.write(j2_tenant_base.render(ITEMS=new_filters))

    # Create JSON for Contracts
    if new_contracts:
        filename = f"aci-json/new-contracts-{tenant}.json"
        print(f"New contracts found, creating at: {filename}")
        with open(filename, "w") as fout:
            fout.write(j2_tenant_base.render(ITEMS=new_contracts))

    # Create JSON to associate EPG's to contracts
    # no?

    # Create JSON for Subjects
    if len(new_subjects.keys()) > 0:
        j2_contract_base = j2_env.get_template("base_contract.jinja2")
        for contract_name in new_subjects.keys():
            filename = f"aci-json/new-subjects-{contract_name}.json"
            print(f"New subjects found, creating at: {filename}")
            subjects = new_subjects[contract_name]["subjects"]
            with open(filename, "w") as fout:
                fout.write(j2_contract_base.render(ITEMS=subjects))

    print("Done.\n")
