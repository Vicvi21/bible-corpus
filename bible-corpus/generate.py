# -*- coding:utf8 -*-

from bible import Bible

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import re
import random


class RandomBible(object):

    @classmethod
    def create_xml_from(cls,
                        bible, 
                        results_folder, 
                        space_as_char):
        
        unique_chars = bible.unique_chars
        original_path = bible.file_path
        
        xml_tree = ET.ElementTree(file=original_path)
        
        xml_root = xml_tree.getroot()
        xml_header, xml_text = xml_root.getchildren()
        
        language_info = xml_header.find("profileDesc"
                                        ).find("langUsage"
                                               ).find("language")
                                               
        original_language = language_info.text
        stripped_language = original_language.strip()
        new_language = stripped_language + " random"
        if space_as_char:
            new_language += "(space as character)"
        language_info.text = original_language.rstrip().replace(
                                                            stripped_language, 
                                                            "") + \
                             new_language + \
                             original_language.lstrip().replace(
                                                            stripped_language, 
                                                            "")
        
        language_info.attrib["iso639"] = language_info.attrib["iso639"] + \
                                                                        "_rdm"
        language_info.attrib["id"] = language_info.attrib["id"] + "_rdm"
        
        for book in xml_text.getchildren()[0]:
            if book.attrib.get("type", "") == "book" :
                for chapter in book:
                    if chapter.attrib.get("type", "") == "chapter" :
                        for verse in chapter:
                            if verse.attrib.get("type", "") == "verse" :
                                verse.text = RandomBible.substitute_verse(
                                                                verse.text, 
                                                                unique_chars,
                                                                space_as_char)
        results_path = results_folder + new_language + ".xml"
        xml_tree.write(results_path)
        return results_path
        
    @classmethod
    def generate_from(cls,
                      bible, 
                      results_folder, 
                      space_as_char):
        results_path = RandomBible.create_xml_from(bible, 
                                                   results_folder, 
                                                   space_as_char)
        return Bible.from_path(results_path)
    
    @classmethod
    def substitute_verse(cls, raw_verse, bag_of_characters, space_as_char):
        if space_as_char:
            bag_of_characters.add(" ")
        new_verse = ""
        for letter in list(raw_verse):
            if letter.lower() in bag_of_characters:
                new_letter = random.sample(bag_of_characters, 1)[0]
                if letter.isupper():
                    new_letter = new_letter.upper()
                new_verse += new_letter
            else:
                new_verse += letter
        return new_verse