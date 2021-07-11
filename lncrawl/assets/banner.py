# -*- coding: utf-8 -*-

import re
from colorama.ansi import Fore, Style

from .icons import Icons
from .version import get_value

banner_text = r'''
╭╮╱╱╱╱╱╱╭╮╱╭╮╱╱╱╱╱╱╱╱╱╱╱╱╭╮╱╭━━━╮╱╱╱╱╱╱╱╱╱╭╮
┃┃╱╱╱╱╱╱┃┃╭╯╰╮╱╱╱╱╱╱╱╱╱╱╱┃┃╱┃╭━╮┃╱╱╱╱╱╱╱╱╱┃┃
┃┃╱╱╭┳━━┫╰┻╮╭╋━╮╭━━┳╮╭┳━━┫┃╱┃┃╱╰╋━┳━━┳╮╭╮╭┫┃╭━━┳━╮
┃┃╱╭╋┫╭╮┃╭╮┃┃┃╭╮┫╭╮┃╰╯┃┃━┫┃╱┃┃╱╭┫╭┫╭╮┃╰╯╰╯┃┃┃┃━┫╭╯
┃╰━╯┃┃╰╯┃┃┃┃╰┫┃┃┃╰╯┣╮╭┫┃━┫╰╮┃╰━╯┃┃┃╭╮┣╮╭╮╭┫╰┫┃━┫┃
╰━━━┻┻━╮┣╯╰┻━┻╯╰┻━━╯╰╯╰━━┻━╯╰━━━┻╯╰╯╰╯╰╯╰╯╰━┻━━┻╯
╱╱╱╱╱╭━╯┃ <version>
╱╱╱╱╱╰━━╯ <link>
'''

# banner_text = r'''
#       __...--~~~~~-._   _.-~~~~~--...__
#     //               `V'               \\ 
#    //      Lightnovel | Crawler         \\ 
#   //__...--~~~~~~-._  |  _.-~~~~~~--...__\\ 
#  //__.....----~~~~._\ | /_.~~~~----.....__\\
# ====================\\|//====================
#                     `---` <version>
#   <link>
# '''


# banner_text = r'''
#  _     _       _     _                        _    ____                    _  <version>
# | |   (_) __ _| |__ | |_ _ __   _____   _____| |  / ___|_ __ __ ___      _| | ___ _ __ 
# | |   | |/ _` | '_ \| __| '_ \ / _ \ \ / / _ \ | | |   | '__/ _` \ \ /\ / / |/ _ \ '__|
# | |___| | (_| | | | | |_| | | | (_) \ V /  __/ | | |___| | | (_| |\ V  V /| |  __/ |   
# |_____|_|\__, |_| |_|\__|_| |_|\___/ \_/ \___|_|  \____|_|  \__,_| \_/\_/ |_|\___|_|   
#          |___/       <link> 
# '''

def get_color_banner():
    text = banner_text.strip('\n')
    #' Lightnovel Crawler v' +
    version_text = Style.BRIGHT + 'v' + get_value() + Style.RESET_ALL
    link_text = Icons.LINK + Fore.CYAN + ' https://github.com/dipu-bd/lightnovel-crawler' + Fore.RESET
    text = text.replace('<version>', Fore.RESET + version_text + Fore.YELLOW)
    text = text.replace('<link>', Fore.CYAN + link_text + Fore.YELLOW)
    text = re.sub(r'(╱+)', Fore.RESET + Style.DIM + r'\1' + Style.RESET_ALL + Fore.YELLOW, text)
    text = Fore.YELLOW + text + Fore.RESET
    return text
