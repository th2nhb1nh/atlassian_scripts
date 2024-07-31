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

def environment = Eval.me(issue.environment)
def mrdPageId = environment.pageIds.mrd.pageId

def confluenceLink = getPrimaryConfluenceLink()
assert confluenceLink
def authenticatedRequestFactory = confluenceLink.createImpersonatingAuthenticatedRequestFactory()

log.warn(mrdPageId)

authenticatedRequestFactory
            .createRequest(Request.MethodType.GET, "rest/scriptrunner/latest/custom/getIssueMRDCopies?pageId=" + mrdPageId)
            .addHeader("Content-Type", "application/json")
            .addHeader("Accept", "application/json")
            .execute(new ResponseHandler<Response>() {
                @Override
                void handle(Response response) throws ResponseException {
                    if(response.statusCode != HttpURLConnection.HTTP_OK) {
                        throw new Exception(response.getResponseBodyAsString())
                    }
                    else {
                        def responseObject = new JsonSlurper().parseText(response.responseBodyAsString)
                        Double productCopies = responseObject["productCopies"]
                        Double partCopies = responseObject["partCopies"]
                        log.warn(productCopies)
                        log.warn(partCopies)
                        
                        def cfMainProductCopies = customFieldManager.getCustomFieldObjectByName("Main Product Copies")
                        def cfReplacementPartsCopies = customFieldManager.getCustomFieldObjectByName("Replacement Parts Copies")
                        cfMainProductCopies.updateValue(null, issue, new ModifiedValue(issue.getCustomFieldValue(cfMainProductCopies), productCopies), new DefaultIssueChangeHolder());
                        cfReplacementPartsCopies.updateValue(null, issue, new ModifiedValue(issue.getCustomFieldValue(cfReplacementPartsCopies), partCopies), new DefaultIssueChangeHolder());
                    }
                }
        })