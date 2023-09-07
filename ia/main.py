"""
Compilation report
https://adviserinfo.sec.gov/compilation
"""

"""
Question to answer... how much AUM managed in the USA? 
- federal and state
""" 
import xml.etree.ElementTree as ET

def parse_firm(firm, is_state):
    firm_data = {}
    
    # Parse Info
    firm_data['Info'] = firm.find('Info').attrib
    
    # Parse Main Address
    firm_data['MainAddr'] = firm.find('MainAddr').attrib
    
    # Parse Mailing Address
    mailing = firm.find('MailingAddr')
    firm_data['MailingAddr'] = mailing.attrib if mailing is not None else {}
    
    # For convenience
    firm_data['FederalRgstn'] = not is_state
    
    # Parse Registration
    if is_state:
        firm_data['StateRgstn'] = [{'Rgltr': rgltr.attrib} for rgltr in firm.findall('./StateRgstn/Rgltrs/Rgltr')]
    else:
        firm_data['Rgstn'] = firm.find('Rgstn').attrib
    
    # Parse Notice Filed States
    if not is_state:
        firm_data['NoticeFiled'] = [{'States': state.attrib} for state in firm.findall('./NoticeFiled/States')]
    
    # Parse Filing
    firm_data['Filing'] = firm.find('Filing').attrib
    
    # Parse FormInfo
    form_info = {}
    
    part1A = firm.find('./FormInfo/Part1A')
    part1A_info = {}
    for item in part1A:
        part1A_info[item.tag] = item.attrib
        web_addrs = item.findall('WebAddrs/WebAddr')
        if web_addrs:
            part1A_info[item.tag]['WebAddrs'] = [web.text for web in web_addrs]
    form_info['Part1A'] = part1A_info

    part1B = firm.find('./FormInfo/Part1B') if is_state else None
    if part1B:
        part1B_info = {}
        for item in part1B:
            part1B_info[item.tag] = item.attrib
        form_info['Part1B'] = part1B_info
    
    firm_data['FormInfo'] = form_info
    
    return firm_data

def flatten_dict(d, parent_key='', sep='.'):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if k == 'StateRgstn':
            for i, elem in enumerate(v):
                state_abbr = elem.get('Rgltr', {}).get('Cd', i)
                elem_key = f"{new_key}.{state_abbr}"
                items.update(flatten_dict(elem, elem_key, sep=sep).items())
        elif k == 'NoticeFiled':
            for i, elem in enumerate(v):
                state_abbr = elem.get('States', {}).get('RgltrCd', i)
                elem_key = f"{new_key}.{state_abbr}"
                items.update(flatten_dict(elem, elem_key, sep=sep).items())
        elif isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            for i, elem in enumerate(v):
                if isinstance(elem, dict):
                    items.update(flatten_dict(elem, f"{new_key}[{i}]", sep=sep))
                else:
                    items[f"{new_key}[{i}]"] = elem
        else:
            items[new_key] = v
    return {k.replace('.States', '').replace('.Rgltrs', ''): v for k, v in items.items()}

def flatten_list_of_dicts(list_of_dicts):
    return [flatten_dict(d) for d in list_of_dicts]

def print_aum(flattened_firms):
    federal_total_aum = 0
    state_total_aum = 0

    for firm in flattened_firms:
        if firm.get('FederalRgstn'):
            federal_total_aum += float(firm.get('FormInfo.Part1A.Item5F.Q5F2C', 0))
        else:
            state_total_aum += float(firm.get('FormInfo.Part1A.Item5F.Q5F2C', 0))
        formatted_federal_total_aum = f"${int(federal_total_aum):,}"
        formatted_state_total_aum = f"${int(state_total_aum):,}"

    print(f"Federal Total AUM: {formatted_federal_total_aum}")
    print(f"State Total AUM: {formatted_state_total_aum}")

def main():
    federal_tree = ET.parse('./ia/data/IA_FIRM_SEC_Feed_09_06_2023.xml')
    state_tree = ET.parse('./ia/data/IA_FIRM_STATE_Feed_09_06_2023.xml')
    
    all_firms = []
    for tree in [federal_tree, state_tree]:
        root = tree.getroot()
        
        is_state = ""
        if root.tag == 'IAPDFirmSECReport':
            is_state = False
        elif root.tag == 'IAPDFirmStateReport':
            is_state = True
        else:
            raise "unknown tree"
        
        for firm in root.findall('./Firms/Firm'):
            parsed_firm = parse_firm(firm, is_state)
            all_firms.append(parsed_firm)

    flattened_firms = flatten_list_of_dicts(all_firms)
    
    print_aum(flattened_firms)
    
if __name__ == '__main__':
    main()
