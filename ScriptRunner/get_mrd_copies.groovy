import com.atlassian.jira.issue.IssueManager
import com.opensymphony.workflow.InvalidInputException
import com.atlassian.applinks.api.ApplicationLink
import com.atlassian.applinks.api.ApplicationLinkService
import com.atlassian.applinks.api.application.confluence.ConfluenceApplicationType
import com.atlassian.jira.issue.Issue
import com.atlassian.sal.api.component.ComponentLocator
import com.atlassian.sal.api.net.Request
import com.atlassian.sal.api.net.Response
import com.atlassian.sal.api.net.ResponseException
import com.atlassian.sal.api.net.ResponseHandler
import groovy.json.JsonBuilder
import groovy.json.JsonSlurper
import com.atlassian.jira.issue.ModifiedValue
import com.atlassian.jira.issue.util.DefaultIssueChangeHolder
import com.atlassian.jira.component.ComponentAccessor

/**
 * Retrieve the primary confluence application link
 * @return confluence app link
 */
def ApplicationLink getPrimaryConfluenceLink() {
    def applicationLinkService = ComponentLocator.getComponent(ApplicationLinkService.class)
    final ApplicationLink conflLink = applicationLinkService.getPrimaryApplicationLink(ConfluenceApplicationType.class)
    return conflLink
}

def customFieldManager = ComponentAccessor.getCustomFieldManager()

// Log issue environment details
log.warn("Issue environment: ${issue.environment}")
def environment = Eval.me(issue.environment)
log.warn("Parsed environment: ${environment}")

def mrdPageId = environment?.pageIds?.mrd?.pageId
log.warn("MRD Page ID: ${mrdPageId}")

if (!mrdPageId) {
    log.warn("MRD Page ID is missing. Exiting script.")
    return
}

def confluenceLink = getPrimaryConfluenceLink()
assert confluenceLink
def authenticatedRequestFactory = confluenceLink.createImpersonatingAuthenticatedRequestFactory()

authenticatedRequestFactory
    .createRequest(Request.MethodType.GET, "rest/scriptrunner/latest/custom/getIssueMRDCopies?pageId=" + mrdPageId)
    .addHeader("Content-Type", "application/json")
    .addHeader("Accept", "application/json")
    .execute(new ResponseHandler() {
        void handle(Response response) throws ResponseException {
            log.warn("HTTP response status code: ${response.statusCode}")
            if (response.statusCode != HttpURLConnection.HTTP_OK) {
                log.warn("HTTP request failed with response: ${response.getResponseBodyAsString()}")
                throw new Exception(response.getResponseBodyAsString())
            } else {
                def responseObject = new JsonSlurper().parseText(response.responseBodyAsString)
                log.warn("Parsed response object: ${responseObject}")

                Double productCopies = responseObject["productCopies"] as Double
                Double partCopies = responseObject["partCopies"] as Double
                
                log.warn("Retrieved productCopies: ${productCopies}")
                log.warn("Retrieved partCopies: ${partCopies}")

                def cfMainProductCopies = customFieldManager.getCustomFieldObjectByName("Main Product Copies")
                def cfReplacementPartsCopies = customFieldManager.getCustomFieldObjectByName("Replacement Parts Copies")

                def currentMainProductCopies = issue.getCustomFieldValue(cfMainProductCopies)
                def currentReplacementPartsCopies = issue.getCustomFieldValue(cfReplacementPartsCopies)
                
                log.warn("Old Main Product Copies: ${currentMainProductCopies}")
                log.warn("Old Replacement Parts Copies: ${currentReplacementPartsCopies}")

                if (cfMainProductCopies && cfReplacementPartsCopies) {
                    if (productCopies != null && partCopies != null) {
                        log.warn("Updating Main Product Copies and Replacement Parts Copies...")
                        // Use setCustomFieldValue method for updating the values
                        issue.setCustomFieldValue(cfMainProductCopies, productCopies)
                        issue.setCustomFieldValue(cfReplacementPartsCopies, partCopies)
                        log.warn("New Main Product Copies: ${issue.getCustomFieldValue(cfMainProductCopies)}")
                        log.warn("New Replacement Parts Copies: ${issue.getCustomFieldValue(cfReplacementPartsCopies)}")
                    } else {
                        log.warn("Retrieved values are null, skipping update.")
                    }
                } else {
                    log.warn("One or both custom fields are not found.")
                }
            }
        }
})
