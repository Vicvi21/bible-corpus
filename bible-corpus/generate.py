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
    def create_xml_from_deprecated(cls,
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
                                try:
                                    verse.text = RandomBible.substitute_verse(
                                                                verse.text, 
                                                                unique_chars,
                                                                space_as_char)
                                except:
                                    pass
        results_path = results_folder + new_language + ".xml"
        xml_tree.write(results_path, encoding="unicode")
        return results_path

    @classmethod
    def create_xml_from(cls,
                        bible, 
                        results_folder):
        
        # Don't get unique chars
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
        new_language += "(keeps long_char frequency)"
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
        
        # Dictionary of counter chars
        char_bag = RandomBible.count_character(unique_chars,
                                               xml_text)
        
        # Scramble characters
        RandomBible.scramble_verses(char_bag, xml_text)
        print("Finished: " + new_language)
        
        results_path = results_folder + new_language + ".xml"
        xml_tree.write(results_path, encoding="unicode")
        return results_path
    
    @classmethod
    def count_character(cls, unique_chars, xml_text):
        count = {}
        for book in xml_text.getchildren()[0]:
            if book.attrib.get("type", "") == "book" :
                for chapter in book:
                    if chapter.attrib.get("type", "") == "chapter" :
                        for verse in chapter:
                            if verse.attrib.get("type", "") == "verse" :
                                if verse.text:
                                    for character in unique_chars:
                                        count[character] = count.get(character, 
                                                                 0) + \
                                                            verse.text.lower(
                                                                ).count(
                                                                    character)
        return count
    
    @classmethod
    def scramble_verses(cls, char_bag, xml_text):
        uniform_bag = RandomBible.probabilities_to_uniform_bag(
                                        RandomBible.char_bag_to_probability(
                                                                    char_bag)
                                                               )
        for book in xml_text.getchildren()[0]:
            if book.attrib.get("type", "") == "book" :
                for chapter in book:
                    if chapter.attrib.get("type", "") == "chapter" :
                        for verse in chapter:
                            new_verse = ""
                            if verse.attrib.get("type", "") == "verse" :
                                if verse.text:
                                    uniform_bag = RandomBible.\
                                                probabilities_to_uniform_bag(
                                                    RandomBible.\
                                                        char_bag_to_probability(
                                                                        char_bag)
                                                                             )
                                    if uniform_bag == []:
                                        uniform_bag = RandomBible.to_uniform_bag(
                                                                        char_bag
                                                                        )
                                    for character in verse.text.lower():
                                        if character in char_bag.keys():
                                            new_character = random.sample(
                                                            uniform_bag, 
                                                            1)[0]
                                            new_verse += new_character
                                            char_bag[new_character] = \
                                                        char_bag[new_character] - 1
    
                                        else:
                                            new_verse += character
                            verse.text = new_verse
    
    @classmethod
    def to_uniform_bag(cls, char_bag):
        bag = []
        for character, freq in char_bag.keys():
            for _ in range(freq):
                bag.append(character)
        return bag
    
    @classmethod
    def char_bag_to_probability(cls, char_bag):
        probabilities = {}
        total = 0
        for _, frequency in char_bag.items():
            total += frequency
        
        if total == 0:
            return {}
        
        for character, frequency in char_bag.items():
            probabilities[character] = frequency/total
        return probabilities
    
    @classmethod
    def probabilities_to_uniform_bag(cls, proba_bag):
        uniform_bag = []
        for character, probability in proba_bag.items():
            for _ in range(int(probability*100)):
                uniform_bag.append(character)
        return uniform_bag
    
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