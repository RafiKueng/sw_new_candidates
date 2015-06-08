run those commands inside ipyhton or other interactive session!

how to collect all candaidate models:

1. extract the tex table from the paper to candidates.tex
2. parse_candidates_tex.py

3. main.py for the ones from the old system of the list candidates.csv
4. main.py:writeModelsToFile() to write those to old_models.csv

-----

5. get_new_models_list.py
6. get_new_models_list.py:fetch_talk() to get the new ones from the talk page
7. get_new_models_list.py:run write_models() to write them to the file new_models.csv

8. get_new_models_list.py:collect_all_models_() to merge the two lists to "all_models.csv"

-----

