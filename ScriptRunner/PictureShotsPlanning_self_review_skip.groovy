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

def cfPictureShotPlanReview = customFieldManager.getCustomFieldObjectByName("Picture Shots Planning Task Review Checklist")
def cfPictureShotPlanReviewType = cfPictureShotPlanReview.getCustomFieldType()
def checklistItemsForPictureShotPlanTaskReview = []

rank = 0
issue.getCustomFieldValue(cfPictureShotPlanReview).each { pageUrl ->
    def checklistItemForPictureShotPlanTaskReview = cfPictureShotPlanReviewType.getSingularObjectFromString(String.format('{"name" : "%s", "checked" : true, "mandatory" : false, "rank" : %s}', pageUrl, rank))
    checklistItemsForPictureShotPlanTaskReview.add(checklistItemForPictureShotPlanTaskReview)
    rank++
}

log.warn("checklistItemsForPictureShotPlanTaskReview:" + new JsonBuilder(checklistItemsForPictureShotPlanTaskReview).toString())
cfPictureShotPlanReview.updateValue(null, issue, new ModifiedValue(issue.getCustomFieldValue(cfPictureShotPlanReview), checklistItemsForPictureShotPlanTaskReview), new DefaultIssueChangeHolder())

issueInputParameters.setSkipScreenCheck(true)
