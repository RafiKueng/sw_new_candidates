run those commands inside ipyhton or other interactive session!

how to collect all candaidate models and data:
===========

Collect the model meta data:
-----------

1. extract the tex table from the paper to candidates.tex (only body)
    candidates.py will automatically parse and load this table if its imported somewhere
    and save the table as csv (to check) and pickle (as cache: for future faster load)
    if you update the table, remove the candidates.pickle!!


2. run get_old_models.py
    fetches all the models metadata from the old system (mite) that are on the
    candidates list. (or loads the corresponding pickles file if already done once)
    output: tmp_old_models.csv (for inspection)
            tmp_old_models.pickle (for caching, later usage)

3. run get_new_models.py
    fetches all models from spacewarps talk thread
    output: tmp_new_models.csv (for inspection)
            tmp_new_models.pickle (for caching, later usage)

4. run get_all_models.py
    combines the old and new models lists
    output: tmp_all_models.csv (for inspection)
            tmp_all_models.pickle (for caching, later usage)

5. run get_state_and_config.py
    (you don't actually need to run the former three..)
    this executes get_all_models and then fetches for all those models
    the state and the config file from the appropriate source
    download is skipped if file is already present
    output: data/*.state and data/*.cfg files
    
6. run parse_state_and_config.py
    run inside a glass interactive shell:
    ../glass/interactive_glass
    %run parse_state_and_config.py
    This updates the data structure with data from the config files and
    calculates important data from the state file (total mass)
    output: all_data.csv (for inspection)
            all_data.pickle (for caching, later usage)

