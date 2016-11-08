# -*- coding:utf-8 -*-

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from collections import OrderedDict


old_testament = OrderedDict({
                            "b.GEN" : "Genesis ",
                            "b.EXO" : "Exodus ",
                            "b.LEV" : "Leviticus ",
                            "b.NUM" : "Numbers ",
                            "b.DEU" : "Deuteronomy ",
                            "b.JOS" : "Joshua ",
                            "b.JDG" : "Judges ",
                            "b.RUT" : "Ruth ",
                            "b.1SA" : "1 Samuel ",
                            "b.2SA" : "2 Samuel ",
                            "b.1KI" : "1 Kings ",
                            "b.2KI" : "2 Kings ",
                            "b.1CH" : "1 Chronicles ",
                            "b.2CH" : "2 Chronicles ",
                            "b.EZR" : "Ezra ",
                            "b.NEH" : "Nehemiah ",
                            "b.EST" : "Esther ",
                            "b.JOB" : "Job ",
                            "b.PSA" : "Psalms ",
                            "b.PRO" : "Proverbs ",
                            "b.ECC" : "Ecclesiastes ",
                            "b.SON" : "Song of Solomon ",
                            "b.ISA" : "Isaiah ",
                            "b.JER" : "Jeremiah ",
                            "b.LAM" : "Lamentations ",
                            "b.EZE" : "Ezekiel",
                            "b.DAN" : "Daniel ",
                            "b.HOS" : "Hosea",
                            "b.JOE" : "Joel",
                            "b.AMO" : "Amos",
                            "b.OBA" : "Obadiah",
                            "b.JON" : "Jonah",
                            "b.MIC" : "Micah",
                            "b.NAH" : "Nahum",
                            "b.HAB" : "Habakkuk",
                            "b.ZEP" : "Zephaniah",
                            "b.HAG" : "Haggai",
                            "b.ZEC" : "Zechariah",
                            "b.MAL" : "Malachi"
                            })

new_testament = OrderedDict({
                            "b.MAT" : "Matthew",
                            "b.MAR" : "Mark",
                            "b.LUK" : "Luke",
                            "b.JOH" : "John",
                            "b.ACT" : "Acts (of the Apostles)",
                            "b.ROM" : "Romans",
                            "b.1CO" : "1 Corinthians",
                            "b.2CO" : "2 Corinthians",
                            "b.GAL" : "Galatians",
                            "b.EPH" : "Ephesians",
                            "b.PHI" : "Philippians",
                            "b.COL" : "Colossians",
                            "b.1TH" : "1 Thessalonians",
                            "b.2TH" : "2 Thessalonians",
                            "b.1TI" : "1 Timothy",
                            "b.2TI" : "2 Timothy",
                            "b.TIT" : "Titus",
                            "b.PHM" : "Philemon",
                            "b.HEB" : "Hebrews",
                            "b.JAM" : "James",
                            "b.1PE" : "1 Peter",
                            "b.2PE" : "2 Peter",
                            "b.1JO" : "1 John",
                            "b.2JO" : "2 John",
                            "b.3JO" : "3 John",
                            "b.JUD" : "Jude",
                            "b.REV" : "Revelation"
                            })

all_books = old_testament.copy()
all_books.update(new_testament)


class Verse(object):
    
    def __init__(self, xml_node, parent_chapter):
        self._id = xml_node.attrib['id']
        self._type = xml_node.attrib['type']
        self._parent = parent_chapter
        
        try:
            self.text = xml_node.text.strip()
        except:
            self.text = ""
        
    def __repr__(self, *args, **kwargs):
        return "(Book {0}, chapter {1}, verse {2}) \n {3}".format(
                                        all_books[self._parent._parent._id],
                                        self._parent._parent._id,
                                        self._parent._id,
                                        len(self._id),
                                        str(self)
                                        )
        
    def __str__(self, *args, **kwargs):
        return self.text
    
    def unique_chars(self):
        return set(list(self.text))
    
    def char_frequency(self):
        res = {}
        chars = list(self.text)
        for char in chars:
            res[char] = res.get(char, 0) + 1
        return res
            

class Chapter(object):
    
    def __init__(self, xml_node, parent_book):
        self._id = xml_node.attrib['id']
        self._type = xml_node.attrib['type']
        self._parent = parent_book
        
        verses = []
        for child in xml_node:
            if child.attrib.get("type", "") == "verse" :
                verses.append(Verse(child, self))
                
        self.verses = verses

    def __repr__(self, *args, **kwargs):
        return "Book {0} ({1}), chapter {2} with {3} verses".format(
                                                all_books[self._parent._id],
                                                self._parent._id,
                                                self._id,
                                                len(self.verses)
                                                )
        
    def unique_chars(self):
        res = set({})
        for verse in self.verses:
            res = res.union(verse.unique_chars())
        return res
    
    def char_frequency(self):
        res = {}
        for verse in self.verses:
            partial_freq = verse.char_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return res


class Book(object):
    
    def __init__(self, xml_node, bible_parent):
        self._id = xml_node.attrib['id']
        self._type = xml_node.attrib['type']
        self._parent = bible_parent
        
        chapters = []
        for child in xml_node:
            if child.attrib.get("type", "") == "chapter" :
                chapters.append(Chapter(child, self))
                
        self.chapters = chapters
        
    def __repr__(self, *args, **kwargs):
        return "Book {0} ({1}) with {2} chapters".format(all_books[self._id],
                                                   self._id,
                                                   len(self.chapters))
        
    def unique_chars(self):
        res = set({})
        for chapter in self.chapters:
            res = res.union(chapter.unique_chars())
        return res
    
    def char_frequency(self):
        res = {}
        for chapter in self.chapters:
            partial_freq = chapter.char_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return res


class BookSet(object):
    
    def __init__(self):
        self._old_testament = old_testament.copy()
        self._old_testament_idx = []
        
        self._new_testament = new_testament.copy()
        self._new_testament_idx = []
        
        self._all_books = all_books.copy()
        self._all_books_idx = []
        
        self.ids = self._all_books.keys()
        
        self._iter_idx = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            self._iter_idx += 1
            return self._all_books_idx[self._iter_idx - 1]
        except:
            self._iter_idx = 0
            raise StopIteration
    
    def __getitem__(self, value):
        if isinstance(value, int) or\
           isinstance(value, slice):
            return self._all_books_idx[value]
        else:
            return self._all_books[value]
    
    def __setitem__(self, key, value):
        if not isinstance(value, Book):
            raise ValueError("Not a Bible Book")
        
        if not key in self._all_books.keys():
            raise KeyError("Can't assign this slot")
        
        self._all_books[key]=value
        self._all_books_idx.append(value)
        
        if key in self._old_testament.keys():
            self._old_testament[key] = value
            self._old_testament_idx.append(value)
        else:
            self._new_testament[key] = value
            self._new_testament_idx.append(value)
            
    def add(self, book):
        dict_entry = book._id
        self[dict_entry] = book


class Bible(object):
    
    def __init__(self, file_path):
        self._xml_tree = ET.ElementTree(file=file_path)
        self.file_path = file_path
        
        xml_root = self._xml_tree.getroot()
        xml_header, xml_text = xml_root.getchildren()
        
        language_info = xml_header.find("profileDesc"
                                        ).find("langUsage"
                                               ).find("language")
                                               
        self.language = language_info.text.strip()
        self.iso639 = language_info.attrib["iso639"].strip()
        self.lang_id = language_info.attrib["id"].strip()
        
        script_info = xml_header.find("profileDesc"
                                        ).find("wsdUsage"
                                               ).find("writingSystem")
        self.encoding = script_info.attrib['id']
                
        books = BookSet()
        for child in xml_text.getchildren()[0]:
            if child.attrib.get("type", "") == "book" :
                books.add(Book(child, self))
        
        self.books = books
    
    def get_book_ids(self):
        return self.books.ids
    
    def get_book_set(self, *args):
        for arg in args:
            yield self.books[arg]
        
    def get_old_testament(self):
        return self.books._old_testament_idx
    
    def get_new_testament(self):
        return self.books._new_testament_idx
    
    def unique_chars(self):
        res = set({})
        for book in self.books:
            res = res.union(book.unique_chars())
        return res
    
    def char_frequency(self):
        res = {}
        for book in self.books:
            partial_freq = book.char_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return res

    def __repr__(self, *args, **kwargs):
        return "{0} (iso639={1}, {2})".format(self.language,
                                              self.iso639,
                                              self.encoding)