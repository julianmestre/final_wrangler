import os
import shutil
from functools import reduce
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt




def compile_final_reports(df, problems):
    """
    Args:
    - df (DataFrame)          : final evaluation data frame
    - problems (list)         : list of problem/questions names

    Returns:
    - ans (dict: int -> str)  : dictionary mapping sids to reports
    """

    ans = dict()

    for tup in df.itertuples(index=False):

        temp = []
        total_marks = 0

        # provide summary at the top
        sid = tup[0]
        temp.append('Summary:')
        temp.append(' - SID: {}'.format(sid))
        temp.append(' - Total marks: {}')
        temp.append('')

        for i, prob in enumerate(problems):
            prob_marks = tup[2*i+1]
            total_marks += prob_marks
            temp.append('{} ({} marks):'.format(prob, prob_marks))

            for rubric_item in tup[2*i+2]:
                temp.append(' - {}'.format(rubric_item))
            
            temp.append('')

        # update "total marks" line
        temp[2] = temp[2].format(total_marks)

        ans[sid] = '\n'.join(temp)
    
    return ans


def read_gradescope_evaluations(
    gs_eval_folder
):
    """
    Read Gradescope evaluation csv files and merge them into a single pandas data frame

    Args:
    - gs_eval_folder (str)    : folder holding the evaluation csv files

    Returns:
    - ans (DataFrame)         : concatenation of smaller files with extra column
    """

    def problem_name_from_file_name(x):
        # skip the first number and the .csv extension and replace _ with " "
        return " ".join(x[:-4].split('_')[1:])

    files = os.listdir(gs_eval_folder)
    # Sort files
    files.sort(key=lambda x: int(x.split('_')[0]))

    dfs = []
    prob_names = []

    for file_name in files:
        full_file_file = os.path.join(gs_eval_folder, file_name)
        aux = pd.read_csv(
            full_file_file,
            dtype = {'SID': 'Int32'},
            skipfooter = 4,    #  ignore rubric points and whatnot,
            engine='python',
        )
        aux.set_index('SID', inplace=True)
        cols = list(aux.columns)
        rubric_columns = cols[cols.index('Submission Time') + 1: cols.index('Adjustment')]

        temp = aux[rubric_columns].stack()
        applied_rubrics_map = dict()
        for sid, rubric in temp[temp == True].index:
            if sid not in applied_rubrics_map:
                applied_rubrics_map[sid] = []
            applied_rubrics_map[sid].append(rubric)
        aux['applied_rubrics'] = aux.index.map(applied_rubrics_map)
        
        old_cols = ['Score', 'applied_rubrics']
        aux = aux[old_cols].copy()
        prob_name = problem_name_from_file_name(file_name)
        aux.columns = pd.MultiIndex.from_tuples(
            [(prob_name, col) for col in old_cols]
        )

        prob_names.append(prob_name)
        dfs.append(aux)
    
    ans = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True, how='outer'), dfs).reset_index()

    # add reports column
    reports = compile_final_reports(ans, prob_names)
    ans['report'] = ans['SID'].map(reports)

    return ans
        


