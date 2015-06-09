run those commands inside ipyhton or other interactive session!

how to collect all candaidate models and data:
===========

Collect the model meta data:
-----------

1. extract the tex table from the paper to candidates.tex (only body)
    candidates.py will automatically parse and load this table if its imported somewhere
    and save the table as csv (to check) and pickle (as cache: for future faster load)
    if you update the table, remove the candidates.pickle!!


2. run main.py
    fetches all the models metadata from the old system (mite) that are on the
    candidates list.

4. main.py:writeModelsToFile() to write those to tmp0_old_models.csv

5. get_new_models_list.py
6. get_new_models_list.py:fetch_talk() to get the new ones from the talk page
7. get_new_models_list.py:write_models() to write them to the file tmp1_new_models.csv

8. get_new_models_list.py:collect_all_models_() to merge the two lists to "tmp2_all_models.csv"

Collect model data (state / config and parse:
----------

9. get_state_and_config.py --> tmp3_all_models_with_state_id_cfg.csv
10. open ../glass/interactive_glass
11. parse_State_and_config.py --> all_candidates_data.csv
12. parse_State_and_config.py:print_data()
