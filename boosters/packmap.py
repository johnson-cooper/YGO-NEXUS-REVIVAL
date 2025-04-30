# packmap.py
import requests
import json
import pandas
import os

def get_yugioh_set_info():
    url = "https://db.ygoprodeck.com/api/v7/cardsets.php"
    response = requests.get(url)
    return response.json()

SET_INFO = pandas.json_normalize(get_yugioh_set_info())
SET_DATE_MAP = dict(zip(SET_INFO['set_code'], SET_INFO['tcg_date']))

PACK_MAP = {
    "LOB": 1,
    "MRD": 2,
    "MRL": 3,
    "PSV": 4,
    "LON": 5,
    "LOD": 6,
    "PGD": 7,
    "MFC": 8,
    "DCR": 9,
    "IOC": 10,
    "AST": 11,
    "SOD": 12,
    "RDS": 13,
    "FET": 14,
    "TLM": 15,
    "CRV": 16,
    "EEN": 17,
    "SOI": 18,
    "EOJ": 19,
    "POTD": 20,
    "CDIP": 21,
    "STON": 22,
    "FOTB": 23,
    "TAEV": 24,
    "GLAS": 25,
    "PTDN": 26,
    "LODT": 27,
    "TDGS": 28,
    "CSOC": 29,
    "CRMS": 30,
    "RGBT": 31,
    "ANPR": 32,
    "HA01": 33,
    "DT01": 33,
    "SOVR": 34,
    "ABPF": 35,
    "TSHD": 36,
    "HA02": 37,
    "DT02": 37,
    "DREV": 38,
    "STBL": 39,
    "HA03": 40,
    "DT03": 40,
    "STOR": 41,
    "HA04": 42,
    "DT04": 42,
    "EXVC": 43, # OCG IMPORTS
    "ORCS": 43,
    "GENF": 43,
    "PHSW": 43,
    "NUMH": 43,
    "LVAL": 43,
    "ABYR": 43,
    "CBLZ": 43,
    "JOTL": 43,
    "HA05": 44,
    "DT05": 44,
    "DT06": 44,
    "SDK": 45, # Structure Deck Wave DM Era
    "SDY": 45,
    "SDJ": 45,
    "SDP": 45,
    "SYE": 45,
    "SKE": 45,
    "SDMA": 45,
    "SD10": 46, # Structure Decks GX Era
    "SD09": 46,
    "SDRL": 46,
    "SD7": 46,
    "SD8": 46,
    "SD1": 46,
    "SD2": 46,
    "SD3": 46,
    "SD4": 46,
    "SD5": 46,
    "SD6": 46,
    "SDMM": 47, # Structure Decks 5Ds Era 
    "5DS1": 47,
    "SDSC": 47,
    "SDWS": 47,
    "SDDE": 47,
    "5DS2": 47,
    "5DS3": 47,
    "SDDL": 47,
    "SDLS": 47,
    "MDP2": 48, # Promos DM
    "DB2": 48,
    "PP01": 48,
    "LCJW": 48,
    "EP1": 48,
    "GLD4": 48,
    "SP1": 48,
    "DBT": 48,
    "MOV": 49, # Promos DM Pt 2.
    "MP1": 49,
    "GLD1": 49,
    "TFK": 49,
    "SDD": 49,
    "DOR": 49,
    "PCK": 49,
    "LC02": 50, # Promos GX
    "CT07": 50,
    "PP02": 50,
    "GX02": 50,
    "JUMP": 50,
    "GX03": 50,
    "GX04": 50,
    "GX05": 50,
    "GX06": 50,
    "GX1": 50,
    "YDB1": 50,
    "WC08": 50,
    "PRC1": 51, # Promos 5Ds
    "YMP1": 51,
    "CT08": 51,
    "WB01": 51,
    "TF05": 51,
    "TF04": 51,
    "YDT1": 51,
    "DPK": 52, # DP DM
    "DP1": 52, # DP GX
    "DP2": 52,
    'DPCT': 52,
    "DP04": 52,
    "DP06": 52,
    "DP07": 52,
    "DP03": 52,
    "DP05": 52,
    "DP10": 53, # DP 5Ds
    "DP09": 53,
    "DP08": 53,
    "DP11": 53,
    "TP1": 54, # Tournament Packs 1 & 2
    "TP2": 54,
    "TP3": 54,
    "TP4": 54,
    "TP5": 54,
    "TP6": 54,
    "TP7": 54,
    "TP8": 54,
    "CP01": 55, # Champion Packs
    "CP02": 55,
    "CP03": 55,
    "CP04": 55,
    "CP05": 55,
    "CP06": 55,
    "CP07": 55,
    "CP08": 55,
    "AP01": 56, # Astral Packs
    "AP02": 56,
    "AP03": 56,
    "AP04": 56,
    "AP05": 56,
    "AP06": 56,
    "AP07": 56,
    "AP08": 56,
    "WC09": 56,
    "WC10": 56,
    "WC11": 56,
    "OP01": 58, # Pack Filler
    "YGLD": 58,
    "SS03": 58,
    "SBC1": 58,
    "SBTK": 58,
    "OP01": 58,
    'WCPP': 58, 
    'LCYW': 58, 
    'OP04': 58,
    'DL10': 58,
    'DL9': 58, 
    'PCJ': 58,
    'DOD': 58, 
    'KC01': 59,
    'SP2': 59, # Pack Filler
    'CT2': 59, 
    'SP02': 59, 
    'UE02': 59, 
    'CMC': 59, 
    'DLG1': 59, 
    'YG02': 59, 
    'YG03': 59, 
    'YR05': 59, 
    'DDY1': 59, 
    'YAP1': 59, 
    'YG05': 59, 
    'CT15': 59, 
    'BP01': 59, 
    'YG07': 59, 
    'YF01': 59, 
    'JMPS': 59,
    'YG08': 59, 
    'LCGX': 59,
    'OP03': 1
}

CUR_MAP="SBTK"

def get_yugioh_card_info():
    url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes&enddate=2013-01-01&dateregion=ocg"
    response = requests.get(url)
    return response.json()

def otn_card_info():
    url = "https://raw.githubusercontent.com/johnson-cooper/YGO-NEXUS-REVIVAL/refs/heads/main/boosters/packs_and_cards.txt"
    response = requests.get(url)
    return response.text.split("\r\n")

IGNORE_SET = []

def munge_set_code(x):
    try:
        return ';'.join([y['set_code'].split('-')[0] for y in x if y['set_code'].split('-')[0] not in IGNORE_SET])
    except:
        return ''
    
def get_earliest_release(x):
    try:
        packs = x.get('cs').split(';')
        for pack in PACK_MAP.keys():
            if pack in packs:
                return pack
            
        ret_val = x.get('cs').split(';')[x.get('tcg_dates').split(';').index(min([y for y in x.get('tcg_dates').split(';') if y != '']))]
        return ret_val
    except:
        return ''
    
# Some cards need remapping in a more 1-to-1 manner after general mapping because the Names are not quite aligned
REMAPS = {
    '42': 44,
    '13': 20,
    '15': 22,
    "17": 24,
    "16": 23,
    '12': 19,
    "19": 26,
    "20": 27,
    "23": 30,
    "25": 32,
    "26": 33,
    '47': 52,
    '51': 52,
    '54': 52, # Contains Zephyrus...
    '18': 25,
    '50': 52,
    '48': 52,
    '52': 52,
    '53': 52,
    "46": 42,
    '10': 17, # EEN
    '11': 18, # SOI
    '56': 43,
    '1': 45, # Contains a mix of DB1 cards...
    '3': 46, # DRV1
    '5': 12, # Soul of the Duelist
    '6': 13, # Rise of Destiny
    '8': 15,
    '9': 16,
    '30': 39,
    '28': 36,
    '40': 44,
    '41': 44,
    '39': 42,
    '49': 49,
    '55': 59,
    '45': 35
}

if __name__ == "__main__":
    card_info = pandas.json_normalize(get_yugioh_card_info()['data'])
    card_info['cs'] = card_info['card_sets'].apply(lambda x: munge_set_code(x))
    card_info = card_info.loc[card_info['cs'] != '']
    card_info['tcg_dates'] = card_info['cs'].apply(lambda x: ';'.join([SET_DATE_MAP.get(y, '') for y in x.split(';')]))
    card_info['earliest_release'] = card_info.apply(get_earliest_release, axis=1)
    card_info['konami_id'] =card_info['misc_info'].apply(lambda x: x[0].get('konami_id'))
    otn_info = otn_card_info()
    otn_name = [x.rsplit('Card Name: ', 1)[1] for x in otn_info if 'Card Name: ' in x]
    otn_internal_id = [int(x.split('Internal ID: ')[1].split(',')[0]) for x in otn_info if 'Card Name: ' in x]
    otn_id = [x.split(',')[0].split('ID: ')[1] for x in otn_info if 'Card Name: ' in x]
    otn_df = pandas.DataFrame({'name': otn_name, 'target_internal_id':otn_internal_id, 'old_id': otn_id, 'new_pack_id': 0})
    joint_df = otn_df.set_index('name').join(card_info.set_index('name'), how='left')
    joint_df.new_pack_id = [PACK_MAP[x] if x in PACK_MAP else 0 for x in joint_df.earliest_release]

    joint_df.new_pack_id = [57 if x in ['57','58','59'] else y for x,y in zip(joint_df.old_id, joint_df.new_pack_id)]
    # Remap stuff that wasn't named well...
    joint_df.new_pack_id = [REMAPS.get(x, 0) if y == 0 else y for x,y in zip(joint_df.old_id, joint_df.new_pack_id)]
    joint_df.loc[joint_df.index == 'Red-Eyes B. Dragon', 'new_pack_id'] = 1
    joint_df.loc[joint_df.index.str.startswith('Speed Spell'), 'new_pack_id'] = 57
    joint_df.loc[joint_df.index.str.startswith('Blackwing - Zephyrus the Elite'), 'new_pack_id'] = 53

    # Write to json.
    joint_df[['target_internal_id', 'new_pack_id']].to_json('config.json', orient='records')
