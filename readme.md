run those commands inside ipyhton or other interactive session!

how to collect all candaidate models and data:
===========

Collect the model meta data:
-----------
1. extract the tex table from the paper to candidates.tex
2. parse_candidates_tex.py

3. main.py for the ones from the old system of the list candidates.csv
4. main.py:writeModelsToFile() to write those to tmp0_old_models.csv

5. get_new_models_list.py
6. get_new_models_list.py:fetch_talk() to get the new ones from the talk page
7. get_new_models_list.py:write_models() to write them to the file tmp1_new_models.csv

8. get_new_models_list.py:collect_all_models_() to merge the two lists to "tmp2_all_models.csv"

Collect model data (state / config and parse:
----------

9. get_state_and_config.py --> tmp3_all_models_with_state_id_cfg.csv
10. parse_State_and_config.py --> all_candidates_data.csv
11. parse_State_and_config.py:print_data()
