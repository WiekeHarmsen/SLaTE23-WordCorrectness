# coding=utf-8
import itertools
import numpy as np
import pandas as pd
from nltk.tokenize import wordpunct_tokenize  # version 3.6.2
import helper_scripts.constants as constants


def init_charset():
    return {
        "zero_char": constants.zero_char,       # 'zero' character for insertions/deletions.
        "wbnd_char": ' ',       # 'word boundary' character in transcriptions.
        "consonants": ["p", "b", "t", "d", "k", "g", "f", "v", "s", "ś", "z", "m", "n", "ñ", "l", "r", "q", "h", "c", "ç", "x", "w",
                       "P", "B", "T", "D", "K", "G", "F", "V", "S",      "Z", "M", "N",      "L", "R", "Q", "H", "C",      "X", "W"],
        "vowels": ["i", "I", "ï", "î", "í", "ì", "Ï", "Î", "Í", "Ì",
                   "e", "E", "ë", "ê", "é", "è", "Ë", "Ê", "É", "È", 
                   "a", "A", "ä", "â", "á", "à", "Ä", "Â", "Á", "À",
                   "o", "O", "ö", "ô", "ó", "ò", "Ö", "Ô", "Ó", "Ò", 
                   "u", "U", "ü", "û", "ú", "ù", "Ü", "Û", "Ú", "Ù", "µ",],
        "consonant_and_vowel": ["j", "J", "y", "Y"],
        "punctuation": constants.punctuation,
        "numbers": constants.numbers
    }

def align_init(charset):
    vowels = charset["vowels"]
    consonants = charset["consonants"]
    consonant_and_vowel = charset["consonant_and_vowel"]
    punctuation = charset["punctuation"]
    numbers = charset["numbers"]
    zero_char = charset["zero_char"]
    wbnd_char = charset["wbnd_char"]

    names = vowels + consonants + consonant_and_vowel + punctuation + numbers + [zero_char, wbnd_char]
    matrix = np.zeros((len(names), len(names)))

    diff = pd.DataFrame(matrix, columns=names, index=names)
    # ----------------------------------------------------------------------
    # set low difference between each pair of the same category
    # ----------------------------------------------------------------------
    for i in range(len(vowels)-1):
        ci = vowels[i]
        for j in range(i+1, len(vowels)):
            cj = vowels[j]
            diff.loc[ci, cj] = 2
            diff.loc[cj, ci] = 2

    for i in range(len(consonants)):
        ci = consonants[i]
        for j in range(i+1, len(consonants)):
            cj = consonants[j]
            diff.loc[ci, cj] = 2
            diff.loc[cj, ci] = 2

    for i in range(len(punctuation)):
        ci = punctuation[i]
        for j in range(i+1, len(punctuation)):
            cj = punctuation[j]
            diff.loc[ci, cj] = 2
            diff.loc[cj, ci] = 2

    for i in range(len(numbers)):
        ci = numbers[i]
        for j in range(i+1, len(numbers)):
            cj = numbers[j]
            diff.loc[ci, cj] = 2
            diff.loc[cj, ci] = 2

    # ----------------------------------------------------------------------
    # set high differences between categories
    # ----------------------------------------------------------------------
    for i in range(len(vowels)):
        ci = vowels[i]
        for j in range(len(consonants)):
            cj = consonants[j]
            diff.loc[ci, cj] = 99
            diff.loc[cj, ci] = 99

    for i in range(len(vowels)):
        ci = vowels[i]
        for j in range(len(punctuation)):
            cj = punctuation[j]
            diff.loc[ci, cj] = 99
            diff.loc[cj, ci] = 99

    for i in range(len(consonants)):
        ci = consonants[i]
        for j in range(len(punctuation)):
            cj = punctuation[j]
            diff.loc[ci, cj] = 99
            diff.loc[cj, ci] = 99

    for i in range(len(vowels)):
        ci = vowels[i]
        for j in range(len(numbers)):
            cj = numbers[j]
            diff.loc[ci, cj] = 99
            diff.loc[cj, ci] = 99

    for i in range(len(consonants)):
        ci = consonants[i]
        for j in range(len(numbers)):
            cj = numbers[j]
            diff.loc[ci, cj] = 99
            diff.loc[cj, ci] = 99

    for i in range(len(punctuation)):
        ci = punctuation[i]
        for j in range(len(numbers)):
            cj = numbers[j]
            diff.loc[ci, cj] = 99
            diff.loc[cj, ci] = 99

    diff.loc[wbnd_char, wbnd_char] = 0
    for ci in vowels:
        diff.loc[ci, wbnd_char] = 99
        diff.loc[wbnd_char, ci] = 99

    for ci in consonants:
        diff.loc[ci, wbnd_char] = 99
        diff.loc[wbnd_char, ci] = 99

    for ci in punctuation:
        diff.loc[ci, wbnd_char] = 99
        diff.loc[wbnd_char, ci] = 99

    for ci in numbers:
        diff.loc[ci, wbnd_char] = 99
        diff.loc[wbnd_char, ci] = 99

    # ----------------------------------------------------------------------
    # set low differences between consonant_and_vowel and consonant/vowel category
    # ----------------------------------------------------------------------

    for i in range(len(consonant_and_vowel)):
        ci = consonant_and_vowel[i]
        for j in range(len(consonants)):
            cj = consonants[j]
            diff.loc[ci, cj] = 2
            diff.loc[cj, ci] = 2

    for i in range(len(consonant_and_vowel)):
        ci = consonant_and_vowel[i]
        for j in range(len(vowels)):
            cj = vowels[j]
            diff.loc[ci, cj] = 2
            diff.loc[cj, ci] = 2

    return diff


#INITIALISATION
charset = init_charset()
diff = align_init(charset)


def preprocess(line):
    #Reverse line
    line = line[::-1]
    line = line.replace("&", "en")
    line = line.replace(constants.zero_char, constants.place_holder_char) # to prevent confusion, the zero character is replaced with a different character before the word is aligned

    # Use tokenizer to represent punctuation marks as separate characters.
    line_tokenized = list(itertools.chain(*list(itertools.chain(*[[wordpunct_tokenize(w), ' '] for w in line.split()]))))
    # https://stackoverflow.com/questions/23358444/how-can-i-use-word-tokenize-in-nltk-and-keep-the-spaces

    return ''.join(line_tokenized).strip()


def check_diff_dataframe(line):
    global diff

    for char in line:
        if char not in diff.columns:
            extra_column_diff = diff.reindex(columns = [char], fill_value = 99)
            extra_column_diff.drop(extra_column_diff.tail(0).index,inplace=True)
            diff[char] = extra_column_diff

            extra_row_diff = diff.reindex([char], fill_value = 99)
            diff = pd.concat([diff, extra_row_diff])

          
def align_dist(target_line, original_line):
    target_line = preprocess(target_line)
    original_line = preprocess(original_line)

    check_diff_dataframe(target_line)
    check_diff_dataframe(original_line)

    alnorm, alreal = align(target_line, original_line,)
    dist_score, nsub, ndel, nins = distance(alnorm, alreal)

    #pro processing step
    alnorm = alnorm[::-1]
    alreal = alreal[::-1]
    return dist_score, nsub, ndel, nins, alnorm, alreal


def print_input(target_line, original_line):
    return target_line, original_line


def align(norm_input, real_input):
    fon_ins_cost = 1  # corrected to 3 by 'distance' routine
    fon_del_cost = 1  # corrected to 3 by 'distance' routine
    lnorm = len(norm_input)
    lreal = len(real_input)
    i = 0
    j = 0
    real_i = ''
    norm_j = ''
    dist = []
    op = 0
    real = []
    norm = []
    dist = 0
    
    aln = ''
    alr = ''
    zero_char = charset["zero_char"]

    # ----------------------------------------------------------------------
    # Initialise edges of search space.
    # ----------------------------------------------------------------------
    dist = np.zeros((lnorm+1, lreal+1))
    dist = pd.DataFrame(dist)
    real = np.array([[''] * (lreal+1)] * (lnorm+1))
    real = pd.DataFrame(real)
    norm = np.array([[''] * (lreal+1)] * (lnorm+1))
    norm = pd.DataFrame(norm)

    for i in range(1, lreal+1):
        dist[i][0] = i*fon_del_cost
        real[i][0] = real[i-1][0] + real_input[i-1:i]
        norm[i][0] = norm[i-1][0] + zero_char

    for j in range(1, lnorm+1):
        dist[0][j] = j*fon_ins_cost
        real[0][j] = real[0][j-1] + zero_char
        norm[0][j] = norm[0][j-1] + norm_input[j-1:j]

    # ----------------------------------------------------------------------
    # Construct search space and alignment.
    # ----------------------------------------------------------------------
    for i in range(1, lreal+1):
        for j in range(1, lnorm+1):

            real_i = real_input[i-1:i]
            norm_j = norm_input[j-1:j]

            # try:
            dist[i][j], op = min_func([
                (dist[i-1][j] + fon_del_cost),    # deletion
                # substitution
                (dist[i-1][j-1] + float(diff[real_i][norm_j])*0.5),
                (dist[i][j-1] + fon_ins_cost)])  # insertion
           
            if(op == 0):  # deletion
                real[i][j] = real[i-1][j] + real_i
                norm[i][j] = norm[i-1][j] + zero_char
            elif(op == 1):  # substitution
                real[i][j] = real[i-1][j-1] + real_i
                norm[i][j] = norm[i-1][j-1] + norm_j
            else:  # insertion
                real[i][j] = real[i][j-1] + zero_char
                norm[i][j] = norm[i][j-1] + norm_j

    aln = norm[lreal][lnorm]
    alr = real[lreal][lnorm]

    aln, alr = verify_alignment(aln, alr)
    return aln, alr


def distance(alnorm, alreal):
    fon_ins_cost = 1  # corrected to 3 by 'distance' routine
    fon_del_cost = 1  # corrected to 3 by 'distance' routine

    zero_char = charset["zero_char"]
    
    dist_score = 0
    n_ins = 0
    n_del = 0
    n_sub = 0

    for i in range(len(alnorm)):
        if alnorm[i] == zero_char:
            n_ins += 1
            dist_score += fon_ins_cost
        elif(alreal[i] == zero_char):
            n_del += 1
            dist_score += fon_del_cost
        elif(alnorm[i] != alreal[i]):
            n_sub += 1
            dist_score += diff[alnorm[i]][alreal[i]]

    return dist_score, n_sub, n_del, n_ins

    

# ----------------------------------------------------------------------
# Returns the minimum value of its arguments, and the index of the
# minimum value in the argument array.
# ----------------------------------------------------------------------
def min_func(input_list):
    min_i = 999.0
    pos_i = 0

    for i in range(len(input_list)):
        value1 = float(input_list[i])
        value2 = min_i

        if (value1 < value2):
            min_i = value1
            pos_i = i

    return min_i, pos_i


# ----------------------------------------------------------------------
# Returns the input string s as a list of characters.
# ----------------------------------------------------------------------
def getCharList(s):
    return [char for char in s]


# ----------------------------------------------------------------------
# Verify placement of deletions/insertions in pre-aligned norm and
# realisation transcriptions. This fixes a bug causing misalignments,
# and considers the number of phoneme feature differences in case of
# equal phoneme distances.
# ----------------------------------------------------------------------

def verify_alignment(alnorm, alreal):

    zero_char = charset["zero_char"]

    alnorm_out = getCharList(alnorm)
    alreal_out = getCharList(alreal)
    changes = 0
    i = 0
    p = 0

    # ----------------------------------------------------------------------
    # Exit early if norm and real are equal, or if norm/real do not
    # contain zero characters (nothing to realign).
    # ----------------------------------------------------------------------
    if (alnorm == alreal):
        return (alnorm, alreal)

    # ----------------------------------------------------------------------
    # Verify insertions, skip if no insertions are found.
    # ----------------------------------------------------------------------
    if (alnorm.find(zero_char) != -1):
        for i in range(len(alnorm)-1, 0, -1): # Hier komen (kwamen) dubbele letters erbij
            if (alnorm_out[i] == zero_char):
                p = i
                # find first index where there is no zero_char in norm, save index in var p
                while (alnorm_out[p] == zero_char and p > 0): #alnorm_out was alnorm
                    p = p-1
                if(diff[alnorm_out[p]][alreal_out[p]] == diff[alnorm_out[p]][alreal_out[i]]):
                    aln_out_i = alnorm_out[i]
                    aln_out_p = alnorm_out[p]
                    alnorm_out[p] = aln_out_i
                    alnorm_out[i] = aln_out_p
                    changes += 1

        for i in range(len(alnorm)):
            if (alnorm_out[i] == zero_char):
                p = i
                while (p < len(alnorm)-1 and alnorm_out[p] == zero_char):
                    p += 1
                if (diff[alnorm_out[p]][alreal_out[p]] == diff[alnorm_out[p]][alreal_out[i]]):
                    aln_out_i = alnorm_out[i]
                    aln_out_p = alnorm_out[p]
                    alnorm_out[p] = aln_out_i
                    alnorm_out[i] = aln_out_p
                    changes += 1

    # ----------------------------------------------------------------------
    # Verify deletions, skip if no deletions are found.
    # ----------------------------------------------------------------------
    if(alreal.find(zero_char) != -1):
        for i in range(len(alreal)-1, 0, -1):
            if (alreal_out[i] == zero_char):
                p = i
                # find first index where there is no zero_char in norm, save index in var p
                while (alreal_out[p] == zero_char and p > 0):
                    p = p-1
                if (diff[alnorm_out[p]][alreal_out[p]] == diff[alnorm_out[i]][alreal_out[p]]):
                    aln_real_i = alreal_out[i]
                    aln_real_p = alreal_out[p]
                    alreal_out[p] = aln_real_i
                    alreal_out[i] = aln_real_p
                    changes += 1

        for i in range(len(alreal)):
            if (alreal[i] == zero_char):
                p = i
                while (p < len(alnorm)-1 and alreal_out[p] == zero_char):
                    p += 1
                if (diff[alnorm_out[p]][alreal_out[p]] == diff[alnorm_out[i]][alreal_out[p]]):
                    aln_real_i = alreal_out[i]
                    aln_real_p = alreal_out[p]
                    alreal_out[p] = aln_real_i
                    alreal_out[i] = aln_real_p
                    changes += 1

    # Convert alnorm_out and alreal_out to strings
    alnorm_out = "".join(alnorm_out)
    alreal_out = "".join(alreal_out)

    return alnorm_out, alreal_out


def main():

    target = "hoi4"
    original = "€hallo7"
    dist_score, nsub, ndel, nins, alnorm, alreal = align_dist(
        target, original)
    print(dist_score, nsub, ndel, nins, alnorm, alreal)

if __name__ == '__main__':
    main()
