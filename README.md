# atlassian_scripts

Get Jira Workspace ID by:

```
https://<JSM Premium Site Name>.atlassian.net/rest/servicedeskapi/assets/workspace
```

Steps to run files:
1. Replace the placeholders in `.env.sample` with your confifentials
2. `fetch_addons_data.py` to fetch all data
3. `process_addons_data.py` to convert the data into the suitable format to create Jira Asset objects

OR you can run this file, which would conduct all the tasks of the above files, at one run.
4. `marketplace_get_all_addons.py`
