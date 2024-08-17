import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.bc.issue.IssueService
import com.atlassian.jira.project.ProjectManager
import com.atlassian.jira.security.roles.ProjectRoleManager
import com.atlassian.jira.security.roles.ProjectRoleActors
import com.opensymphony.workflow.InvalidInputException

Closure isUserMemberOfRole = { String role ->
            ProjectManager projectManager = ComponentAccessor.getProjectManager()
            ProjectRoleManager projectRoleManager = ComponentAccessor.getComponent(ProjectRoleManager)
            ProjectRoleActors projectRoleActors = projectRoleManager.getProjectRoleActors(projectRoleManager.getProjectRole(role), issue.getProjectObject())
            def currentUser = ComponentAccessor.getJiraAuthenticationContext().getLoggedInUser()
            projectRoleActors.getUsers().contains(currentUser)
        }

def currentUser = ComponentAccessor.getJiraAuthenticationContext().getLoggedInUser()
if ( !isUserMemberOfRole('Administrators')) {
def roleToCheck = "Product Manager"
if (!isUserMemberOfRole(roleToCheck)) {			
    invalidInputException = new InvalidInputException(String.format("Only %s can execute this transition", roleToCheck))
}
}

def isProjectLead(user) {
    return user.name == issue.getProjectObject().getProjectLead().name
}
