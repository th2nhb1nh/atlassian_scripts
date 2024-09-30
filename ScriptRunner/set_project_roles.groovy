import com.atlassian.jira.issue.Issue
//import com.atlassian.jira.ComponentManager
import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.issue.fields.CustomField
import com.atlassian.jira.issue.CustomFieldManager
import com.atlassian.jira.user.ApplicationUser
import com.atlassian.jira.user.util.UserManager
import com.atlassian.jira.security.JiraAuthenticationContext
import com.atlassian.jira.security.roles.*
import com.atlassian.jira.issue.IssueManager
import com.atlassian.jira.issue.link.IssueLinkManager
import com.atlassian.jira.issue.MutableIssue
import com.atlassian.jira.issue.ModifiedValue
import com.atlassian.jira.issue.util.DefaultIssueChangeHolder
import groovy.xml.MarkupBuilder
import com.onresolve.scriptrunner.runner.customisers.WithPlugin
import com.atlassian.jira.issue.fields.screen.FieldScreen
import com.atlassian.jira.issue.fields.screen.FieldScreenManager
import com.atlassian.jira.issue.customfields.option.Options
import com.atlassian.jira.issue.customfields.option.Option
import com.opensymphony.workflow.WorkflowContext
import org.apache.log4j.Category
import com.atlassian.jira.workflow.JiraWorkflow

import com.atlassian.jira.project.Project
import com.atlassian.jira.project.ProjectManager
import com.atlassian.jira.security.roles.ProjectRole
import com.atlassian.jira.security.roles.ProjectRoleActors
import com.atlassian.jira.security.roles.ProjectRoleManager

import com.atlassian.mail.Email
import com.atlassian.mail.server.MailServerManager
import com.atlassian.mail.server.SMTPMailServer
import com.atlassian.jira.issue.RendererManager

import com.atlassian.jira.event.issue.IssueEventManager
import com.atlassian.jira.event.issue.IssueEventBundleFactory
import com.atlassian.jira.event.issue.IssueEventBundle
import com.atlassian.jira.event.issue.IssueEvent

import org.apache.log4j.Logger
import org.apache.log4j.Level


def log = Logger.getLogger("com.onresolve.jira.groovy")
log.setLevel(Level.DEBUG)

//[actionId:screenId]
/* Mapping of transition and its corresponding screens */
/* Please update if the workflow changed */
actionScreenMapping = [
51:10424, 71:10536, 91:11205, 101:10548, 2081:11204, //market-end feedback
61:10537, 81: 10436, 411:11205, 421:11200, 2091:11204, //factory-end sourcing
1161:10602, 1181:11205, 1201:10600, 1221:10438, 2111:11204, //Competitor Sample Purchase
1171:10440, 1191:11205, 1211:10601, 1231:10603, 2121:11204, //Factory Sample Purchase
151:10439, 171:11205, 181:10437, 191:10604, 2131:11204, //sample purchase
201:10500, 211:10551, 221:11205, 231:11201, 2101:11204, //market-end vs factory-end evaluation
251:10504, 261:11205, 2141:11204, // Initiation Stage Wrap-Up
3121:10507, 2911:10700, 2931:10702, 2921:10705, 2951:11205, 2961:11202, 2941:11204, //Product Prototype Internal Communication
3111:10508, 3011:10701, 2981:10703, 3001:10704, 2991:12000, 2971:10800, 3021:11204, //Prototype External Communication
3101:10501, 3061:10801, 3041:11400, 3031:11203, 3051:11204, //prototype evaluation
3091:10505, 3081:11400, 3071:11204, //Prototype Stage Wrap-Up (replace Product Prototype Internal Communication + Prototype External Communication + prototype evaluation)
591:10511, 601:10802, 611:10803, 621:11205, 1441:10804, 2191:12900, //SKU-UP Initiation
1491:10512, 1521:10806, 1531:10807, 1541:11205, 1561:10808, 2201:11204, //product specs
1501:10513, 1621:10809, 1631:10810, 1641:11205, 1661:10811, 2211:11204, //mrd
1511:10805, 1571:10812, 1581:10813, 1591:11205, 1611:10814, 2221:11204, //label artworks
1671:13700, 1701:13701, 1711:13702, 1721:11205, 1741:13704, 2241:11204, //Product Instruction Manual
1681:10818, 1751:13705, 1761:10820, 1771:13706, 1791:11803, 2231:11204, //product copy
1841:10821, 1851:10822, 1861:10823, 1871:11205, 1891:10900, 2271:11204, //pictures shot planning
1691:10824, 1801:10825, 1811:10826, 1821:12700, 1961:11500, 2251:11204, //product packaging design
831:10506, 841:11205, 2261:11204, // Pre-Launch Stage Wrap-Up
851:10517, 871:10901, 881:10902, 891:11205, 2001:10903, 2291:11204, //prd
901:10510, 911:10904, 921:10905, 931:10906, 941:11205, 951:10907, 2301:11204, //pilot-run external communication
961:10502, 971:10908, 981:11600, 991:10909, 2311:11204, // pilot-run sample review
1001:10518, 1021:10910, 1031:10911, 1041:11205, 2041:10912, 2321:11204, //qc test procedure
1051:10913, 1061:11205, 2331:11204, //Pilot-Run Stage Wrap-up
1071:10503, 1081:11000, 1091:11700, 1101:11001, 2341:11204, //Initial PO Budget
1121:10519, 1131:11601, 1141:11602, 1151:11205, 2381:11603, 2391:12500, //PO Release
2401:11701, 2411:11205, 2421:11204, //Initial PO Stage Wrap-Up
2481:11900, 2491:11901, 2501:11902, 2511:11205, 2521:11903, 2531:11204, //Studio Shot Shooting
2541:11904, 2551:11905, 2561:11906, 2571:11205, 2581:11907, 2591:11204, //Additional Sketching
2601:11908, 2611:11909, 2621:11910, 2631:11205, 2641:11911, 2651:11204, //Outdoor Shot Shooting
2661:11912, 2681:11913, 2691:11914, 2701:11205, 2711:11915, 2721:11204, //Image Post-Editing
2731:11916, 2741:11917, 2761:11205, 2781:11204, // listing feed creation
2791:11920, 2801:11205, 2811:11204, //Digital Creation Stage Wrap-Up
3281:13202, 3291:13401, 3301:13400, 3311:13402, 3321:0, 3331:11204, //AMZ A+ Content
3341:13900, 3361:13901, 3371:13902, 3381:13903, 3391:0, 3401:11204, //eMail Notifications aka Product Page Optimization
3411:13102, 3421:13103, 3431:0, 3441:11205, 3451:0, 3461:11204, //Test Bench Samples
3471:13200, 3501:0, 3511:0, 3521:11205, 3531:0, 3541:11204, //AMZ ads
3481:13201, 3551:0, 3561:0, 3571:11205, 3581:0, 3591:11204, //eBay ads
3491:13501, 3601:0, 3611:0, 3621:0, 3631:0, 3641:11204, //G-Shopping Review
3651:13500, 3681:0, 3691:0, 3701:0, 3711:0, 3721:11204, //Web Meta Desc
3661:13502, 3731:13504, 3741:13503, 3751:11205, 3761:13505, 3771:11204, //eBlast Post
4001:13502, 4011:13504, 4021:11205, 4041:11204, // Product Announcement (replace eBlast Post)
3671:13100, 3781:13300, 3791:13301, 3801:13302, 3811:0, 3821:11204, //AMZ brand page
3841:13600, 3851:11205, 3861:11204, //Merchandising Stage Wrap-Up
]

/* Mapping of transition and its corresponding project roles */
/* Please update if the workflow changed */
actionProjectRoleMapping = [//market-end feedback
                            51:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            71:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            91:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Project Lead']],
                            101:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2081:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'approvePRs_condition':['Buyer'],'declinePRs':['Project Lead']],
                            //factory-end sourcing
                            61:['currentPRs':['Project Lead'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            81:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            411:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Project Lead']],
                            421:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2091:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'approvePRs_condition':['Buyer'],'declinePRs':['Project Lead']],
                            //m-sample purchase
                            1161:['currentPRs':['Buyer'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            1181:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            1202:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            1221:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2111:['currentPRs':['Project Lead'],'approvePRs':[],'approvePRs_condition':['Buyer'],'declinePRs':['Buyer']],
                            //f-sample purchase
                            1171:['currentPRs':['Buyer'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            1191:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            1211:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            1231:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2121:['currentPRs':['Project Lead'],'approvePRs':[],'approvePRs_condition':['Buyer'],'declinePRs':['Buyer']],
                            //sample purchase *** no longer used
                            151:['currentPRs':['Buyer','Merchandiser'],'nextPRs':['Project Lead']],
                            171:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer','Merchandiser']],
                            181:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            191:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2131:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer','Merchandiser']],
                            //market-end feedback vs factory-end sourcing evaluation
                            201:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            211:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            221:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Buyer']],
                            231:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2101:['currentPRs':['Project Lead'],'approvePRs':['Buyer','Merchandiser'],'declinePRs':['Buyer']],
                            //initiation stage wrap-up
                            251:['currentPRs':['Buyer','Merchandiser'],'nextPRs':['Project Lead']],
                            261:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Buyer','Merchandiser']],
                            2141:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Merchandiser','Buyer']],
                            //prototype internal communication
                            3121:['currentPRs':['Project Lead'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            2911:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2931:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2921:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2951:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Project Lead']],
                            2961:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2941:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Project Lead']],
                            //prototype external communication
                            3111:['currentPRs':['Buyer'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            3011:['currentPRs':['Project Lead'],'nextPRs':['Buyer']],
                            2981:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            3001:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2991:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer'],'declinePRs_external':['Buyer'], 'declinePRs_internal':['Project Lead','Merchandiser']],
                            2971:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            3021:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            //prototype evaluation
                            3101:['currentPRs':['Buyer'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            3061:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            3041:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Project Lead'],'declinePRs_evaluation':['Buyer'], 'declinePRs_external':['Project Lead','Buyer'], 'declinePRs_internal':['Project Lead','Merchandiser']],
                            3031:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            3051:['currentPRs':['Project Lead'],'approvePRs':['Merchandiser'],'declinePRs':['Buyer']],
                            // Prototype Stage Wrap-Up
                            3091:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],
                            3081:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs_evaluation':['Buyer'], 'declinePRs_external':['Project Lead','Buyer'], 'declinePRs_internal':['Project Lead','Merchandiser']],
                            3071:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Merchandiser']],
                            //sku-up initiation
                            591:['currentPRs':['Project Lead'],'nextPRs':['Buyer']],
                            601:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            611:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            621:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            1441:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2191:['currentPRs':['Project Lead'],'approvePRs':['Buyer','Project Lead','Graphic Designer 2'],'declinePRs':['Project Lead']],
                            //product specs
                            1491:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            1521:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            1531:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            1541:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            1561:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2201:['currentPRs':['Project Lead'],'approvePRs_condition':['Tech Support','Copywriter','Graphic Designer 1'],'declinePRs':['Buyer']],
                            //mrd
                            1501:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            1621:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            1631:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            1641:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Project Lead']],
                            1661:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2211:['currentPRs':['Project Lead'],'approvePRs_condition':['Tech Support','Copywriter','Graphic Designer 1'],'declinePRs':['Project Lead']],
                            //product packaging design
                            1691:['currentPRs':['Graphic Designer 2'],'nextPRs':['Graphic Designer 2'],'nextPRs_skip':['Project Lead']],
                            1801:['currentPRs':['Graphic Designer 2'],'nextPRs':['Graphic Designer 2']],
                            1811:['currentPRs':['Graphic Designer 2'],'nextPRs':['Buyer']],
                            1821:['currentPRs':['Buyer'],'approvePRs':['Graphic Designer 2'],'declinePRs':['Graphic Designer 2']], //TODO: Check
                            1961:['currentPRs':['Graphic Designer 2'],'nextPRs':['Project Lead']],
                            2251:['currentPRs':['Project Lead'],'approvePRs_condition':['Tech Support','Copywriter','Graphic Designer 1'],'declinePRs':['Graphic Designer 2']],
                            //Product Instruction Manual ***new update PLD-408
                            1671:['currentPRs':['Tech Support'],'nextPRs':['Copywriter'],'nextPRs_skip':['Product Manager'],'nextPRs_skip_custom':['Graphic Designer 2']],
                            1701:['currentPRs':['Copywriter'],'nextPRs':['Tech Support']],
                            1721:['currentPRs':['Tech Support'],'approvePRs':['Graphic Designer 2'],'declinePRs':['Copywriter']],
                            1711:['currentPRs':['Graphic Designer 2'],'nextPRs':['Tech Support']],
                            1741:['currentPRs':['Tech Support'],'approvePRs':['Product Manager'],'declinePRs':['Graphic Designer 2']],
                            2241:['currentPRs':['Product Manager'],'approvePRs_condition':['Merchandiser', 'Buyer'],'declinePRs':['Tech Support']],
                            //product copy
                            1681:['currentPRs':['Copywriter'],'nextPRs':['Copywriter']],
                            1751:['currentPRs':['Copywriter'],'nextPRs':['Project Lead']],
                            1761:['currentPRs':['Copywriter'],'nextPRs':['Project Lead']],//not used
                            1771:['currentPRs':['Project Lead'],'approvePRs':['Marketing Manager'],'declinePRs':['Copywriter']],
                            1791:['currentPRs':['Copywriter'],'nextPRs':['Marketing Manager']],//not used
                            2231:['currentPRs':['Marketing Manager'],'approvePRs':['Graphic Designer 3'],'approvePRs_condition':['Graphic Designer 3','Merchandiser', 'Buyer'],'declinePRs':['Copywriter']],
                            //label artworks
                            1511:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1'],'nextPRs_skip':['Buyer']],
                            1571:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1']],
                            1581:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 2']],
                            1591:['currentPRs':['Graphic Designer 2'],'approvePRs':['Graphic Designer 1'],'declinePRs':['Graphic Designer 1']],
                            1611:['currentPRs':['Graphic Designer 1'],'nextPRs':['Buyer']],
                            2221:['currentPRs':['Buyer'],'approvePRs_condition':['Merchandiser', 'Buyer'],'declinePRs':['Graphic Designer 1']],
                            //pictures shot planning
                            1841:['currentPRs':['Graphic Designer 3'],'nextPRs':['Graphic Designer 3'],'nextPRs_skip':['Project Lead']],
                            1851:['currentPRs':['Graphic Designer 3'],'nextPRs':['Graphic Designer 3']],
                            1861:['currentPRs':['Graphic Designer 3'],'nextPRs':['Product Manager']],//not used
                            1871:['currentPRs':['Product Manager'],'approvePRs':['Graphic Designer 3'],'declinePRs':['Graphic Designer 3']],
                            1891:['currentPRs':['Graphic Designer 3'],'nextPRs':['Project Lead']],
                            2271:['currentPRs':['Project Lead'],'approvePRs_condition':['Project Lead'],'declinePRs':['Graphic Designer 3']],
                            // Pre-Launch Stage Wrap-Up
                            831:['currentPRs':['Merchandiser', 'Buyer'],'nextPRs':['Project Lead']],
                            841:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Merchandiser', 'Buyer']],
                            2261:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Merchandiser', 'Buyer']],
                            //prd
                            851:['currentPRs':['Buyer'],'nextPRs':['Buyer'],'nextPRs_skip':['Project Lead']],
                            871:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            881:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            891:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            2001:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2291:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            //pilot-run external communication
                            901:['currentPRs':['Buyer'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            911:['currentPRs':['Project Lead'],'nextPRs':['Buyer']],
                            921:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            931:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            941:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            951:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2301:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            // pilot-run sample review
                            961:['currentPRs':['Buyer'],'nextPRs':['Project Lead'],'nextPRs_skip':['Project Lead']],
                            971:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            981:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs_sample':['Buyer'],'declinePRs_external':['Project Lead', 'Buyer']],
                            991:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            2311:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            //qc test procedure
                            1001:['currentPRs':['Buyer'],'nextPRs':['Buyer'],'nextPRs_skip':['Project Lead']],
                            1021:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            1031:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            1041:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            2041:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2321:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            //Pilot-Run Stage Wrap-up
                            1051:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            1061:['currentPRs':['Project Lead'],'approvePRs_condition':['Project Lead'],'declinePRs':['Buyer']],
                            2331:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            //Initial PO Budget
                            1071:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            1081:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']],
                            1091:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']], //TODO: check
                            1101:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2341:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            //PO Release
                            1121:['currentPRs':['Buyer'],'nextPRs':['Buyer'],'nextPRs_skip':['Project Lead']],
                            1131:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            1141:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            1151:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            2381:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2391:['currentPRs':['Project Lead'],'approvePRs':['Buyer'],'declinePRs':['Buyer']],
                            //Initial PO Stage Wrap-Up
                            2401:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            2411:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Buyer']],
                            2421:['currentPRs':['Project Lead'],'approvePRs':['Photographer', 'Photographer', 'Graphic Designer 1'],'declinePRs':['Buyer']],
                            //Studio Shot Shooting
                            2481:['currentPRs':['Photographer'],'nextPRs':['Photographer']],
                            2491:['currentPRs':['Photographer'],'nextPRs':['Photographer']],
                            2501:['currentPRs':['Photographer'],'nextPRs':['Graphic Designer 3']],
                            2511:['currentPRs':['Graphic Designer 3'],'approvePRs':['Photographer'],'declinePRs':['Photographer']],
                            2521:['currentPRs':['Photographer'],'nextPRs':['Marketing Manager']],
                            2531:['currentPRs':['Marketing Manager'],'approvePRs_condition':['Graphic Designer 3'],'declinePRs':['Photographer']],
                            //Additional Sketching
                            2541:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1'],'nextPRs_skip':['Graphic Designer 3']],
                            2551:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1']],
                            2561:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 2']],
                            2571:['currentPRs':['Graphic Designer 2'],'approvePRs':['Graphic Designer 1'],'declinePRs':['Graphic Designer 1']],
                            2581:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 3']],
                            2591:['currentPRs':['Graphic Designer 3'],'approvePRs_condition':['Graphic Designer 3'],'declinePRs':['Graphic Designer 1']],
                            //Outdoor Shot Shooting
                            2601:['currentPRs':['Photographer'],'nextPRs':['Photographer'],'nextPRs_skip':['Graphic Designer 3']],
                            2611:['currentPRs':['Photographer'],'nextPRs':['Photographer']],
                            2621:['currentPRs':['Photographer'],'nextPRs':['Graphic Designer 3']],
                            2631:['currentPRs':['Graphic Designer 3'],'approvePRs':['Photographer'],'declinePRs':['Photographer']],
                            2641:['currentPRs':['Photographer'],'nextPRs':['Graphic Designer 3']],
                            2651:['currentPRs':['Graphic Designer 3'],'approvePRs_condition':['Graphic Designer 3'],'declinePRs':['Photographer']],
                            //Image Post-Editing
                            2661:['currentPRs':['Graphic Designer 3'],'nextPRs':['Graphic Designer 3']],
                            2681:['currentPRs':['Graphic Designer 3'],'nextPRs':['Graphic Designer 3']],
                            2691:['currentPRs':['Graphic Designer 3'],'nextPRs':['Marketing Manager']],
                            2701:['currentPRs':['Marketing Manager'],'approvePRs':['Graphic Designer 3'],'declinePRs':['Graphic Designer 3']],
                            2711:['currentPRs':['Graphic Designer 3'],'nextPRs':['Marketing Manager']],
                            2721:['currentPRs':['Marketing Manager'],'approvePRs':['Marketing Manager'],'declinePRs':['Graphic Designer 3']],
                            // listing feed creation
                            2731:['currentPRs':['Merchandiser'],'nextPRs':['Merchandiser']],
                            2741:['currentPRs':['Merchandiser'],'nextPRs':['Product Manager']],
                            2761:['currentPRs':['Product Manager'],'approvePRs':['Marketing Manager'],'declinePRs':['Merchandiser']],
                            2781:['currentPRs':['Marketing Manager'],'approvePRs':['Merchandiser'],'declinePRs':['Merchandiser']],//not used
                            //Digital Creation Stage Wrap-Up
                            2791:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],
                            2801:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Merchandiser']],
                            2811:['currentPRs':['Project Lead'],'approvePRs':['Merchandiser', 'Merchandiser', 'Buyer'],'declinePRs':['Merchandiser']],
                            //amz brand page
                            3281:['currentPRs':['Merchandiser'],'nextPRs':['Graphic Designer 3'],'nextPRs_skip':['Project Lead']], 
                            3291:['currentPRs':['Graphic Designer 3'],'nextPRs':['Graphic Designer 3']], 
                            3301:['currentPRs':['Graphic Designer 3'],'nextPRs':['Merchandiser']],
                            3311:['currentPRs':['Merchandiser'],'approvePRs':['Project Lead'],'declinePRs':['Graphic Designer 3']],
                            3321:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']], //not used
                            3331:['currentPRs':['Project Lead'],'approvePRs_condition':['Merchandiser', 'Merchandiser', 'Merchandiser'],'declinePRs':['Graphic Designer 3']],
                            //eMail notifications
                            3341:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']], 
                            3361:['currentPRs':['Merchandiser'],'nextPRs':['Merchandiser']],//not used
                            3371:['currentPRs':['Merchandiser'],'nextPRs':['Merchandiser']],//not used
                            3381:['currentPRs':['Merchandiser'],'approvePRs':['Merchandiser'],'declinePRs':['Merchandiser']],//not used
                            3391:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],//not used
                            3401:['currentPRs':['Project Lead'],'approvePRs_condition':['Merchandiser', 'Merchandiser', 'Merchandiser'],'declinePRs':['Merchandiser']],
                            //test bench samples 
                            3411:['currentPRs':['Buyer'],'nextPRs':['Buyer']],
                            3421:['currentPRs':['Buyer'],'nextPRs':['Project Lead']],
                            3431:['currentPRs':['Buyer'],'nextPRs':['Project Lead']], //not used
                            3441:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Buyer']],
                            3451:['currentPRs':['Buyer'],'nextPRs':['Project Lead']], //not used
                            3461:['currentPRs':['Project Lead'],'approvePRs_condition':['Merchandiser', 'Merchandiser', 'Merchandiser'],'declinePRs':['Buyer']],
                            //amz ads
                            3471:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']], 
                            3501:['currentPRs':['Merchandiser'],'nextPRs':['Merchandiser']],//not used
                            3511:['currentPRs':['Merchandiser'],'nextPRs':['Merchandiser']],//not used
                            3521:['currentPRs':['Merchandiser'],'approvePRs':['Merchandiser'],'declinePRs':['Merchandiser']],//not used
                            3531:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],//not used
                            3541:['currentPRs':['Project Lead'],'approvePRs_condition':['Project Lead', 'Merchandiser', 'Merchandiser'],'declinePRs':['Merchandiser']],
                            //ebay ads
                            3481:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']], 
                            3551:['currentPRs':['Merchandiser'],'nextPRs':['Merchandiser']],//not used
                            3561:['currentPRs':['Merchandiser'],'nextPRs':['Merchandiser']],//not used
                            3571:['currentPRs':['Merchandiser'],'approvePRs':['Merchandiser'],'declinePRs':['Merchandiser']],//not used
                            3581:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],//not used
                            3591:['currentPRs':['Project Lead'],'approvePRs_condition':['Project Lead', 'Merchandiser', 'Merchandiser'],'declinePRs':['Merchandiser']],
                            //g-shopping review
                            3491:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']], 
                            3601:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1']],//not used
                            3611:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 3']],//not used
                            3621:['currentPRs':['Graphic Designer 3'],'approvePRs':['Marketing Manager'],'declinePRs':['Graphic Designer 1']],//not used
                            3631:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],//not used
                            3641:['currentPRs':['Project Lead'],'approvePRs_condition':['Project Lead', 'Merchandiser', 'Merchandiser'],'declinePRs':['Merchandiser']],
                            //web meta desc
                            3651:['currentPRs':['Project Lead'],'nextPRs':['Project Lead']], 
                            3681:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1']],//not used
                            3691:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 3']],//not used
                            3701:['currentPRs':['Graphic Designer 3'],'approvePRs':['Marketing Manager'],'declinePRs':['Graphic Designer 1']],//not used
                            3711:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],//not used
                            3721:['currentPRs':['Project Lead'],'approvePRs_condition':['Merchandiser'],'declinePRs':['Project Lead']],
                            //amz a+ content
                            3671:['currentPRs':['Merchandiser'],'nextPRs':['Graphic Designer 1'],'nextPRs_skip':['Merchandiser']], 
                            3781:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1']],
                            3791:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 3']],
                            3801:['currentPRs':['Graphic Designer 3'],'approvePRs':['Merchandiser'],'declinePRs':['Graphic Designer 1']],
                            3811:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],//not used
                            3821:['currentPRs':['Merchandiser'],'approvePRs_condition':['Merchandiser'],'declinePRs':['Graphic Designer 1']],
                            //eblast post -> rename to Product Announcement
                            3661:['currentPRs':['Merchandiser'],'nextPRs':['Graphic Designer 1'],'nextPRs_skip':['Merchandiser']], 
                            3731:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 1']],
                            3741:['currentPRs':['Graphic Designer 1'],'nextPRs':['Graphic Designer 3']],
                            3751:['currentPRs':['Graphic Designer 3'],'approvePRs':['Graphic Designer 3'],'declinePRs':['Graphic Designer 1']],
                            3761:['currentPRs':['Graphic Designer 3'],'nextPRs':['Merchandiser']],
                            3771:['currentPRs':['Merchandiser'],'approvePRs_condition':['Merchandiser'],'declinePRs':['Graphic Designer 3']],
                            //Product Announcement
                            4001:['currentPRs':['Merchandiser'],'nextPRs':['Graphic Designer 1'],'nextPRs_skip':['Product Manager']], 
                            4011:['currentPRs':['Graphic Designer 1'],'nextPRs':['Merchandiser']],
                            4021:['currentPRs':['Merchandiser'],'approvePRs':['Product Manager'],'declinePRs':['Graphic Designer 1']],
                            4041:['currentPRs':['Product Manager'],'approvePRs_condition':['Product Manager'],'declinePRs':['Merchandiser']],
                            //Merchandising Stage Wrap-Up
                            3841:['currentPRs':['Merchandiser'],'nextPRs':['Project Lead']],
                            3851:['currentPRs':['Project Lead'],'approvePRs':['Project Lead'],'declinePRs':['Merchandiser']],
                            3861:['currentPRs':['Project Lead'],'approvePRs':[],'declinePRs':['Merchandiser']],
]


/* DEBUG ONLY */
debugActionProjectRoleMapping = [
                                    2451:['Tech Support','Copywriter','Graphic Designer 1'],// product copy
                                    2461:['Merchandiser'],//Market-end Feedback
                                    2471:['Buyer','Product Manager','Graphic Designer 1'],//MRD
                                    2821:['Buyer'],//Initial PO Stage Wrap-Up
                                    2831:['Buyer'],//PO Release
                                    2841:['Buyer'],//Initial PO Budget
                                    2851:['Buyer'],//Pilot-Run Stage Wrap-up
                                    2861:['Buyer'],//QC Test Procedure
                                    2871:['Buyer'],//Pilot-Run Sample Review
                                    2881:['Buyer'],//Pilot-Run External Communication
                                    2891:['Buyer'],//PRD
                                    2901:['Merchandiser','Buyer'],//Pre-Launch Stage Wrap-Up
                                    3141:['Buyer'],//Prototype External Communication
                                    3151:['Buyer'],//Product Prototype Evaluation
                                    3161:['Merchandiser'],//Prototype Stage Wrap-Up
                                    3171:['Graphic Designer 1', 'Photographer', 'Photographer'],//Additional Sketching
                                    3181:['Graphic Designer 1', 'Photographer', 'Photographer'],//Outdoor Shot Shooting
                                    3191:['Graphic Designer 1', 'Photographer', 'Photographer'],//Studio Shot Shooting
                                    3201:['Graphic Designer 3'],//Image Post-Editing
                                    3211:['Merchandiser'],//Listing Feed Creation
                                    3221:['Merchandiser'],//Digital Creation Stage Wrap-Up
                                    3261:['Product Manager'],//SKU-UP Initiation
                                    3131:['Product Manager'],//Product Prototype Internal Communication
                                    3911:['Merchandiser', 'Merchandiser', 'Buyer'],//AMZ A+ Content
                                    3871:['Merchandiser', 'Merchandiser', 'Buyer'],//AMZ Brand Page
                                    3881:['Merchandiser', 'Merchandiser', 'Merchandiser'],//Google Shopping Ads
                                    3891:['Product Manager', 'Merchandiser', 'Merchandiser'],//Web Meta Desc
                                    3901:['Merchandiser', 'Merchandiser'],//eBlast Post
                                    4051:['Merchandiser', 'Merchandiser']//Product Announcement
                                ]

//store Prototype Decline Stage
prototypeDeclineStage = ''
//conditionPassed used for 'Product Data Compliation' and 'Product Marketing Material Creation' and 'Product Pictures Shooting'
conditionPassed = false
//skipped used for 'SKIP'
skipped = false
//skipped used for 'Manual Creation SKIP'
skipped_custom = false

actionId = transientVars.get("actionId")
screenId = actionScreenMapping.get(actionId)

/* SET STAGE/STATION/STEP */
def workflowManager = ComponentAccessor.getWorkflowManager()
JiraWorkflow workflow = workflowManager.getWorkflow(issue)
def wfd = workflow.getDescriptor()
def actionName = wfd.getAction(actionId).getName()
log.warn "Action name " + actionName

stagesMapping = [
        "Initiation Stage" : ['Market Feedback', 'Factory Sourcing', 'M-Sample Purchase', 'F-Sample Purchase','M vs. F Eval', 'Initiation Wrap-Up', 'Initiation Stage Wrap-up'],
        "Prototype Stage" : ['P-TYPE Int. Meet', 'P-TYPE Ext. Meet', 'P-TYPE Eval','P-TYPE Wrap-Up', 'Prototype Stage Wrap-up'],
        "Pre-launch Stage" : ['SKU Initiation', 'Product Spec', 'MRD', 'Label Artwork', 'Manual Creation','Picture Shot Plan', 'Package Creation', 'Copy Creation', 'Pre-Launch Wrap-Up'],
        "Pilot-run Stage" : ['PRD','P-Run Ext. Meet','P-Run Sample Review','Test Procedure','Pilot-Run Wrap-up'],
        "Initial PO Stage" : ['Initial PO Budget','PO Release','Initial PO Wrap-Up'],
        "Digital Creation Stage" : ['Sketching', 'Studio Shot', 'Outdoor Shot', 'Post Editing', 'Feed Creation', 'Digital Wrap-Up'],
        "Merchandising Stage": ['AMZ Brand Page', 'Page Optimization', 'Test Bench', 'AMZ Ads', 'eBay Ads', 'AMZ A+ Content', 'Merchandising Wrap-up']
]

def prefixKeywords = ["Information Gathering", "Information Analysis", "Closed", "Documentation", "Approval Review", "Meeting Follow-up", "Actual Meeting", "Meeting Arrangement", "Check List Verification", "Task Processing", "Task Review"]
def environment = Eval.me(issue.environment)

for (prefixKeyword in prefixKeywords) {
    if (actionName.contains(prefixKeyword)) {
        environment.currentStep = prefixKeyword
        actionName -= prefixKeyword
        actionName = actionName.substring(0, actionName.length() - 1) //remove last character
        environment.currentStation = actionName
        environment.currentStage = getStageFromActionName(actionName)
    }
}

/* SET PROJECT ROLE */
def rolesToAdd = []
def rolesToRemove = []

if (screenId == null && (debugActionProjectRoleMapping.keySet().contains(actionId))) { //debug transition
    rolesToRemove += environment.currentProjectRoles
    rolesToAdd += debugActionProjectRoleMapping.get(actionId)
    switch (actionId) {
        case 2451:
            if (environment.stages."Product Instruction Manual" == "Closed") { rolesToAdd.remove("Copywriter")}
            if (environment.stages."Product Packaging Design" == "Closed") { rolesToAdd.remove("Graphic Designer 2")}
            break;
        case 2471:
            if (environment.stages."Product Specs" == "Closed") { rolesToAdd.remove("Buyer")}
            if (environment.stages."Label Artworks" == "Closed") { rolesToAdd.remove("Graphic Designer 1")}
            break;
    }
} else {
    def customFields = getCustomFieldsOnScreen(screenId)
    def isValidFields = true
    for (customField in customFields) {
        isValidFields &= validateCustomFields(customField)
    }
    log.warn "IS VALID FIELD " + isValidFields

    if (isApprovalAction(screenId)) {
        log.warn "Approval action"
        def isApproved = validateCustomFields(customFields.find{ it.getName().contains("Approval Option") })
        if (isValidFields) {
            rolesToRemove += getPRsFromMapping(actionId, 'currentPRs')
            rolesToAdd += getPRsFromMapping(actionId, conditionPassed ? 'approvePRs_condition' : 'approvePRs')
        } else {
            if (isApproved == false) {
                rolesToRemove += getPRsFromMapping(actionId, 'currentPRs')
                def key = 'declinePRs'
                if (prototypeDeclineStage) {
                    key += '_' + prototypeDeclineStage
                }
                rolesToAdd += getPRsFromMapping(actionId, key)
            }
        }
    } else if (isCloseAction(screenId)) {
        log.warn "Close action"
        rolesToRemove += getPRsFromMapping(actionId, 'currentPRs')
        if (isValidFields) {
            rolesToAdd += getPRsFromMapping(actionId, conditionPassed ? 'approvePRs_condition' : 'approvePRs')
        } else {
            rolesToAdd += getPRsFromMapping(actionId, 'declinePRs')
        }
    } else {
        log.warn "Normal action"
        if (skipped_custom) {
            rolesToRemove += getPRsFromMapping(actionId, 'currentPRs')
            rolesToAdd += getPRsFromMapping(actionId, 'nextPRs_skip_custom')
            
            //add comment if available
            if(transientVars?.comment) {
                transientVars.comment = String.format("%s - %s", actionName, transientVars.comment)
            }
        } else if (skipped) {
            rolesToRemove += getPRsFromMapping(actionId, 'currentPRs')
            rolesToAdd += getPRsFromMapping(actionId, 'nextPRs_skip')
            
            //add comment if available
            if(transientVars?.comment) {
                transientVars.comment = String.format("%s - %s", actionName, transientVars.comment)
            }
        } else if (isValidFields) {
            rolesToRemove += getPRsFromMapping(actionId, 'currentPRs')
            rolesToAdd += getPRsFromMapping(actionId, 'nextPRs')

            //add comment if available
            if(transientVars?.comment) {
                transientVars.comment = String.format("%s - %s", actionName, transientVars.comment)
            }
        } else {
            //remove comment if fields is invalid
            if(transientVars?.comment) {
                transientVars.comment = null
            }
        }
    }
}

log.warn "ADD " + rolesToAdd
log.warn "REMOVE " + rolesToRemove
for (roleToRemove in rolesToRemove) {
    //if (environment.currentProjectRoles.contains(roleToRemove)) {
    environment.currentProjectRoles.remove(roleToRemove)
    //}
}

for (roleToAdd in rolesToAdd) {
    //if (!environment.currentProjectRoles.contains(roleToAdd)) {
    environment.currentProjectRoles.add(roleToAdd)
    //}
}
issue.environment = environment.inspect()

/* SEND EMAILS */
def issueEventMappings = [
        "Product Manager":10102,
        "Merchandiser":10101,
        "Buyer":10100,
        "Copywriter": 10103,
        "Graphic Designer 2":10108,
        "Graphic Designer 1":10600,
        "Graphic Designer 3":10105,
        "Photographer":10109,
        "Tech Support":10104,
        "Instruction Writer":10107,
        "Marketing Manager":10106,
        "Project Participant":10106
]


ProjectRoleManager projectRoleManager = ComponentAccessor.getComponent(ProjectRoleManager)
def rolesToAddUnique = rolesToAdd.unique(false)
log.warn "Send email to " + rolesToAddUnique
for (currentProjectRole in rolesToAddUnique) {
    def eventId = issueEventMappings.get(currentProjectRole)
    IssueEventManager issueEventManager = ComponentAccessor.getIssueEventManager()
    IssueEventBundleFactory issueEventFactory = (IssueEventBundleFactory) ComponentAccessor.getComponent(IssueEventBundleFactory)
    IssueEventBundle eventBundle = issueEventFactory.wrapInBundle(new IssueEvent (issue, null, ComponentAccessor.getJiraAuthenticationContext().getLoggedInUser(), eventId, true))
    issueEventManager.dispatchEvent(eventBundle)
    log.warn "Dispatch Event to " + currentProjectRole + " ID: " + eventId
}

/* PRIVATE METHODS */

def getStageFromActionName(actionName) {
    for (stage in stagesMapping.keySet()) {
        def actions = stagesMapping.get(stage)
        if (actions.contains(actionName)) {
            return stage
        }
    }
}

def getPRsFromMapping(actionId,key) {
    log.warn "KEY " + key
    def PRs = actionProjectRoleMapping.get(actionId).get(key)
    if (PRs == null) {
        return []
    }
    return PRs
}

def isApprovalAction(screenId) {
    def approvalScreenIds = [11205,11700,11400,11600,12000,12700,13302,13402,13704,13706,13903]
    return approvalScreenIds.contains(screenId)
}

def isCloseAction(screenId) {
    return screenId == 11204 || screenId == 12500 || screenId == 12900
}

def getCustomFieldsOnScreen(screenId) {
    def fieldScreenManager = ComponentAccessor.getComponent(FieldScreenManager)
    def customFieldManager = ComponentAccessor.getCustomFieldManager()
    def customFields = []
    def fieldScreen = fieldScreenManager.getFieldScreen(screenId)
    def fieldScreenTabs = fieldScreen.getTabs()
    for (fieldScreenTab in fieldScreenTabs) {
        for (fieldScreenLayoutItem in fieldScreenTab.getFieldScreenLayoutItems()) {
            def customField = customFieldManager.getCustomFieldObject(fieldScreenLayoutItem.getFieldId())
            if (customField != null) {
                customFields.add(customField)
            }
        }
    }
    return customFields
}

def validateCustomFields(customField) {
    if (customField == null) {
        return false
    }
    //CustomField 'Manual Creation Information Gathering SKIP'
    if (customField.getId().contains("15110")) {
        String skipValue = issue.getCustomFieldValue(customField)
        skipped_custom = skipValue != null
        return true
    }

    //CustomField 'SKIP this step completely!'
    if (customField.getId().contains("11507")) {
        String skipValue = issue.getCustomFieldValue(customField)
        skipped = skipValue != null
        return true
    }

    switch (customField.getCustomFieldType().getName()) {
        case "Checkboxes":
            def result = validateCheckboxes(customField)
            log.warn "Validate checkboxes " + result
            return result
            break
        case "Checklist":
            def result = validateChecklist(customField)
            log.warn "Validate checklist " + result
            return result
            break
        case "Select List (single choice)":
            def result = validateSelectList(customField)
            log.warn "Validate Select List " + result
            return result
        default:
            if (customField.getId().contains("10814") || customField.getId().contains("10815") || customField.getId().contains("11814")) {
                return true
            }
            return issue.getCustomFieldValue(customField) != null
            break
    }
    return false
}

//2 kinds of select list:
//- APPROVAL OPTION
//- FALSE if select option contains "Decline", otherwise TRUE
//- CLOSE
//- TRUE if select option contains "Close"
def validateSelectList(customField) {
    String selectListItem = issue.getCustomFieldValue(customField)
    log.warn "SELECTLIST VALUE " + selectListItem
    if (selectListItem == null) {
        return false
    }

    if (customField.getId().contains("11508")) { //CLOSE
        //market-end feedback vs factory-end sourcing
        // if (actionId == 2081) {
        //     def environment = Eval.me(issue.environment)
        //     conditionPassed = (environment.stages."Factory-end Sourcing" == null && environment.stages."Competitor Sample Purchase" == null) || (environment.stages."Factory-end Sourcing" == "Closed" && environment.stages."Market-end Feedback" == "Closed" && environment.stages."Competitor Sample Purchase" == null && environment.stages."Factory Sample Purchase" == null)
        // }
        // if (actionId == 2091) {
        //     def environment = Eval.me(issue.environment)
        //     conditionPassed = (environment.stages."Market-end Feedback" == null && environment.stages."Factory Sample Purchase" == null) || (environment.stages."Factory-end Sourcing" == "Closed" && environment.stages."Market-end Feedback" == "Closed" && environment.stages."Competitor Sample Purchase" == null && environment.stages."Factory Sample Purchase" == null)
        // }

        if (actionId == 2111 || actionId == 2121) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."Competitor Sample Purchase" == "Closed" && environment.stages."Factory Sample Purchase" == "Closed"
        }

        //product data compliation
        if (actionId == 2201 || actionId == 2211 || actionId == 2251) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."Product Specs" == "Closed" && environment.stages."MRD" == "Closed" && environment.stages."Product Packaging Design" == "Closed"
        }

        //product marketing material creation
        if (actionId == 2231 || actionId == 2241 || actionId == 2221) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."Product Copy" == "Closed" && environment.stages."Product Instruction Manual" == "Closed" && environment.stages."Label Artworks" == "Closed"
        }

        //product pictures shooting
        if (actionId == 2531 || actionId == 2591 ) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."Studio Shot Shooting" == "Closed" && environment.stages."Additional Sketching" == "Closed" && environment.stages."Outdoor Shot Shooting" != "Closed"
        }
        if (actionId == 2651) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."Studio Shot Shooting" != "Closed" && environment.stages."Additional Sketching" != "Closed" && environment.stages."Outdoor Shot Shooting" == "Closed"
        }

        //Pilot-Run Stage Wrap-up
        if (actionId == 2331) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."Picture Shots Planning" == "Closed"
        }

        //pictures shot planning
        if (actionId == 2271) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."Pilot-Run Stage Wrap-up" == "Closed"
            // conditionPassed = environment.stages."Pilot-Run Stage Wrap-up" == "Approval Review"
        }

        //merchandising stage milestone 1
        if (actionId == 3331 || actionId == 3401 || actionId == 3461) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."AMZ A+ Content" == "Closed" && environment.stages."Product Page Optimization" == "Closed" && environment.stages."Test Bench Samples" == "Closed"
        }

        //merchandising stage milestone 2
        if (actionId == 3541 || actionId == 3591 || actionId == 3641) {
            def environment = Eval.me(issue.environment)
            conditionPassed = environment.stages."AMZ Ads" == "Closed" && environment.stages."eBay Ads" == "Closed" && environment.stages."Google Shopping Performance" == "Closed"
        }

        //merchandising stage milestone 3
        // if (actionId == 3721 || actionId == 3771 || actionId == 3821) {
        //     def environment = Eval.me(issue.environment)
        //     //conditionPassed = environment.stages."Web Meta Desc" == "Closed" && environment.stages."eBlast Post" == "Closed" && environment.stages."AMZ A+ Content" == "Closed"
        //     conditionPassed = environment.stages."eBlast Post" == "Closed" && environment.stages."AMZ A+ Content" == "Closed"
        // }

        if (actionId == 3721 || actionId == 3771 || actionId == 3821 || actionId == 4041) {
            def environment = Eval.me(issue.environment)
            //conditionPassed = environment.stages."Web Meta Desc" == "Closed" && environment.stages."eBlast Post" == "Closed" && environment.stages."AMZ A+ Content" == "Closed"
            conditionPassed = environment.stages."Product Announcement" == "Closed" && environment.stages."AMZ Brand Page" == "Closed"
        }

        return selectListItem == "Close"
    } else { //APPROVAL REVIEW
        if (actionId == 2991 || actionId == 3041 || actionId == 3081 || actionId == 981) {
            if (selectListItem.contains("Internal")) {
                prototypeDeclineStage = 'internal'
            } else if (selectListItem.contains("External")) {
                prototypeDeclineStage = 'external'
            } else if (selectListItem.contains("Evaluation")) {
                prototypeDeclineStage = 'evaluation'
            } else if (selectListItem.contains("Sample")) {
                prototypeDeclineStage = 'sample'
            }
        }

        return !selectListItem.contains("Decline")
    }

    def defaultOptions = []
    ComponentAccessor.getOptionsManager().getOptions(customField.getConfigurationSchemes().listIterator().next().getOneAndOnlyConfig()).each { 
        if (it.getDisabled() == false) { defaultOptions.add(it.toString()) }
    }
    for (option in defaultOptions) {
        log.warn "Option " + option
    }

    return false
}

def validateCheckboxes(customField) {
    def checkboxItems = []
    issue.getCustomFieldValue(customField).each { checkboxItems.add(it.toString())}
    log.warn "CHECKBOX VALUE " + checkboxItems
    if (checkboxItems.size() == 0) {
        return false
    }

    def defaultOptions = []
    ComponentAccessor.getOptionsManager().getOptions(customField.getConfigurationSchemes().listIterator().next().getOneAndOnlyConfig()).each { 
        if (it.getDisabled() == false) { defaultOptions.add(it.toString()) }
    }
    for (option in defaultOptions) {
        log.warn "Option " + option
    }

    return checkboxItems.intersect(defaultOptions).size() == defaultOptions.size()
}

def validateChecklist(customField) {
    def checklistActionItems = issue.getCustomFieldValue(customField)
    log.warn "CHECKLIST VALUE " + checklistActionItems
    if (customField.getId().contains("10813") && actionId == 3061 && checklistActionItems == null) {
        log.warn "EDGE CASEs : Prototype Evaluation Information Analysis"
        return true
    }
    if (customField.getId().contains("11819") && actionId == 971 && checklistActionItems == null) {
        log.warn "EDGE CASEs : Pilot-Run Sample Review Information Analysis"
        return true
    }

    if (customField.getId().contains("11821") && actionId == 991) {
        log.warn "EDGE CASEs : Pilot-run sample review"
        return true
    }

    if (customField.getId().contains("11202") && actionId == 1861) {
        log.warn "EDGE CASEs : Picture Shots Planning Task Review"
        return true
    }
    
    // if ((customField.getId().contains("14702") && actionId == 3661)) {
    //     log.warn "LAUNCH EBLAST POST"
    //     return checklistActionItems != null
    // }
    
    if ((customField.getId().contains("14702") && actionId == 4001) || (customField.getId().contains("14702") && actionId == 4011)) {
        log.warn "EDGE CASEs : PRODUCT ANNOUNCEMENT"
        return true
    }

    if ((customField.getId().contains("14600") && actionId == 3281)) {
        log.warn "AMZ A+ CONTENT"
        return checklistActionItems != null
    }

    if ((customField.getId().contains("14500") && actionId == 3671)) {
        log.warn "AMZ BRAND PAGE"
        return checklistActionItems != null
    }

    if ((customField.getId().contains("12400") && actionId == 3121) || (customField.getId().contains("12401") && actionId == 3111) || (customField.getId().contains("12401") && actionId == 3011) || (customField.getId().contains("12600") && actionId == 901) || (customField.getId().contains("12600") && actionId == 911) || (customField.getId().contains("10807") && actionId == 2981) || (customField.getId().contains("10802") && actionId == 2931) || (customField.getId().contains("11816") && actionId == 921) || (customField.getId().contains("10813") && actionId == 2971) || ((customField.getId().contains("11819") || (customField.getId().contains("11820"))) && actionId == 951)) {
        log.warn "Communication EDGE CASEs"
        return checklistActionItems != null
    }

    // Product copy processing edge case
    // If checklist doesn't have items, then skip validating
    // If checklist has items, then proceed to validate
    if (customField.getId().contains("11104") && actionId == 1751 && checklistActionItems == null) {
        log.warn "Copy creation EDGE CASEs"
        return true
    }

    log.warn "IS READY " + isReady(checklistActionItems)
    if ( isReady(checklistActionItems) == "Fully-Ready" ) {
        return true
    }

    return false
}

def isReady(checklist) {
    if (checklist == null || checklist.size() == 0) {
        return "Checklist is null"
    }

    def uncheckedExists = false
    def uncheckedRequiredExists = false

    for (checklistCondition in checklist) {
        //def checklistItem = ((ChecklistItem) checklistCondition)
        def checklistItem = checklistCondition
        if (!checklistItem.isChecked()) {
            uncheckedExists = true
            if (checklistItem.isMandatory()) {
                uncheckedRequiredExists = true
                break
            }
        }
    }

    if (uncheckedRequiredExists) {
        return "Not-Ready"
    } else if (uncheckedExists) {
        return "Required-Ready"
    } else {
        return "Fully-Ready"
    }
}