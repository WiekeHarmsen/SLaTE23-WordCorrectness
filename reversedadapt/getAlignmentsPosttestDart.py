# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 10:40:08 2020

@author: wieke
"""
import os
import glob
import textgrids as tg
import re
import pandas as pd
import reversedadapt.adapt_graph as adapt_graph

def reverse(s): 
    str = "" 
    for i in s: 
      str = i + str
    return str

def removeInsertions(s):
    return s.replace("-", "")

def trimPipesAndSpaces(s):
    return s.replace("|", " ").strip()

def determineCorrectness(row):
    return row['prompt'] in row['aligned_asrTrans'] or row['prompt'] in row['reversed_aligned_asrTrans']

def applyReversedAlignment(prompt, asrTrans):
    # Get reversed prompt and asrTrans
    rev_prompt = reverse(prompt)
    rev_asrTrans = reverse(asrTrans)

    # Align reversed prompt and asrTrans
    dist_score, nsub, ndel, nins, align_rev_ref, align_rev_hyp = adapt_graph.align_dist(rev_prompt, rev_asrTrans)

    # De-reverse the aligned transcriptions        
    align_ref_rev = reverse(align_rev_ref)
    align_hyp_rev = reverse(align_rev_hyp)

    # Perform correction for ----| parts (change ----| to |----)    
    begin = 0
    selection_list = []
    
    #Search indices of -----| parts
    while re.search("\-+\|", align_ref_rev[begin:]) != None:
        selection = []
        start_span = re.search("\-+\|", align_ref_rev[begin:]).span()[0] +begin
        end_span = re.search("\-+\|", align_ref_rev[begin:]).span()[1] +begin
        selection.append(start_span)
        selection.append(end_span)
        selection_list.append(selection)
        begin = end_span
    
    #Change first - and last | in selection list
    for sel in selection_list:
        align_ref_rev = align_ref_rev[:sel[0]] + "|" + align_ref_rev[sel[0] + 1:]
        align_ref_rev = align_ref_rev[:sel[1]-1] + "-" + align_ref_rev[sel[1]:]   

    return align_ref_rev, align_hyp_rev

def splitAlignmentsIntoSegments(align_ref_rev, align_hyp_rev, align_ref, align_hyp):
    indices_rev = [0] + [i.start() for i in re.finditer("\|", align_ref_rev)] + [len(align_ref_rev)] + [9999]
    align_ref_rev_list = [align_ref_rev[indices_rev[idx]: indices_rev[idx+1]] for idx, item in enumerate(indices_rev) if item != 9999][:-1]
    align_hyp_rev_list = [align_hyp_rev[indices_rev[idx]: indices_rev[idx+1]] for idx, item in enumerate(indices_rev) if item != 9999][:-1]

    indices = [0] + [i.start() for i in re.finditer("\|", align_ref)]  + [len(align_ref)] + [9999]
    align_ref_list = [align_ref[indices[idx]: indices[idx+1]] for idx, item in enumerate(indices) if item != 9999][:-1]
    align_hyp_list = [align_hyp[indices[idx]: indices[idx+1]] for idx, item in enumerate(indices) if item != 9999][:-1]

    return align_ref_rev_list, align_hyp_rev_list, align_hyp_list

def getAlignmentsPromptAsrTrans(prompt, asrTrans):
    # Preprocess strings -> replace spaces with |
    prompt = prompt.replace(" ", "|")
    asrTrans = asrTrans.replace(" ", "|")

    # Apply reversed alignment process
    align_ref_rev, align_hyp_rev = applyReversedAlignment(prompt, asrTrans)

    # Apply normal alignment process
    dist_score, nsub, ndel, nins, align_ref, align_hyp = adapt_graph.align_dist(prompt, asrTrans)

    # Split alignments into segments that match the prompt
    align_ref_rev_list, align_hyp_rev_list, align_hyp_list = splitAlignmentsIntoSegments(align_ref_rev, align_hyp_rev, align_ref, align_hyp)
    
    # Create output DataFrame
    outputDF = pd.DataFrame()
    outputDF['prompt'] = pd.Series(align_ref_rev_list).apply(removeInsertions).apply(trimPipesAndSpaces)
    outputDF['aligned_asrTrans'] = pd.Series(align_hyp_list).apply(trimPipesAndSpaces)
    outputDF['reversed_aligned_asrTrans'] = pd.Series(align_hyp_rev_list).apply(trimPipesAndSpaces)
    outputDF['correct'] = outputDF.apply(determineCorrectness, axis=1)

    outputDF = outputDF.set_index("prompt")
    print(outputDF)
    return outputDF

# def main():
#     getAlignmentsPromptAsrTrans("jong hallo vergeten doei", "jing h hallo doe doei")
#     getAlignmentsPromptAsrTrans("jong onze zieke", "jon jong z zieke zeker")
#     getAlignmentsPromptAsrTrans("jong zieke", "jong jon zieke")

# main()