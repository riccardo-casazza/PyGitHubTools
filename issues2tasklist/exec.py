from github import Github
import argparse


def get_tasklist_by_state(issue_state, included_labels, excluded_labels, repo):
    issues = source_repo.get_issues(state=issue_state, labels=included_labels)
    tasklist = '''```[tasklist]
### Task List ('''+issue_state+''')'''
    for issue in issues:
        if included_labels not in issue.labels and not issue.pull_request:
            tasklist = tasklist + "\n- [ ] " + issue.html_url
    tasklist = tasklist + "\n```"
    return tasklist


def update_tasklist_comment(separator, repo, issue_id, tasklists):
    issue = repo.get_issue(issue_id)
    old_body = issue.body
    fixed_part = old_body.split(separator)[0]

    issue.edit(body=fixed_part + separator + "\n" + tasklists)

parser = argparse.ArgumentParser(
    description='Script to get a list of tasks from repository <source_repo> filtered by <included_labels> and <excluded_labels> and put the tasklist result in the issue <issue_id> in <destination_repo> ')
parser.add_argument('--source_repo', type=str, required=True,
                    help='Source repository containing tasks')
parser.add_argument('--included_labels', type=str, required=True, nargs='+',
                    help='a list of labels to include in the task list')
parser.add_argument('--excluded_labels', type=str, required=True, nargs='+',
                    help='a list of labels to exclude from the task list')
parser.add_argument('--issue_id', type=int, required=True,
                    help='The issue where the tasklist will be written to')
parser.add_argument('--destination_repo', type=str, required=True,
                    help='The repository containing issue_id')
parser.add_argument('--github_access_token', type=str, required=True,
                    help='Your github access token')

args = parser.parse_args()
source_repo_name = args.source_repo
included_labels = args.included_labels
excluded_labels = args.excluded_labels
destination_repo_name = args.destination_repo

g = Github(args.github_access_token)
source_repo = g.get_repo(source_repo_name)
destination_repo = g.get_repo(destination_repo_name)

tasklists = get_tasklist_by_state(
    "open", included_labels, excluded_labels, source_repo)
tasklists = tasklists + "\n\n"
tasklists = tasklists + \
    get_tasklist_by_state("closed", included_labels,
                          excluded_labels, source_repo)

update_tasklist_comment(
    "---------------------------------------", destination_repo, args.issue_id, tasklists)
