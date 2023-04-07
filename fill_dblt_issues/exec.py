import os
from github import Github
from github import Label
import argparse


def update_tasklist_comment(separator, repo, issue_id, open_task_list, closed_task_list):
    issue = repo.get_issue(issue_id)
    old_body = "" if issue.body == None else issue.body
    parts = old_body.split(separator)
    fixed_part = ""
    if len(parts) > 1:
        fixed_part = parts[0]

    issue.edit(body=fixed_part + separator + "\n" +
               open_task_list + "\n" + closed_task_list)


def get_tasklist_by_state(issue_state, included_labels, excluded_labels, repo):
    issues = repo.get_issues(state=issue_state, labels=included_labels)
    some_items = False
    tasklist = '''```[tasklist]
### Task List ('''+issue_state+''')'''
    for issue in issues:
        issue_labels = list(map(lambda x: x.name, issue.labels))
        if all(list(map(lambda x: x not in issue_labels, excluded_labels))) and not issue.pull_request:
            print("---"+str(issue.number) + " - " + issue.title)
            some_items = True
            tasklist = tasklist + "\n- [ ] " + issue.html_url
    tasklist = tasklist + "\n```"
    tasklist = tasklist if some_items else ""
    return tasklist


parser = argparse.ArgumentParser(
    description='')
parser.add_argument('--source_repos', type=str, required=True, nargs='+',
                    help='Source repository containing DBLT tasks')
parser.add_argument('--github_access_token', type=str, required=True,
                    help='Your github access token')

args = parser.parse_args()

g = Github(args.github_access_token)
repo_names = args.source_repos


for repo_name in repo_names:
    print("Repo " + repo_name)
    repo = g.get_repo(repo_name)
    dblt_issues = repo.get_issues(labels=["DBLT"])

    for dblt_issue in dblt_issues:
        print("-DBLT issue " + dblt_issue.title +
              " ("+str(dblt_issue.number)+")")
        labels = list(filter(lambda lab: lab.name !=
                      "DBLT", dblt_issue.labels))
        print("--Open issues")
        open_issues = get_tasklist_by_state("open", labels, ["DBLT"], repo)
        print("--Closed issues")
        closed_issues = get_tasklist_by_state("closed", labels, ["DBLT"], repo)

        update_tasklist_comment("---------------------------------------",
                                repo, dblt_issue.number, open_issues, closed_issues)
