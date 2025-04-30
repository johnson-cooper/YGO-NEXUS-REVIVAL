import requests

def get_yugioh_card_info():
    url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes&enddate=2012-01-01&dateregion=ocg"
    response = requests.get(url)
    data = response.json()['data']
    card_map = {x.get('id'): x.get('misc_info', [{}])[0].get('konami_id', None) for x in data}
    return card_map

ID_TO_KID = get_yugioh_card_info()

class ydc():
    def __init__(self):
        pass
    def from_ydk(self, ydk_file):
        with open(ydk_file, "r") as file:
            ydk_data = file.read()
            ydk_data = ydk_data.split("\n")
            main_idx = ydk_data.index('#main')
            extra_idx = ydk_data.index('#extra')
            side_idx = ydk_data.index('!side')
            main = ydk_data[main_idx+1:extra_idx]
            extra = ydk_data[extra_idx+1:side_idx]
            if len(main) < 40:
                raise ValueError("Main deck must have at least 40 cards.")
            if len(main) > 60:
                raise ValueError("Main deck must have at most 60 cards.")
            # Perhaps add check to make sure main deck files dont contain syncros, fusion
            # Add check to make sure extra deck contains only syncros, fusion
            if len(extra) > 15:
                raise ValueError("Extra deck must have at most 15 cards.")
            self.main = main
            self.extra = extra
    def to_ydc(self, ydc_file):
        main = [ID_TO_KID[int(x)] for x in self.main]
        extra = [ID_TO_KID[int(x)] for x in self.extra]
        # According to files these are all the headers
        # [52225, 52428, 42278, 19538] # Seems to be 60% of decks
        # [52225, 52428, 36736, 18329] # Seems to be 40% of decks...
        # [52225, 52428, 8575, 16759] # For all structure deck?
        # [52225, 52428, 57883, 19427] # For 1 structure deck?
        ydc_header = [52225, 52428, 42278, 19538]
        ydc_data = ydc_header + [len(main)] + main + [len(extra)] + extra + [0]
        bd = [x.to_bytes(length=2, byteorder='little') for x in ydc_data]
        to_write = bd[0]
        for x in bd[1:]:
            to_write += x
        with open(ydc_file, "wb") as file:
            file.write(to_write)

# example usage.
# converter = ydc()
# converter.from_ydk(ydk_file)
# converter.to_ydc(ydc_file)