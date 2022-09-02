import requests
from PIL import Image, ImageFilter
from io import BytesIO

def make_game_banner(banner, logo1, logo2):
    raw_background = requests.get(banner, stream=True).raw
    raw_logo1 = requests.get(logo1, stream=True).raw
    raw_logo2 = requests.get(logo2, stream=True).raw
    background = Image.open(raw_background)
    team1 = Image.open(raw_logo1)
    team2 = Image.open(raw_logo2)

    blured_background = background.filter(ImageFilter.GaussianBlur(10))

    team1, team2 = scale_team_logos(blured_background, team1, team2)

    positions = get_logos_positions(blured_background, team1, team2) 
    blured_background.paste(team1, (positions[0], positions[1]), team1)
    blured_background.paste(team2, (positions[2], positions[3]), team2)
    bufer = BytesIO()
    blured_background.save(bufer, format = 'png')
    bufer.seek(0)

    return bufer


def scale_team_logos(banner, logo1, logo2):
    base_height = int(banner.height / 3)
    logos = []
    for logo in (logo1, logo2):
        hpercent = (base_height / float(logo.height))
        wsize = int((float(logo.width) * float(hpercent)))
        logo = logo.resize((wsize, base_height), Image.ANTIALIAS)
        logos.append(logo)

    return logos


def get_logos_positions(banner, logo1, logo2):
    banner_mid_height = int(banner.height / 2)
    base_position = (int(banner.width / 4), banner_mid_height, banner.width - int(banner.width / 4), banner_mid_height)  
    logo1_mid_height = int(logo1.height / 2) 
    logo2_mid_height = int(logo2.height / 2) 
    logo1_mid_width = int(logo1.width / 2)
    logo2_mid_width = int(logo2.width / 2)
    x1_pos = int(banner.width / 4) - logo1_mid_width
    x2_pos = banner.width - int(banner.width / 4) - logo2_mid_width
    y1_pos = banner_mid_height - logo1_mid_height 
    y2_pos = banner_mid_height - logo1_mid_height 
    position = (x1_pos, y1_pos, x2_pos, y2_pos)  

    return position

