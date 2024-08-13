# atlassian_scripts

get jira workspace id by:

```
https://<JSM Premium Site Name>.atlassian.net/rest/servicedeskapi/assets/workspace
```

steps to run files:

## fetch all addons
1. replace the placeholders in `.env.sample` with your confifentials
2. `fetch_addons_data.py` to fetch all data
3. `process_addons_data.py` to convert the data into the suitable format to create jira assets objects

OR you can run this file, which would conduct all the tasks of the above files, at one run 
```python
python3 marketplace_get_all_addons.py
```

## fetch new addons (limit 50 addons for each)
```python
python3 marketplace_fetch_new_addons.py
```