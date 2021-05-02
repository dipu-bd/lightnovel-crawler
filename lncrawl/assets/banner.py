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


def get_color_banner():
    text = banner_text.strip('\n')
    version_text = Icons.BOOK + Style.BRIGHT + ' Lightnovel Crawler v' + get_value() + Style.RESET_ALL
    link_text = Icons.LINK + Fore.BLUE + ' https://github.com/dipu-bd/lightnovel-crawler' + Fore.RESET
    text = text.replace('<version>', Fore.RESET + version_text + Fore.YELLOW)
    text = text.replace('<link>', Fore.RESET + link_text + Fore.YELLOW)
    text = Fore.YELLOW + text + Fore.RESET
    return text
