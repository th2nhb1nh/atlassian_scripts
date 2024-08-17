import com.atlassian.jira.component.ComponentAccessor 
import groovy.json.JsonBuilder
import com.atlassian.jira.issue.ModifiedValue
import com.atlassian.jira.issue.util.DefaultIssueChangeHolder

def customFieldManager = ComponentAccessor.customFieldManager
def optionsManager = ComponentAccessor.optionsManager
def issueManager = ComponentAccessor.issueManager 

def customField = customFieldManager.getCustomFieldObject(11205L)
def fieldConfig = customField.getRelevantConfig(issue) 
def option = optionsManager.getOptions(fieldConfig).find { it.value == "Done" }
issueInputParameters.addCustomFieldValue(customField.id, option.optionId as String)

def cfMrdReview = customFieldManager.getCustomFieldObjectByName("Picture Shots Planning Task Review Checklist")
def cfMrdReviewType = cfMrdReview.getCustomFieldType()
def checklistItemsForMrdTaskReview = []

rank = 0
issue.getCustomFieldValue(cfMrdReview).each { pageUrl ->
    def checklistItemForMrdTaskReview = cfMrdReviewType.getSingularObjectFromString(String.format('{"name" : "%s", "checked" : true, "mandatory" : false, "rank" : %s}', pageUrl, rank))
    checklistItemsForMrdTaskReview.add(checklistItemForMrdTaskReview)
    rank++
}

log.warn("checklistItemsForMrdTaskReview:" + new JsonBuilder(checklistItemsForMrdTaskReview).toString())
cfMrdReview.updateValue(null, issue, new ModifiedValue(issue.getCustomFieldValue(cfMrdReview), checklistItemsForMrdTaskReview), new DefaultIssueChangeHolder())

issueInputParameters.setSkipScreenCheck(true)
