import com.atlassian.jira.component.ComponentAccessor

//reset environment
def environment = Eval.me(issue.environment)
environment.stages."SKU-UP Initiation" = null
issue.environment = environment.inspect()

//reset fields
def customFieldManager = ComponentAccessor.getCustomFieldManager()
String[] fieldIds = ["10823", "10826", "10821", "10824", "10825"]
for (String fieldId : fieldIds) {
    issue.setCustomFieldValue(customFieldManager.getCustomFieldObject("customfield_" + fieldId), null)
}
