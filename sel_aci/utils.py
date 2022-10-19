from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from rich.pretty import pprint
import sys
from sel_aci.aci import ACI
from sel_aci.objs import CustomWorksheet


def get_filter_name(contract):
    filter_name = f"{contract['protocol'].upper()}_"
    if contract["src_port"]:
        filter_name += f"Src_{contract['src_port']}_"
    if contract["dst_port"]:
        filter_name += f"Dst_{contract['dst_port']}_"
    filter_name += "Fltr"

    return filter_name


def get_contract_name(contract):
    contract_name = f"{contract['src_epg']}_to_{contract['dst_epg']}_Con"

    return contract_name


def create_filter(filter_name, contract, j2_env):
    j2_filter = j2_env.get_template("new_filter.jinja2")
    print(f"creating: {filter_name}")

    src_port_from = "unspecified"
    src_port_to = "unspecified"
    dst_port_from = "unspecified"
    dst_port_to = "unspecified"

    src_port = contract["src_port"]
    dst_port = contract["dst_port"]
    if src_port:
        if "-" in src_port:
            src_port_from, src_port_to = src_port.split("-")
        else:
            src_port_from = src_port_to = src_port
    if dst_port:
        if "-" in dst_port:
            dst_port_from, dst_port_to = dst_port.split("-")
        else:
            dst_port_from = dst_port_to = dst_port

    kwargs = {"FILTER_NAME": filter_name,
              "PROTOCOL": contract["protocol"],
              "SRC_PORT_FROM": src_port_from,
              "SRC_PORT_TO": src_port_to,
              "DST_PORT_FROM": dst_port_from,
              "DST_PORT_TO": dst_port_to,
              }
    new_filter = j2_filter.render(**kwargs)

    return new_filter


def create_contract(contract, contract_name, filter_name, j2_env):
    j2_contract = j2_env.get_template("new_contract.jinja2")
    print(f"creating: {contract_name}")

    subject_name = f"mysubject1-{filter_name}"

    kwargs = {
        "CONTRACT_NAME": contract_name,
        "SUBJECT_NAME": subject_name,
        "FILTER_NAME": filter_name,
        "ACTION": contract["action"]
    }

    new_contract = j2_contract.render(**kwargs)
    return new_contract


def create_subject(filter_name, subject_name, contract, j2_env):
    j2_subject = j2_env.get_template("new_subject.jinja2")

    kwargs = {
        "SUBJECT_NAME": subject_name,
        "FILTER_NAME": filter_name,
        "ACTION": contract["action"]
    }
    return 'h'


def get_epg_provider_consumers(contract, contract_name, filter_name):
    associations = {}
    if "Dst" in filter_name:
        associations["consumer"] = contract["src_epg"]
        associations["provider"] = contract["dst_epg"]
    elif "Src" in filter_name:
        associations["consumer"] = contract["dst_epg"]
        associations["provider"] = contract["src_epg"]

    return associations


def create_contracts(excel_filename, filters):
    # Create File
    ws = CustomWorksheet(excel_filename=excel_filename)
    # Jinja Environment
    j2_env = Environment(
        loader=FileSystemLoader("sel_aci/templates"),
        lstrip_blocks=True,
        trim_blocks=True,
        undefined=StrictUndefined,
    )

    contracts = ws.get_contracts()
    if contracts:
        tenant = contracts[0]["tenant"]
    else:
        print("Error pulling contracts from file.")
        sys.exit()
    pprint(contracts)

    new_filters = []
    new_contracts = []
    contract_names = []
    new_subjects = {}
    new_epg_associations = []
    for contract in contracts:
        # Get Names
        filter_name = get_filter_name(contract)
        contract_name = get_contract_name(contract)

        # Create filter
        if filter_name not in filters:
            new_filter = create_filter(filter_name, contract, j2_env)
            new_filters.append(new_filter)
            filters.append(filter_name)

        # Create contract if needed
        if contract_name not in contract_names:
            new_contract = create_contract(contract, contract_name, filter_name, j2_env)
            new_contracts.append(new_contract)
            contract_names.append(contract_name)

        # Create new subject
        subject_name = "2"
        new_subject = create_subject(filter_name, subject_name, contract, j2_env)
        if not new_subjects.get(contract_name):
            new_subjects[contract_name] = [new_subject]
        else:
            new_subjects[contract_name].append(new_subject)

        #association = get_epg_provider_consumers(contract, contract_name, filter_name)

    # Create JSON for Filters
    j2_tenant_base = j2_env.get_template("base_tenant.jinja2")
    with open(f"new-filters-{tenant}.json", "w") as fout:
        fout.write(j2_tenant_base.render(ITEMS=new_filters))

    # Create JSON for Contracts
    with open(f"new-contracts-{tenant}.json", "w") as fout:
        fout.write(j2_tenant_base.render(ITEMS=new_contracts))

    # Create JSON to associate EPG's to contracts


def get_filters(aci: str, username: str, password: str, tenant: str) -> None:
    aci = ACI(aci=aci, username=username, password=password)
    aci.login()

    filters = aci.get_filters(tenant="Heroes")
    filename = f"filters-{tenant}.txt"

    with open(filename, "w") as fin:
        for name in filters:
            fin.write(f"{name}\n")
    print(f"Filters created at: {filename}")
