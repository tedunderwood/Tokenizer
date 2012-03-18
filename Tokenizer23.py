## TOKENIZING First Pass: Identifies common words and words not yet in the lexicon.

import codecs
import os
import difflib
from operator import itemgetter

OutPath = "/Users/tunderwood/Rules/HyphenRules/"

InPath = "/Users/tunderwood/Rules/FileSources/"

RulePath = "/Users/tunderwood/Rules/Active/"

OutputPath = "/Users/tunderwood/Rules/Tokenized/"

print('Begin')

TabChar = '\t'
SpaceChar = " "

Punctuation = {".", "?", "!", ":", ";", '"', "'", ",", "—", "$", "£",
'″', "′", '”', "´", '*', '(', ')', '¢', '_', '[', ']'}

StopWords = {"the", "of", "a", "and", "to", "in", "a", "that", "is",
"it", "was", "as", "his", "by", "he", "with", "for", "be", "which",
"i", "not", "on", "this", "at", "from", "or", "but", "have", "are",
"they", "had", "all", "were", "an", "we" "one", "been"}

Genres = {'non', 'mis', 'let', 'poe', 'dra', 'ora', 'fic', 'bio'}

def chunks(l, MinSize):
    TotalLen = len(l)
    NumChunks = int(TotalLen / MinSize)
    if NumChunks < 2:
        return [l]      
    Remainder = TotalLen % MinSize
    ChunkLen = MinSize + int(Remainder / NumChunks) + 1
    return [l[i:i+ ChunkLen] for i in range(0, TotalLen, ChunkLen)]

def strip_punctuation(Token):
    """Strip punctuation marks from the beginning and end of a word"""

    TokLis = list(Token)   
    WordBegun = False

    for Index, Char in enumerate(TokLis):
        if Char.isalnum():
            Token = Token[Index:]
            WordBegun = True
            break

    if not WordBegun:
        return ""
    TokLis = list(Token)
    
    # Now in reverse.
    LastPos = len(TokLis) - 1
    WordBegun = False
    
    for Index in range(LastPos, 0, -1):
        if TokLis[Index].isalnum():
            Token = Token[:Index + 1]
            WordBegun = True
            break

    if not WordBegun:
        return ""
    else:
        return Token

## Open the MainDictionary, read it into Lexicon. In this program Lexicon
## is a universal mapper covering dictionary words (which map to themselves)
## as well as variant-spellings and syncopates (which map to corrections).
    

print('Loading dictionary.')

FileString = RulePath + "TokenizeDictionary.txt"
F = codecs.open(FileString, 'r', 'utf-8')
FileLines = F.readlines()
F.close()

Lexicon = {}

for Line in FileLines:
    Line = Line.rstrip()
    LineParts = Line.split(TabChar)
    Word = LineParts[0].rstrip()
    Word = Word.lower()
    Lexicon[Word] = Word

HyphRules = {}

FileString = RulePath + 'HyphenRules.txt'
F = codecs.open(FileString, 'r', 'utf-8')
FileLines = F.readlines()
F.close()

FileLines.reverse()
# Doing this so that unhyphenated forms get read before hyphenated ones.

for Line in FileLines:
    Line = Line.rstrip()
    LineParts = Line.split(TabChar)
    Word = LineParts[0].rstrip()
    Corr = LineParts[1].rstrip()
    HyphRules[Word] = Corr
    if " " not in Corr:
        Lexicon[Corr] = Corr
    else:
        StripWord = Word.replace("-", "")
        HyphRules[StripWord] = Corr
    if "-" in Word:
        StripWord = Word.replace("-", "")
        StripCorr = Corr.replace(" ", "")
        StripCorr = StripCorr.replace("-", "")
        if StripWord != StripCorr and StripWord not in HyphRules:
            HyphRules[StripWord] = Corr
            print(Word, 'produced two corrections.')

Fuse = {}
FuseStarters = set()

FileString = RulePath + 'FusingRules.txt'
F = codecs.open(FileString, 'r', 'utf-8')
FileLines = F.readlines()
F.close()

for Line in FileLines:
    Line = Line.rstrip()
    LineParts = Line.split(TabChar)
    Word = LineParts[0].rstrip()
    Word = tuple(Word.split(SpaceChar))
    FuseStarters.add(Word[0])
    Corr = LineParts[1].rstrip()
    Fuse[Word] = Corr

## Variant spellings get thrown into Lexicon.

FileString = RulePath + "VariantSpellings.txt"
F = codecs.open(FileString, 'r', 'utf-8')
FileLines = F.readlines()
F.close()

for Line in FileLines:
    Line = Line.rstrip()
    LineParts = Line.split(TabChar)
    Word = LineParts[0].rstrip()
    Corr = LineParts[1].rstrip()
    Lexicon[Word] = Corr
    if Corr not in Lexicon:
        Lexicon[Corr] = Corr

## SyncRules get thrown into the Lexicon unless they produce hyphenates.

SyncRules = {}

FileString = RulePath + "SyncopeRules.txt"
F = codecs.open(FileString, 'r', 'utf-8')
FileLines = F.readlines()
F.close()

for Line in FileLines:
    Line = Line.rstrip()
    LineParts = Line.split(TabChar)
    Word = LineParts[0].rstrip()
    Corr = LineParts[1].rstrip()
    if "-" in Corr:
        SyncRules[Word] = Corr
    else:
        Lexicon[Word] = Corr

DirList = os.listdir(InPath)

Count = 0

DocLen = len(DirList)

Metadata = {}
Titles = {}

User = input('Collection type? (ecc/ncf/eaf/19b/ver) ')
CollType = User

if User == "ecc":
    FileString = RulePath + "ECCOmeta.txt"
    F = codecs.open(FileString, 'r', 'utf-8')
    FileLines = F.readlines()
    F.close()

    for Line in FileLines:
        Line = Line.rstrip()
        LineParts = Line.split(TabChar)
        ID = LineParts[0]
        Date = LineParts[1]
        File = LineParts[2] + ".txt"
        Author = LineParts[3]
        Genre = LineParts[6]
        Title = LineParts[7]
        Metadata[File] = (ID, File, Author, Date, Genre, 'ecc')
        Titles[File] = Title
        
elif User == "19b":
    FileString = RulePath + "Metadata.txt"
    F = codecs.open(FileString, 'r', 'utf-8')
    FileLines = F.readlines()
    F.close()

    for Line in FileLines:
        Line = Line.rstrip()
        LineParts = Line.split(TabChar)
        ID = LineParts[0][:-4]
        Date = LineParts[4]
        File = LineParts[0]
        Author = LineParts[1]
        Genre = LineParts[8]
        Title = LineParts[13]
        if Genre not in Genres:
            print(ID, Title, 'Genre: ', Genre)
            Genre = input('Correction? ')
        Metadata[File] = (ID, File, Author, Date, Genre, '19b')
        Titles[File] = Title

elif User == "ver":
    FileString = RulePath + "VerseMetadata.txt"
    F = codecs.open(FileString, 'r', 'utf-8')
    FileLines = F.readlines()
    F.close()

    for Line in FileLines:
        Line = Line.rstrip()
        LineParts = Line.split(TabChar)
        ID = LineParts[0] + "v"
        Date = LineParts[3]
        File = LineParts[1]
        File = File[:-4] + "v.txt"
        Author = LineParts[2]
        Author = Author.strip('"')
        Title = LineParts[8]
        Collection = LineParts[5]
        Metadata[File] = (ID, File, Author, Date, "poe", "ver")
        Titles[File] = Title


for FileName in DirList:
    if FileName[0] == '.' or FileName[-1] != 't':
        continue
    if FileName not in Metadata:
        print(FileName, 'not in metadata file.')

for FileName, Title in Titles.items():
    if FileName not in DirList:
        print(FileName, 'in metadata but not source directory.')
        print(Title)
        print('\n')

## The following section limits the Lexicon to roughly the top 27,000 words.

FileString = "/Users/tunderwood/Rules/Output/Included.txt"
F = codecs.open(FileString, 'r', 'utf-8')
FileLines = F.readlines()
F.close()

Common = {}

for Line in FileLines:
    Line = Line.rstrip()
    LineParts = Line.split(TabChar)
    Word = LineParts[0]
    Freq = int(LineParts[1])
    if Freq > 99:
        Common[Word] = Freq

del FileLines
   
Segment = int(input('Starting segment number? '))

Tenth = int(DocLen/10)
Tenths = frozenset(range(Tenth, DocLen+Tenth, Tenth))
TenthCount = 10
Chunk = "0"

if CollType == 'ecc':
    User = input('How many chunks to produce? ')
    Divisor = 100 / int(User)

for FileName in DirList:

    if FileName[0] == '.' or FileName[-1] != 't':
        print('Skipping hidden file', FileName)
        continue

    Count += 1

    if Count in Tenths:
        print(TenthCount,'%', sep='')
        if CollType == 'ecc' and TenthCount < 100:
            Chunk = str(int(TenthCount / Divisor))
        TenthCount += 10

    ThisTitle = Titles[FileName].lower()
    ThisTitle = ThisTitle.split()
    ThisTitle = [strip_punctuation(x) for x in ThisTitle]
    TitleWords = set(ThisTitle)
    KeyTitleWords = TitleWords - StopWords
    HeadList = []
    HeadCount = {}
    
    FileString = InPath + FileName
    F = codecs.open(FileString, 'r', 'utf-8')
    Document = F.readlines()
    F.close()

    DVector = []

    LineCount = 0

    for Line in Document:
        Line = Line.rstrip()
        if Line == '' or Line.isdigit():
            continue

    ## Split each line into words after replacing certain problematic substrings.
        Line = Line.replace('äî', ' ')
        Line = Line.replace('Äî', ' ')
        Line = Line.replace('ñ™', ' ')
        Line = Line.replace(chr(8218), ' ')
        Line = Line.replace(chr(8212), ' ')
        Line = Line.replace("--", " ")
        Line = Line.replace("_", " ")
        Line = Line.replace('▪', ' ')
        Line = Line.replace(';', ' ')
        Line = Line.replace('"', ' ')
        Line = Line.replace('[', ' ')
        Line = Line.replace(']', ' ')
        Line = Line.replace('&', ' ')
        Line = Line.replace(':', ' ')
        Line = Line.replace('|', '')
        Line = Line.replace(chr(8739), '')
        Line = Line.replace('{', '')
        Line = Line.replace('}', '')
        Line = Line.replace('′', "'")
        Line = Line.replace('´', "'")
        WordList = Line.split()
        LineCount += 1

        WordSet = set([x.lower() for x in WordList])
        if len(WordSet.intersection(KeyTitleWords)) > 0 and LineCount > 30:
            StrippedList = []
            for Word in WordList:
                Candidate = strip_punctuation(Word.lower())
                if not Candidate.isdigit():
                    StrippedList.append(Candidate)
            WordSet = set(StrippedList) - StopWords
            UnionLength = len(WordSet.intersection(KeyTitleWords))
            SetLength = len(WordSet)
            if UnionLength > (SetLength * .75) and SetLength > 1:
                Position = 0
                SequenceCount = 0
                TotalNonstopCount = 0
                for Word in StrippedList:
                    if Word not in StopWords:
                        TotalNonstopCount += 1
                        if Word in ThisTitle[Position:]:
                            NewPos = ThisTitle.index(Word)
                            if NewPos >= Position:
                                SequenceCount += 1
                            Position = NewPos
                Ratio = SequenceCount / (TotalNonstopCount + .001)
                if Ratio > 0.7:                   
                    Match = False
                    LowerLine = SpaceChar.join(StrippedList)
                    for RunningHead in HeadList:
                        EditDistance = difflib.SequenceMatcher(None, LowerLine, RunningHead).ratio()
                        if EditDistance > 0.75:
                            Match = True
                            HeadCount[RunningHead] += 1
                    if not Match:
                        HeadList.append(LowerLine)
                        HeadCount[LowerLine] = 1
                    continue
                
            Match = False
            LowerLine = SpaceChar.join(StrippedList)
            for RunningHead in HeadList:
                EditDistance = difflib.SequenceMatcher(None, LowerLine, RunningHead).ratio()
                if EditDistance > 0.7:
                    Match = True
                    HeadCount[RunningHead] += 1
            if Match:
                continue

        # Extend the doc vector by adding these words.

        DVector.extend(WordList)

    ListOfLists = chunks(DVector, 50000)
    DocTokens = len(DVector)
    NumSegments = len(ListOfLists)
    TotalRecognized = 0

    for Seg in ListOfLists:

        SegmentTokens = len(Seg)

        Included = {}
        ## Initialize Included count.
        for Word, Corr in Lexicon.items():
            Included[Corr] = 0
        
        SkipWords = 0
        CleanVector = []
        
        for Index, Word in enumerate(Seg):

            if SkipWords > 0:
                SkipWords = SkipWords - 1
                continue

            Word = Word.lower()

            # Here is where we pick up multi-word phrases. We strip punctuation only from
            # the *final* word in the phrase, thus avoid fusing across punctuation.

            if Word in FuseStarters and Index + 3 < SegmentTokens: 

                TwoWord = (Word, strip_punctuation(Seg[Index + 1].lower()))
                if TwoWord in Fuse:
                    Corr = Fuse[TwoWord]
                    if Corr in Lexicon:
                        Corr = Lexicon[Corr]
                        Included[Corr] +=1
                        SkipWords = 1
                        continue
                    else:
                        print(Corr, 'in fuse dictionary but not lexicon.')
                        Included[Corr] = 1
                        SkipWords = 1
                        continue
                    
                ThreeWord = (Word, Seg[Index + 1].lower(), strip_punctuation(Seg[Index+2].lower()))
                if ThreeWord in Fuse:
                    Corr = Fuse[ThreeWord]
                    if Corr in Lexicon:
                        Corr = Lexicon[Corr]
                        Included[Corr] +=1
                        SkipWords = 2
                        continue
                    else:
                        print(Corr, 'in fuse dictionary byt not lexicon.')
                        Included[Corr] = 1
                        SkipWords = 2
                        continue
            
            Word = strip_punctuation(Word)

            if len(Word) > 2 and Word[-2:] == "'s":
                Word = Word[:-2]

            if len(Word) > 0 and not Word[0].isdigit():
                CleanVector.append(Word)

        for Index, Word in enumerate(CleanVector):

            ## SyncRules is a transformation that does not produce "continue"
            ## because it produces hyphenated phrases that need further processing.

            if Word in SyncRules:
                Word = SyncRules[Word]
                   
            if Word in Lexicon:
                Corr = Lexicon[Word]
                if Corr in Included:
                    Included[Corr] += 1
                    continue
                else:
                    print(Corr, 'in variant list but not lexicon.')
                    continue

            if Word in HyphRules:
                Corr = HyphRules[Word]
                if " " in Corr:
                    CorrList = Corr.split(SpaceChar)
                    for Elem in CorrList:
                        if Elem in Lexicon:
                            Corr = Lexicon[Elem]
                            Included[Corr] += 1
                        else:
                            print(Elem, 'in hyphen list but not lexicon.')
                    continue
                else:
                    if Corr in Lexicon:
                        Corr = Lexicon[Corr]
                        Included[Corr] += 1
                        continue
                    else:
                        print(Corr, 'in hyphen list but not lexicon.')
                        continue

            Word = Word.replace(",", "-")
            # The point of that is to split words fused across a comma.

            if "-" in Word:
                FuseWord = Word.replace("-", "")
                if FuseWord in Lexicon:
                    Corr = Lexicon[FuseWord]
                    Included[Corr] += 1
                    continue
                SplitWord = Word.split("-")
                for Elem in SplitWord:
                    if Elem in Lexicon:
                        Corr = Lexicon[Elem]
                        Included[Corr] += 1
                continue

            # Here ends the second word-matching loop.

        WriteList = sorted(Included.items(), key = itemgetter(1), reverse = True)
        SegRecognized = 0
        FileMetadata = Metadata[FileName]
        TailString = '\t' + FileMetadata[3] + '\t' + FileMetadata[4] + '\t' + FileMetadata[5] + '\n'
        HeadString = str(Segment) + '\t' + FileMetadata[0] + '\t'

        FileString = OutputPath + 'Data' + Chunk + '.txt'
        F = codecs.open(FileString, 'a', 'utf-8')
        for Entry in WriteList:
            if Entry[0] not in Common or Entry[1] < 1:
                continue
            # That section keeps us from writing uncommon words.
            SegRecognized = SegRecognized + Entry[1]
            Line = HeadString + Entry[0] + '\t' + str(Entry[1]) + TailString
            F.write(Line)
        F.close()

        MetaString = str(Segment) + TabChar + TabChar.join(FileMetadata)
        MetaString = MetaString + TabChar +  str(SegmentTokens) + TabChar + str(SegRecognized)
        MetaString = MetaString + TabChar + Titles[FileName] + '\n'
        FileString = OutputPath + 'SegmentMetadata.txt'
        F = codecs.open(FileString, 'a', 'utf-8')
        F.write(MetaString)
        F.close()

        Segment +=1

        TotalRecognized = TotalRecognized + SegRecognized
        # End segment-level loop.
        
    # Here's where the document-level metadata gets written.
    FileMetadata = Metadata[FileName]
    MetaString = TabChar.join(FileMetadata)
    MetaString = MetaString + TabChar +  str(DocTokens) + TabChar + str(TotalRecognized)
    MetaString = MetaString + TabChar + Titles[FileName] + '\n'
    FileString = OutputPath + "DocMetadata.txt"
    F = codecs.open(FileString, 'a', 'utf-8')
    F.write(MetaString)
    F.close()
    FileString = OutputPath + "RunningHeads.txt"
    F = codecs.open(FileString, 'a', 'utf-8')
    for Head in HeadList:
        F.write(Head + " --- " + str(HeadCount[Head]) + '\n')
    F.close()
    # End document-level loop
    

print('Done.')
