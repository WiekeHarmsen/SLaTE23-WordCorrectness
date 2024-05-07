import helper_scripts.constants as constant
import helper_scripts.annotator as annotator 
import unidecode


def check_for_context_rules(correct, orth_cat, target_phons, target_pcus, original_pcus, pcu_idx, pos_label, pos_details, morphemes):
    error_cat = "-"
    taret_pcu = target_pcus[pcu_idx]
    original_pcu = original_pcus[pcu_idx]
    target_phon = target_phons[pcu_idx]
    
    """
    Special Cases: Regularities in pronunciation of specific structures
    """    
    #Rule 1: The "w" before an "r" is pronounced as a /v/ (e.g. wreed)
    if taret_pcu == "w" and pcu_idx != 0 and target_phons[pcu_idx-1] == "v" and pcu_idx != len(target_pcus)-1 and target_pcus[pcu_idx+1] == "r":
        orth_cat = "CoSc1"
        if not correct and original_pcu == "v":
            error_cat = "CoSc1"
    
    #Rule 2: An /w/ or /j/ pronounced between two vowels is not written (e.g. februari)
    elif taret_pcu == "-" and target_phon in ["w", "j"] and 0 < pcu_idx < len(target_pcus)-1 and target_pcus[pcu_idx-1] in constant.all_vowels and target_pcus[pcu_idx+1] in constant.all_vowels:
        orth_cat = "CoSc2"
        if not correct and original_pcu in ["w", "j"]:
            error_cat = "CoSc2"
    
    #Rule 3: When a "w" is pronounced after an /ee/ or /ie/ sound, an "u" should be written before the "w" (e.g. nieuw, sneeuw)
    elif taret_pcu in ["eeu", "ieu"] and pcu_idx != len(target_pcus)-1 and target_pcus[pcu_idx+1] == "w":
        orth_cat = "CoSc3"
        if not correct and original_pcu in ["ee", "ie"]:
            error_cat = "CoSc3"
    
    """
    Consonant Doubling
    """    
    #Rule 1: A consonant is doubled if it's written after a short vowel (excluding sjwa) and if it's not at the end of the word
    if taret_pcu in constant.double_cons and pcu_idx > 0 and target_phons[pcu_idx-1] in constant.short_vowels_phon and pcu_idx != len(target_pcus)-1: 
        orth_cat = "CoCd1"
        if not correct and original_pcu == taret_pcu[0]:
            error_cat = "CoCd1"

    #Rule 2: A consonant is not doubled if it's written after a long vowel and if it's not at the end of the word.      
    if taret_pcu in constant.single_cons and pcu_idx > 0 and target_phons[pcu_idx-1] in constant.long_vowels_phon and pcu_idx != len(target_pcus)-1:
        orth_cat = "Un"
        if not correct and taret_pcu == original_pcu[0] and original_pcu in constant.double_cons:
            error_cat = "UnSub1a"
            
#     #Rule 3: A consonant is not doubled if it's written after a sjwa.      
#     if taret_pcu in single_cons and pcu_idx > 0 and target_phons[pcu_idx-1] == "@" and pcu_idx != len(target_pcus)-1:
#         orth_cat = "CoCd3"
#         if not correct and taret_pcu == original_pcu[0] and original_pcu in double_cons:
#             error_cat = "CoCd3"
        
    """
    Vowel Singulation
    """
    #Rule 1: A long vowel is written with one letter symbol if it is at the end of a syllable  
    if taret_pcu in constant.short_vowels and target_phon in constant.long_vowels_phon:
        orth_cat = "CoVs1"
        if not correct and original_pcu in constant.long_vowels and original_pcu[0] == taret_pcu:
            error_cat = "CoVs1"
        
    #Rule 2 Exception 1 : A long vowel is written with two letter symbols if it is followed by "ch" (e.g. goochelen)    
    if taret_pcu in constant.long_vowels and target_phon in constant.long_vowels_phon and pcu_idx != len(target_pcus)-1 and target_pcus[pcu_idx+1] == "ch":
        orth_cat = "CoVs2a"
        if not correct and original_pcu in constant.short_vowels and taret_pcu[0] == original_pcu:
            error_cat = "CoVs2a"
            
    #Rule 2 Exception 2 : A long ee is written with two symbols at the end of a word to avoid confusion with the sjwa (e.g. "zee")
    elif taret_pcu == "ee" and target_phon == "e" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "CoVs2b"
        if not correct and original_pcu == "e":
            error_cat = "CoVs2b"
            
    #Rule 2 Exception 3 : A long ie is written with two symbols at the end of a word (e.g. "drie")
    elif taret_pcu == "ie" and target_phon == "i" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "CoVs2c"
        if not correct and original_pcu == "i":
            error_cat = "CoVs2c"
            
    #Rule 2 Exception 4 : A long vowel is written with two symbols before a diminutive suffix (e.g. "laatje")
    elif taret_pcu in constant.long_vowels and target_phon in constant.long_vowels_phon and "dim" in pos_details and "".join(target_pcus[pcu_idx+1:]).replace(constant.zero_char, "") in ["pje", "tje", "je"]:
        orth_cat = "CoVs2d"
        if not correct and original_pcu in constant.short_vowels and taret_pcu[0] == original_pcu:
            error_cat = "CoVs2d"
    
    #Rule 2: A long vowel is written with two letter symbols if it is not at the end of a syllable    
#     elif taret_pcu in con.long_vowels and target_phon in con.long_vowels_phon:
#         orth_cat = "CoVs2a"
#         if not correct and original_pcu incon. short_vowels and taret_pcu[0] == original_pcu:
#             error_cat = "CoVs2a"
    
    #Rule 3:  A short vowel is always written with one letter symbol 
#     if taret_pcu in con.short_vowels and target_phon in con.short_vowels_phon:
#         orth_cat = "CoVs3"
#         if not correct and original_pcu in con.long_vowels and original_pcu[0] == taret_pcu:
#             error_cat = "CoVs3"    
        
    """
    Accented Vowels and Consonants
    """
    #Rule 1: Some vowels need an accent to simplify pronunciation.
    if unidecode.unidecode(taret_pcu) != taret_pcu:
        orth_cat = "CoAc1"
        if not correct and unidecode.unidecode(taret_pcu) == original_pcu:
            error_cat = "CoAc1"
        
    #Rule 2: Most vowels don't need an accent to simplify pronunciation.
    if not correct and taret_pcu == unidecode.unidecode(original_pcu):
        orth_cat = "Un"
        error_cat = "CoAc2"
        
    
    """
    Apostrophe
    """
    #Rule 1: Apostrophe is written in proper names that end in an sis-sound and are used as genitive (e.g., Kees')
    if taret_pcu == "'" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1) and pos_label == "SPEC" and "deeleigen" in pos_details and morphemes[-1][-1] == "'":
        orth_cat = "CoAp1"
        if not correct:
            error_cat = "CoAp1a"
        
    #Rule 2: Apostrophe is written in plural and genitive forms, that people could read wrongly with a short vowel instead of long vowel (e.g., opa's)
    elif taret_pcu == "'" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2) and target_pcus[pcu_idx+1]=="s":
        orth_cat = "CoAp1"
        if not correct:
            error_cat = "CoAp1b"
            
    #salto'-s vs salto-os
    elif not correct and taret_pcu == "'" and 0 < pcu_idx < len(original_pcus)-1 and original_pcus[pcu_idx-1] + original_pcus[pcu_idx+1] in constant.long_vowels and target_pcus[pcu_idx+2]=="s":
        orth_cat = "CoAp1"
        error_cat = "CoAp1b"
    
    #Rule 3: Apostrophe is written in diminutives of words ending in a consonant +"y" (e.g., Baby'tje)
    elif taret_pcu == "'" and target_pcus[pcu_idx-1] == "y" and target_pcus[pcu_idx-2] in constant.adapt_consonants and "dim" in pos_details:
        orth_cat = "CoAp1"
        if not correct:
            error_cat = "CoAp1c"
    
    #Rule 4: Apostrophe is written in one symbol words or abbreviations before suffixes of plural and genitive forms (e.g., HBO'er, sms't)
    elif taret_pcu == "'" and morphemes[-1] in ["tje", "tjes", "t", "er", "te", "ten", "en"]:
        orth_cat = "CoAp1"
        if not correct:
            error_cat = "CoAp1d"
        
    #Rule 5: Apostrophe is written instead of other letters to shorten a word (e.g., zo'n, 's (morgens), m'n, z'n)
    elif taret_pcu == "'" and "'" in morphemes[-1]:
        orth_cat = "CoAp1"
        if not correct:
            error_cat = "CoAp1e"
    
    #Rule 6: Other apostrophes
    elif taret_pcu == "'":
        orth_cat = "CoAp1"
        if not correct:
            error_cat = "CoAp1f"
        
    return orth_cat, error_cat

def check_for_morphology_rules(correct, orth_cat, target_phons, target_pcus, original_pcus, pcu_idx, pos_label, morphemes, lemma):
    error_cat = "-"
    taret_pcu = target_pcus[pcu_idx]
    original_pcu = original_pcus[pcu_idx]
    target_phon = target_phons[pcu_idx]
    
    obstruent_pairs = [["b", "p"], ["v", "f"], ["z", "s"]]
    obstruent_pairs_flat = [item for sublist in obstruent_pairs for item in sublist]
    sonorant_pairs = [["r","l"], ["w", "j", "h"], ["m", "n"]]
    
    """
    Uniformity
    """      
    #Rule 2: Miniaturization (Geminaatdelging)
    if taret_pcu in constant.double_cons and pcu_idx != 0 and annotator.geminaatdelging(target_pcus[:pcu_idx], target_pcus[pcu_idx+1:], morphemes, taret_pcu[0]):
        orth_cat = "MoMi1"
        if not correct and original_pcu == taret_pcu[0]:
            error_cat = "MoMi1"
        
    #Rule 3: Assimilation of stem followed by miniaturization
    elif taret_pcu in obstruent_pairs_flat and not taret_pcu in morphemes and 0 < pcu_idx < len(target_pcus)-1 and annotator.same_phon_around_idx(target_pcus, pcu_idx, target_phons):
        orth_cat = "MoAsMi1"
        if not correct and original_pcu == constant.zero_char:
            error_cat = "MoAsMi1"
        
    #Rule 4: Final devoicing
    elif taret_pcu == "d"  and annotator.at_end_of_morpheme(pcu_idx, target_pcus, morphemes, lemma, "d"):
        orth_cat = "MoFd1"
        if not correct and original_pcu == "t":
            error_cat = "MoFd1a"
    elif taret_pcu == "b" and annotator.at_end_of_morpheme(pcu_idx, target_pcus, morphemes, lemma, "b"):
        orth_cat = "MoFd1"
        if not correct and original_pcu == "p":
            error_cat = "MoFd1b"
        
    #Rule 4: Final devoicing exception
    elif taret_pcu == "f" and annotator.at_end_of_morpheme(pcu_idx, target_pcus, morphemes, lemma, "f"):
        orth_cat = "MoFd2"
        if not correct and original_pcu == "v":
            error_cat = "MoFd2a"
    elif taret_pcu == "s" and annotator.at_end_of_morpheme(pcu_idx, target_pcus, morphemes, lemma, "s"):
        orth_cat = "MoFd2"
        if not correct and original_pcu == "z":
            error_cat = "MoFd2b"
        
    #Rule 5: t is written, but [t] is not pronounced. e.g. in "worstjes", "postkantoor"
    elif (taret_pcu == "t" or taret_pcu == "d") and target_phon == constant.zero_char:
        orth_cat = "MoEndT1"
        if not correct and original_pcu == constant.zero_char:
            error_cat = "MoEndT1"
        
    #Rule 6: n is written, but [n] is not pronounced. e.g. in "binnen", "fietsen"
    elif taret_pcu == "n" and target_phon == constant.zero_char and annotator.at_end_of_morpheme(pcu_idx, target_pcus, morphemes, lemma, "n"):
        orth_cat = "MoEndN1"
        if not correct and original_pcu == constant.zero_char:
            error_cat = "MoEndN1"
    
    #Rule 1: Assimilation of stem (unvoiced consonant is pronounced as voiced or vise versa)
    else:
        orth_cat, error_cat = annotator.check_for_stem_assimilation(taret_pcu, original_pcu, target_phon, orth_cat, error_cat)
        
        
    
    """
    Analogy
    """
    #Rule 1: You write a "between s" between two part of a composition word if you hear that "s". 
    if taret_pcu == "s" and annotator.n_or_space_between_two_morphemes(target_pcus[:pcu_idx], target_pcus[pcu_idx+1:], morphemes, "s"):
        orth_cat = "MoCoS1"
        if not correct and original_pcu == constant.zero_char:
            error_cat = "MoCoS1"
        
    #Rule 2: If you don't hear a "s" between two parts of a composition word, you don't write one.
    elif taret_pcu == constant.zero_char and len(target_pcus[pcu_idx+1:]) >= 3 and annotator.n_or_space_between_two_morphemes(target_pcus[:pcu_idx], target_pcus[pcu_idx+1:], morphemes, "|"):
        orth_cat = "MoCoS2"
        if not correct and original_pcu == "s":
            error_cat = "MoCoS2"
    
    """
    Hyphen
    """
    #Rule 1: Use a hyphen in case of word repetition (e.g., zon- en feestdagen)
    if taret_pcu == "#" and (pcu_idx == 0 or annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1)):
        orth_cat = "MoHy1"
        if not correct:
            error_cat = "MoHy1a"
        
    #Rule 2: Use a hyphen in composion words containing abbreviations, numbers, single letters and special characters (abc-boek, %-teken)
    elif taret_pcu == "#" and "-" in morphemes[-1] and pos_label != "SPEC":
        orth_cat = "MoHy1"
        if not correct:
            error_cat = "MoHy1b"
        
    #Rule 3: Use a hyphen in names (Gert-Jan)
    elif taret_pcu == "#" and "-" in morphemes[-1] and pos_label == "SPEC":
        orth_cat = "MoHy1"
        if not correct:
            error_cat = "MoHy1c"
        
    #Rule 4: Use a hyphen in case of vowel collision (e.g., zonne-energie)
    elif taret_pcu == "#" and "-" not in morphemes[-1] and target_pcus[pcu_idx-1] in constant.all_vowels and target_pcus[pcu_idx+1] in constant.all_vowels:
        orth_cat = "MoHy1"
        if not correct:
            error_cat = "MoHy1d"

    #Rule 5: Other hyphens
    elif taret_pcu == "#":
        orth_cat = "MoHy1"
        if not correct:
            error_cat = "MoHy1e"
    
    return orth_cat, error_cat

def check_for_noun_syntax_rules(correct, orth_cat, target_phons, target_pcus, original_pcus, pcu_idx, pos_label, pos_details, morphemes):
    
    error_cat = "-"
    taret_pcu = target_pcus[pcu_idx]
    original_pcu = original_pcus[pcu_idx]
    target_phon = target_phons[pcu_idx]
    
    """
    Number
    """
    #Rule 1: Plural noun forms end in -s or -n        
    if (pos_label != "WW") and ("mv" in pos_details or "mv-n" in pos_details) and taret_pcu == "s" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "SyNum1a"
        if not correct:
            error_cat = "SyNum1a"
    elif (pos_label != "WW") and ("mv" in pos_details or "mv-n" in pos_details) and taret_pcu == "n" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "SyNum1b"
        if not correct:
            error_cat = "SyNum1b"
    
    """
    Sjwa in non-verb suffixes
    """
    #Rule 1: Some suffices exist of an "e" (sjwa) , or "e" (sjwa) + "n"
    if taret_pcu == "e" and not "WW" in pos_label and "met-e" in pos_details and (annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1) or annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2)):
        orth_cat = "SySjwa1"
        if not correct:
            if "mv-n" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
                error_cat = "SySjwa1"
            elif annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
                error_cat = "SySjwa1" 
    
    """
    Composition words
    """
    #Rule 1b: Write composition words that exists of two or more nouns as much as possible together            
    if taret_pcu == constant.zero_char and annotator.n_or_space_between_two_morphemes(target_pcus[:pcu_idx], target_pcus[pcu_idx+1:], morphemes, "|"):
        if not correct and original_pcu == "|":
            orth_cat = "Ins"
            error_cat = "SySp1a"
    
    #Rule 1b: Write non-composition words also as much as possible together
    elif taret_pcu == constant.zero_char and original_pcu == "|":
        orth_cat = "Ins"
        error_cat = "SySp1b"
    
    #Rule 2: Between -n needs to be written between two morphemes in some composition words    
    elif taret_pcu == "n" and len(target_pcus[pcu_idx+1:]) >= 3 and annotator.n_or_space_between_two_morphemes(target_pcus[:pcu_idx], target_pcus[pcu_idx+1:], morphemes, "n"):
        orth_cat = "SyCoN1"
        if not correct and original_pcu == "-":
            error_cat = "SyCoN1"
            
    #Rule 3: Between -n is not written between two morphemes in some composition words 
    elif taret_pcu == constant.zero_char  and len(target_pcus[pcu_idx+1:]) >= 3 and annotator.n_or_space_between_two_morphemes(target_pcus[:pcu_idx], target_pcus[pcu_idx+1:], morphemes, "|"):
        orth_cat = "SyCoN2"  
        if not correct and original_pcu == "n":
            error_cat = "SyCoN2"      
            
    return orth_cat, error_cat

def check_for_verb_syntax_rules(correct, orth_cat, target_phons, target_pcus, original_pcus, pcu_idx, pos_label, pos_details, lemma):
    
    error_cat = "-"
    taret_pcu = target_pcus[pcu_idx]
    original_pcu = original_pcus[pcu_idx]
    target_phon = target_phons[pcu_idx]
    
    """
    Number
    """
    #Rule 1: Plural verb forms end in -n (pv tt, pv vt, vd, od)
    if taret_pcu == "n" and ("mv" in pos_details or "mv-n" in pos_details) and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "SyNum2"
        if not correct and original_pcu == constant.zero_char:
            error_cat = "SyNum2"
    
    """
    Person
    """
    #Rule 1: Present 2nd/3th person singular have suffix t
    if taret_pcu == "t" and "met-t" in pos_details and "pv" in pos_details and "tgw" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "SyPer1"
        if not correct:
            if original_pcu == "d":
                error_cat = "SyPer1a"
            else:
                error_cat = "SyPer1b"
            
        
    """
    Time Past Tense: 't Exkofschip rules: stam + te(n)/de(n)
    """
    if taret_pcu in ["t", "tt", "d", "dd"] and ("pv" in pos_details or "vd" in pos_details):
        #Rule 1: If last letter of word stem in "'t ex kofschip", suffix starts with "t"
        if "pv" in pos_details and "verl" in pos_details and not lemma in constant.strong_verbs:
            if taret_pcu == "t" and "ev" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
                orth_cat = "SyVt1"
                if not correct:
                    if original_pcu == "d":
                        error_cat = "SyVt1a"
                    elif original_pcu == "tt":
                        error_cat = "SyVt1b"
                    else:
                        error_cat = "SyVt1d"

            elif taret_pcu == "tt" and "ev" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
                orth_cat = "SyVt1"
                if not correct:
                    if original_pcu == "d":
                        error_cat = "SyVt1a"
                    elif original_pcu == "t":
                        error_cat = "SyVt1c"
                    else:
                        error_cat = "SyVt1d"    

            elif taret_pcu == "t" and "mv" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -3):
                orth_cat = "SyVt1"
                if not correct:
                    if original_pcu == "d":
                        error_cat = "SyVt1a"
                    elif original_pcu == "tt":
                        error_cat = "SyVt1b"
                    else:
                        error_cat = "SyVt1d" 

            elif taret_pcu == "tt" and "mv" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -3):
                orth_cat = "SyVt1"
                if not correct:
                    if original_pcu == "d":
                        error_cat = "SyVt1a"
                    elif original_pcu == "t":
                        error_cat = "SyVt1c"
                    else:
                        error_cat = "SyVt1d"
                
            #'t exkofschiprule 2
            #Rule 2: If last letter of word stem not in "'t ex kofschip", suffix starts with "d"
            elif taret_pcu == "d" and "ev" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
                orth_cat = "SyVt2"
                if not correct:
                    if original_pcu == "t":
                        error_cat = "SyVt2a"
                    elif original_pcu == "dd":
                        error_cat = "SyVt2b"
                    else:
                        error_cat = "SyVt2d"

            elif taret_pcu == "dd" and "ev" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
                orth_cat = "SyVt2"
                if not correct:
                    if original_pcu == "t":
                        error_cat = "SyVt1a"
                    elif original_pcu == "d":
                        error_cat = "SyVt2c"
                    else:
                        error_cat = "SyVt2d"    

            elif taret_pcu == "d" and "mv" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -3):
                orth_cat = "SyVt2"
                if not correct:
                    if original_pcu == "t":
                        error_cat = "SyVt2a"
                    elif original_pcu == "dd":
                        error_cat = "SyVt2a"
                    else:
                        error_cat = "SyVt2d" 

            elif taret_pcu == "dd" and "mv" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -3):
                orth_cat = "SyVt2"
                if not correct:
                    if original_pcu == "t":
                        error_cat = "SyVt1a"
                    if original_pcu == "tt":
                        error_cat = "SyVt2b"
                    elif original_pcu == "d":
                        error_cat = "SyVt2c"
                    else:
                        error_cat = "SyVt2d" 
        
        elif "vd" in pos_details:
            #Rule 1: If last letter of word stem in "'t ex kofschip", suffix starts with "t"
            if taret_pcu == "t" and "met-e" in pos_details and "mv-n" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -3):
                orth_cat = "SyVd1"
                if not correct:
                    if original_pcu == "d":
                        error_cat = "SyVd1a"
                    else:
                        error_cat = "SyVd1b"
                    
            elif taret_pcu == "t" and "met-e" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
                orth_cat = "SyVd1"
                if not correct:
                    if original_pcu == "d":
                        error_cat = "SyVd1a"
                    else:
                        error_cat = "SyVd1b" 
                    
            elif taret_pcu == "t" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
                orth_cat = "SyVd1"
                if not correct:
                    if original_pcu == "d":
                        error_cat = "SyVd1a"
                    else:
                        error_cat = "SyVd1b" 
            
            #Rule 2: If last letter of word stem not in "'t ex kofschip", suffix starts with "d"
            elif taret_pcu == "d" and "met-e" in pos_details and "mv-n" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -3):
                orth_cat = "SyVd2"
                if not correct:
                    if original_pcu == "t":
                        error_cat = "SyVd2a"
                    else:
                        error_cat = "SyVd2b" 
                    
            elif taret_pcu == "d" and "met-e" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
                orth_cat = "SyVd2"
                if not correct:
                    if original_pcu == "t":
                        error_cat = "SyVd2a"
                    else:
                        error_cat = "SyVd2b"  
                    
            elif taret_pcu == "d" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
                orth_cat = "SyVd2"
                if not correct:
                    if original_pcu == "t":
                        error_cat = "SyVd2a"
                    else:
                        error_cat = "SyVd2b"  
    
    elif taret_pcu == "n" and ("vd" in pos_details) and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "SyVd3"
        if not correct:
            error_cat = "SyVd3"
    
    """
    Infinitives: End in -n
    """
    if taret_pcu == "n" and ("inf" in pos_details) and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
        orth_cat = "SyInf1"
        if not correct:
            error_cat = "SyInf1"
    
    """
    Onvoltooid Deelwoorden: 't Exkofschip rules: stam + te(n)/de(n)
    """
    #Rule 1: The suffix of participia always starts with "d"   
    if taret_pcu == "d" and "od" in pos_details:
        
        if taret_pcu == "d" and "met-e" in pos_details and "mv-n" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -3):
            orth_cat = "SyOd1"  
            if not correct:
                if original_pcu == "t":
                    error_cat = "SyOd1a" 
                else:
                    error_cat = "SyOd1b"
                
                    
        elif taret_pcu == "d" and "met-e" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
            orth_cat = "SyOd1"  
            if not correct:
                if original_pcu == "t":
                    error_cat = "SyOd1a" 
                else:
                    error_cat = "SyOd1b"  
                    
        elif taret_pcu == "d" and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
            orth_cat = "SyOd1"  
            if not correct:
                if original_pcu == "t":
                    error_cat = "SyOd1a" 
                else:
                    error_cat = "SyOd1b" 
    
    """
    Sjwa in verb suffixes
    """
    #Rule 1: Some suffices have an "e" (sjwa) in second position after the "d" or "t".
    if taret_pcu == "e" and "WW" in pos_label and "met-e" in pos_details and (annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1) or annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2)):
        if "mv-n" in pos_details and annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -2):
            orth_cat = "SySjwa2"
            if not correct:
                error_cat = "SySjwa2"
        elif annotator.is_xth_but_last_letter(pcu_idx, target_pcus, -1):
            orth_cat = "SySjwa2"
            if not correct:
                error_cat = "SySjwa2"
        
    return orth_cat, error_cat
    
def check_for_etymology_rules(correct, orth_cat, target_phons, target_pcus, original_pcus, pcu_idx):
    
    error_cat = "-"
    target_pcu = target_pcus[pcu_idx].lower()
    original_pcu = original_pcus[pcu_idx].lower()
    target_phon = target_phons[pcu_idx]

    if not correct and target_phon != constant.zero_char and (target_phon in constant.phon_dict.keys()) and (target_pcu in constant.phon_dict[target_phon]) and (original_pcu in constant.phon_dict[target_phon]):
            orth_cat = "Un"
            error_cat = "UnSub1b"
    # except:
    #     print("key error:", target_phon, "---", "\n", target_phons, "\n", target_pcus, "\n", original_pcus,"\n", pcu_idx)
        

    return orth_cat, error_cat

def check_for_unmarked_rules(correct, orth_cat, target_phons, target_pcus, original_pcus, pcu_idx):
    error_cat = "-"
    taret_pcu = target_pcus[pcu_idx]
    original_pcu = original_pcus[pcu_idx]
    target_phon = target_phons[pcu_idx]
    
    if orth_cat == "-":
        orth_cat = "Un"
    
    #The unmarked principle: Each phoneme is converted to a corresponding grapheme.
    if not correct:
        
        #Deletion of PCU (automobilisten -> automob-listen)
        if target_phon != constant.zero_char and original_pcu == constant.zero_char:
            error_cat = "UnDel1"

        #Insertion of PCU (binnen- -> binnens)
        elif target_phon == constant.zero_char and taret_pcu == constant.zero_char:
            orth_cat = "Ins"
            error_cat = "UnIns1"
            
#         elif target_phon != "-" and (taret_pcu in phon_dict[target_phon]) and (original_pcu in phon_dict[target_phon]):
#             error_cat = "UnSub1"

        #Rule UnSub2: Substitution where the target and original are no homophones of each other.

        #Target is reversed original
        elif target_phon != constant.zero_char and taret_pcu == original_pcu[::-1]:
            error_cat = "UnSub2a"
            
        #Partial deletion of PCU (reus -> re-s)
        elif target_phon != constant.zero_char and original_pcu in taret_pcu:
            error_cat = "UnSub2b"

        #Partial insertion of PCU (b-innen -> buinen)
        elif target_phon != constant.zero_char and taret_pcu in original_pcu:
            error_cat = "UnSub2c"

        #Complete substitution of PCU (is -> ik or buiten -> boeten)
        elif target_pcus != constant.zero_char and original_pcus != "-":
            error_cat = "UnSub2d"

        else:
            error_cat = "UnOther"
            
    return orth_cat, error_cat

def classify_cap_error(correct, target_pcus, original_pcus, pcu_idx, pos_label, pos_details, begin_sentence_cap):    
    
    orth_cap_cat = "-"
    error_cap_cat = "-"

    original_pcu = original_pcus[pcu_idx]
    taret_pcu = target_pcus[pcu_idx]
    
    """
    Syntax: Capital letters
    """
    #Every sentence starts with a capital letter
    if pcu_idx == 0 and taret_pcu[0].isupper() and begin_sentence_cap == 1:
        orth_cap_cat = "SyCap1"
        if not correct and original_pcu[0].islower():
            error_cap_cat = "SyCap1"      
        

    """
    Semantics: Capital letters
    """
    #Rule 1: Every proper name, title and some abbreviations start with a capital letter
    if pcu_idx == 0 and taret_pcu[0].isupper() and begin_sentence_cap == 0 and pos_label == "SPEC" and not "afk" in pos_details:
        orth_cap_cat = "SemCap1"
        if not correct and original_pcu[0].islower():
            error_cap_cat = "SemCap1"

    #Semantics: Capital letters rule 2
    #Rule 2: Some abbreviations have a capital letter in the middle
    elif pcu_idx != 0 and taret_pcu[0].isupper() and begin_sentence_cap == 0 and pos_label == "SPEC" and "afk" in pos_details:
        orth_cap_cat = "SemCap2"
        if not correct and original_pcu[0].islower():
            error_cap_cat = "SemCap2"

    """
    Capital letter at wrong position
    """
    #Every not-first letter of a sentence and non-name is written with a lowercase letter
    if not correct and taret_pcu[0].islower() and original_pcu[0].isupper():
        error_cap_cat = "UnSub3a"   
        
    if not correct and orth_cap_cat == "-" and error_cap_cat == "-" and taret_pcu[0].isupper() and original_pcu[0].islower():
        error_cap_cat = "UnSub3b"  
    return orth_cap_cat, error_cap_cat