import com.atlassian.jira.component.ComponentAccessor

//reset environment
def environment = Eval.me(issue.environment)
environment.stages."Web Meta Desc" = null
environment.stages."eBlast Post" = null
environment.stages."AMZ Brand Page" = null
issue.environment = environment.inspect()

//reset fields
def customFieldManager = ComponentAccessor.getCustomFieldManager()
String[] fieldIds = ["14700", "14702", "14703", "14600", "14602", "14601", "14402"]
for (String fieldId : fieldIds) {
    issue.setCustomFieldValue(customFieldManager.getCustomFieldObject("customfield_" + fieldId), null)
}