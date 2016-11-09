# -*- coding:utf-8 -*-

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from collections import OrderedDict
import operator
import re

from bible_statistics import IndBibleStatistics


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
    
    def tokenize(self):
        temp_text = re.sub(r'[^\w\s]', 
                           '', 
                           self.text, 
                           re.UNICODE).lower()
        temp = temp_text.split(" ")
        while '' in temp:
            temp.remove('')
        return temp
    
    def unique_tokens(self):
        return set(self.tokenize())
    
    def unique_chars(self):
        return set(list(self.text))
    
    def token_frequency(self):
        res = {}
        tokens = self.tokenize()
        for token in tokens:
            res[token] = res.get(token, 0) + 1
        return res
    
    def char_frequency(self):
        res = {}
        chars = list(self.text)
        for char in chars:
            res[char] = res.get(char, 0) + 1
        return res
    
    def token_count(self):
        temp = self.tokenize()
        return len(temp)
    

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
    
    def unique_tokens(self):
        res = set({})
        for verse in self.verses:
            res = res.union(verse.unique_tokens())
        return res
    
    def unique_chars(self):
        res = set({})
        for verse in self.verses:
            res = res.union(verse.unique_chars())
        return res
    
    def token_frequency(self):
        res = {}
        for verse in self.verses:
            partial_freq = verse.token_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return res
    
    def char_frequency(self):
        res = {}
        for verse in self.verses:
            partial_freq = verse.char_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return res

    def token_count(self):
        res = 0
        for verse in self.verses:
            res += verse.token_count()
        return res

class Book(object):
    
    def __init__(self, xml_node):
        self._id = xml_node.attrib['id']
        self._type = xml_node.attrib['type']
        
        chapters = []
        for child in xml_node:
            if child.attrib.get("type", "") == "chapter" :
                chapters.append(Chapter(child, self))
                
        self.chapters = chapters
        
    def __repr__(self, *args, **kwargs):
        return "Book {0} ({1}) with {2} chapters".format(all_books[self._id],
                                                   self._id,
                                                   len(self.chapters))

    def unique_tokens(self):
        res = set({})
        for chapter in self.chapters:
            res = res.union(chapter.unique_tokens())
        return res

    def unique_chars(self):
        res = set({})
        for chapter in self.chapters:
            res = res.union(chapter.unique_chars())
        return res
    
    def token_frequency(self):
        res = {}
        for chapter in self.chapters:
            partial_freq = chapter.token_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return res
    
    def char_frequency(self):
        res = {}
        for chapter in self.chapters:
            partial_freq = chapter.char_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return res
    
    def token_count(self):
        res = 0
        for chapter in self.chapters:
            res += chapter.token_count()
        return res


class BookSet(object):
    
    def __init__(self):
        self._old_testament = Bible.old_testament.copy()
        self._old_testament_idx = [None for i in range(
                                                       len(
                                                           self._old_testament
                                                           )
                                                       )
                                   ]
        
        self._new_testament = Bible.new_testament.copy()
        self._new_testament_idx = [None for i in range(
                                                       len(
                                                           self._new_testament
                                                           )
                                                       )
                                   ]
        
        self._all_books = Bible.all_books.copy()
        self._all_books_idx = [None for i in range(len(self._all_books))]
        
        self.ids = self._all_books.keys()
        
        self._iter_idx = 0
    
    def __len__(self):
        true_size = 0
        for book in self._all_books_idx:
            if book is not None:
                true_size += 1
        return true_size
    
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
        
        self._all_books[key] = value
        arr_idx = list(self._all_books.keys()).index(key)
        self._all_books_idx[arr_idx] = value
        
        if key in self._old_testament.keys():
            self._old_testament[key] = value
            arr_idx = list(self._old_testament.keys()).index(key)
            self._old_testament_idx[arr_idx] = value
        else:
            self._new_testament[key] = value
            arr_idx = list(self._new_testament.keys()).index(key)
            self._new_testament_idx[arr_idx] = value

    def add(self, book):
        self[book._id] = book
        
    def books_with_id(self, *args):
        # return all
        if len(args) == 0:
            for book in self._all_books_idx:
                if book != None:
                    yield book
        else:
            for arg in args:
                yield self[arg]
                
    def total_books(self):
        total_old = 0
        for book in self._old_testament_idx:
            if not book is None:
                 total_old += 1
        
        total_new = 0
        for book in self._new_testament_idx:
            if not book is None:
                total_new += 1
                
        total = total_old + total_new
        return total_old, total_new, total
    
    def total_books_old_testament(self):
        return self.total_books()[0]
    
    def total_books_new_testament(self):
        return self.total_books()[1]
    
    def __repr__(self, *args, **kwargs):
        total_old, total_new, total = self.total_books()
        return "{0} books: {1} new testament and {2} old testament".format(
                                                                        total,
                                                                        total_new,
                                                                        total_old
                                                                        )


class Bible(IndBibleStatistics):
    
    old_testament = OrderedDict([
                             ("b.GEN", "Genesis"),
                             ("b.EXO", "Exodus"),
                             ("b.LEV", "Leviticus"),
                             ("b.NUM", "Numbers"),
                             ("b.DEU", "Deuteronomy"),
                             ("b.JOS", "Joshua"),
                             ("b.JDG", "Judges"),
                             ("b.RUT", "Ruth"),
                             ("b.1SA", "1 Samuel"),
                             ("b.2SA", "2 Samuel"),
                             ("b.1KI", "1 Kings"),
                             ("b.2KI", "2 Kings"),
                             ("b.1CH", "1 Chronicles"),
                             ("b.2CH", "2 Chronicles"),
                             ("b.EZR", "Ezra"),
                             ("b.NEH", "Nehemiah"),
                             ("b.EST", "Esther"),
                             ("b.JOB", "Job"),
                             ("b.PSA", "Psalms"),
                             ("b.PRO", "Proverbs"),
                             ("b.ECC", "Ecclesiastes"),
                             ("b.SON", "Song of Solomon"),
                             ("b.ISA", "Isaiah"),
                             ("b.JER", "Jeremiah"),
                             ("b.LAM", "Lamentations"),
                             ("b.EZE", "Ezekiel"),
                             ("b.DAN", "Daniel"),
                             ("b.HOS", "Hosea"),
                             ("b.JOE", "Joel"),
                             ("b.AMO", "Amos"),
                             ("b.OBA", "Obadiah"),
                             ("b.JON", "Jonah"),
                             ("b.MIC", "Micah"),
                             ("b.NAH", "Nahum"),
                             ("b.HAB", "Habakkuk"),
                             ("b.ZEP", "Zephaniah"),
                             ("b.HAG", "Haggai"),
                             ("b.ZEC", "Zechariah"),
                             ("b.MAL", "Malachi")
                            ])

    new_testament = OrderedDict([
                             ("b.MAT", "Matthew"),
                             ("b.MAR", "Mark"),
                             ("b.LUK", "Luke"),
                             ("b.JOH", "John"),
                             ("b.ACT", "Acts (of the Apostles)"),
                             ("b.ROM", "Romans"),
                             ("b.1CO", "1 Corinthians"),
                             ("b.2CO", "2 Corinthians"),
                             ("b.GAL", "Galatians"),
                             ("b.EPH", "Ephesians"),
                             ("b.PHI", "Philippians"),
                             ("b.COL", "Colossians"),
                             ("b.1TH", "1 Thessalonians"),
                             ("b.2TH", "2 Thessalonians"),
                             ("b.1TI", "1 Timothy"),
                             ("b.2TI", "2 Timothy"),
                             ("b.TIT", "Titus"),
                             ("b.PHM", "Philemon"),
                             ("b.HEB", "Hebrews"),
                             ("b.JAM", "James"),
                             ("b.1PE", "1 Peter"),
                             ("b.2PE", "2 Peter"),
                             ("b.1JO", "1 John"),
                             ("b.2JO", "2 John"),
                             ("b.3JO", "3 John"),
                             ("b.JUD", "Jude"),
                             ("b.REV", "Revelation")
                            ])
    
    all_books = old_testament.copy()
    all_books.update(new_testament)
    
    def __len__(self):
        return len(self.books)
    
    def __init__(self, book_set, **metadata):
        self.metadata = metadata
        for key, value in metadata.items():
            setattr(self, key, value)
            
        if not isinstance(book_set, BookSet):
            raise TypeError("Not a valid BookSet")
        
        self.books = book_set
        super(Bible, self).__init__()
        
    def bible_subset(self, *book_ids):
        books = BookSet()
        for book in self.get_book_set(*book_ids):
            books.add(book)
        return Bible(books, **self.metadata)
    
    @classmethod
    def get_all_book_ids(cls):
        return list(key for key, value in cls.all_books.items())
    
    @classmethod
    def get_old_testament_ids(cls):
        return list(key for key, value in cls.old_testament.items())
    
    @classmethod
    def get_new_testament_ids(cls):
        return list(key for key, value in cls.new_testament.items())

    @classmethod
    def from_path(cls, file_path):
        metadata = {}
        metadata['file_path'] = file_path
        
        xml_tree = ET.ElementTree(file=file_path)
        metadata['xml_tree'] = xml_tree
        
        xml_root = xml_tree.getroot()
        xml_header, xml_text = xml_root.getchildren()
        
        content_info = xml_header.find("fileDesc"
                                       ).find("extent")
        
        for child in content_info:
            if child.tag == "wordCount":
                metadata['reported_word_count'] = int(child.text)
            else:
                metadata['byte_count'] = int(child.text)
        
        language_info = xml_header.find("profileDesc"
                                        ).find("langUsage"
                                               ).find("language")
                                               
        metadata['language'] = language_info.text.strip()
        metadata['iso639'] = language_info.attrib["iso639"].strip()
        metadata['lang_id'] = language_info.attrib["id"].strip()
        
        script_info = xml_header.find("profileDesc"
                                        ).find("wsdUsage"
                                               ).find("writingSystem")
        metadata['encoding'] = script_info.attrib['id']
                
        books = BookSet()
        for child in xml_text.getchildren()[0]:
            if child.attrib.get("type", "") == "book" :
                books.add(Book(child))

        return Bible(books, **metadata)
    
    def get_book_set(self, *args):
        for arg in args:
            yield self.books[arg]
        
    def get_old_testament(self):
        return self.bible_subset(*Bible.get_old_testament_ids())
    
    def get_new_testament(self):
        return self.bible_subset(*Bible.get_new_testament_ids())
    
    def books_in_bible(self):
        return list(book_id for book_id, value in \
                            self.books._all_books.items() if \
                            not isinstance(value, str))
    
    def unique_tokens(self, *book_ids):
        res = set({})
        for book in self.books.books_with_id(*book_ids):
            res = res.union(book.unique_tokens())
        return res
    
    def unique_chars(self, *book_ids):
        res = set({})
        for book in self.books.books_with_id(*book_ids):
            res = res.union(book.unique_chars())
        return res
    
    def token_frequency(self, *book_ids):
        res = {}
        for book in self.books.books_with_id(*book_ids):
            partial_freq = book.token_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return OrderedDict(sorted(res.items(), 
                                  key=operator.itemgetter(1),
                                  reverse=True)
                           )
    
    def char_frequency(self, *book_ids):
        res = {}
        for book in self.books.books_with_id(*book_ids):
            partial_freq = book.char_frequency()
            for key in partial_freq.keys():
                res[key] = res.get(key, 0) + partial_freq[key]
        return OrderedDict(sorted(res.items(), 
                                  key=operator.itemgetter(1), 
                                  reverse=True)
                           )
    
    def token_count(self, *book_ids):
        res = 0
        for book in self.books.books_with_id(*book_ids):
            res += book.token_count()
        return res

    def __repr__(self, *args, **kwargs):
        return "{0} (iso639={1}, {2}, {3} books)".format(self.language,
                                                        self.iso639,
                                                        self.encoding,
                                                        len(self))