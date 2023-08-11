from pathlib import Path
from termcolor import colored


# Creation of path in the current script directory
FORMATTED_OUTPUT = Path.cwd().joinpath("output.txt") # save output directory
CACHE = Path.cwd().joinpath("cache.json")  # cache directory
FORMATTER_CHAR: str = "*"
FORMATTER_TIMES: int = 70

SLEEP_FOR: float = .008

colorful_site_names: dict = {
    "Hotlink": colored("Hotlink", "white", "on_red", attrs=['bold'], force_color=True),
    "Maxis": colored("Maxis", "white", "on_green", attrs=['bold'], force_color=True),
    "Business": colored("Business", "white", "on_blue", attrs=['bold'], force_color=True)
}

positives = ('yes', 'y', '')
negatives = ('no', 'n')
