from enum import Enum


class OutputFormat(str, Enum):
    json = "json"
    epub = "epub"
    web = "web"
    text = "text"
    pdf = "pdf"
    mobi = "mobi"
    docx = "docx"
    rtf = "rtf"
    fb2 = "fb2"
    azw3 = "azw3"
    lit = "lit"
    lrf = "lrf"
    oeb = "oeb"
    pdb = "pdb"
    rb = "rb"
    snb = "snb"
    tcr = "tcr"

    def __str__(self) -> str:
        return self.value
