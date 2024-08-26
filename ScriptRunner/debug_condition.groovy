import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.bc.issue.IssueService
import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.issue.IssueInputParametersImpl

def customFieldManager = ComponentAccessor.getCustomFieldManager()

def cfDebugStation = customFieldManager.getCustomFieldObject(13300L)
String debugStation = issue.getCustomFieldValue(cfDebugStation)

debugStation == "AMZ A+ Content"
