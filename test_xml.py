import xml.etree.ElementTree as ET
from wiki_xml_handler import wiki_xmlhandler
main_wiki_xmlhandler = wiki_xmlhandler('pages.xml')
# print('===================Lincoln===================')
# print(main_wiki_xmlhandler.get_doc('Abraham Lincoln'))
s = main_wiki_xmlhandler.get_doc('ArtificalLanguages')
root = ET.fromstring(s)
revision = root.find('revision')
wikitext = revision.find('text').text
print(wikitext)