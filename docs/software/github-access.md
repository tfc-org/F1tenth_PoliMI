# GitHub access and branch rules

*Snapshot of the `tfc-org` settings, read on 21 October 2026. GitHub is the source of truth: if this page and GitHub disagree, GitHub wins and this page needs an update.*

This page says who can read, push, review and merge in our three repos, and how the rulesets protect the shared branches.

## Repos

| Repo | What | Default branch | Upstream |
|---|---|---|---|
| `F1tenth_PoliMI` | This repo: docs, Docker, our packages | `main` | none |
| `f1tenth_system` | Drivers, our fork (submodule in `ros2_ws/src/`) | `humble-polimi` | `f1tenth/f1tenth_system` |
| `f1tenth_gym_ros` | Simulator, our fork | `dev-humble-polimi` | `f1tenth/f1tenth_gym_ros` |

The org is on the **Free** plan. Org-level rulesets need GitHub Team, so each repo has its own ruleset.

## People and teams

```
tfc-org
├── Owners
├── Members (some in no team)
└── Teams
    └── F1tenth_Team (f1tenth_team)
        └── F1tenth_PoliMI_Admins (f1tenth_polimi_admins)
```

- **Parent and child team.** A child team inherits the parent team's repo access, and gets pinged when someone @mentions the parent. Anything given to the child stays with the child. `F1tenth_PoliMI_Admins` is the child, so its members get the team's write access plus anything given to the admins team, such as its bypass on `F1tenth_PoliMI`.
- **Member listing.** Listing the members of `F1tenth_Team` includes the members of its child teams.

## Permissions

| Who | How they get it | All three repos |
|---|---|---|
| Org owners | Org owner | Admin |
| `F1tenth_Team` | Granted on each repo | Write |
| `F1tenth_PoliMI_Admins` | Inherited from `F1tenth_Team` | Write |
| Org members in no team | Org base permission: read | Read |

- **Read** lets a user clone, open issues, comment and review. Their approval does not count toward a required review, and they cannot push branches to the repo, so they work from a fork.
- **Write** lets a user push branches and approve PRs. The rulesets below still block direct pushes to protected branches.
- **Admin** lets a user change repo settings and rulesets. Org owners can edit every ruleset, even when they are not on its bypass list.

## Rulesets

Each ruleset is `active` and targets branches only. Tags are not protected.

| | `F1tenth_PoliMI` | `f1tenth_system` | `f1tenth_gym_ros` |
|---|---|---|---|
| Ruleset | `std-policies` | `std-protection` | `std-protection` |
| Protected branches | `main` | `humble-polimi`, `jazzy-devel` | `dev-humble-polimi`, `dev-humble` |
| Block deletion | yes | yes | yes |
| Block force push | yes | yes | yes |
| Restrict updates | no | yes, sync from upstream allowed | yes, sync from upstream allowed |
| Require a PR | yes | yes | yes |
| Approvals needed | 1 | 1 | 1 |
| Required reviewer team | `F1tenth_Team` (1 approval) | `F1tenth_PoliMI_Admins` (1 approval) | `F1tenth_PoliMI_Admins` (1 approval) |
| New push dismisses approvals | yes | yes | yes |
| Merge methods | merge, rebase | merge, squash, rebase | merge, squash, rebase |
| Bypass | `F1tenth_PoliMI_Admins`, PR only | Repository role Admin, PR only | Repository role Admin, PR only |

`require_extra_approval_for_unattributed_changes` is on in all three rulesets. This page does not say what it does because we have not checked GitHub's definition.

On `F1tenth_PoliMI` the repo setting also allows squash merges, but the ruleset allows only merge and rebase, so squash is blocked on `main`.

### What each rule means

- **Require a PR.** Nobody can push straight to a protected branch, admins included. Every change arrives through a merged PR.
- **Required reviewer team.** At least one approval must come from a member of that team, and that member needs write access. The PR author's approval never counts: GitHub does not let the author approve their own PR. Whether a child-team member's approval counts for the parent team has not been tested.
- **Restrict updates.** Only bypass actors can update the branch. Merging a PR updates it, so on the two forks only repo admins can merge. "Sync fork" from upstream is still allowed.
- **Bypass, PR only.** The bypass works only at merge time, on a PR. A bypass actor still cannot push directly or force-push. On their own PR they see "Merge without waiting for requirements to be met (bypass rules)", which lets them merge without an approval. This is the only way to merge your own PR without someone else's review.

## Who can do what today

| Action | `F1tenth_PoliMI` `main` | Fork protected branches |
|---|---|---|
| Push directly | nobody | nobody |
| Open a PR from a branch in the repo | `F1tenth_Team` members, owners | `F1tenth_Team` members, owners |
| Approve so that it counts | `F1tenth_Team` members who are not the author | `F1tenth_PoliMI_Admins` members who are not the author |
| Merge after the required approval | `F1tenth_Team` members | repo admins only (restrict updates) |
| Merge own PR without approval (bypass) | `F1tenth_PoliMI_Admins` members | repo admins |
| Change the rulesets | repo admins, org owners | repo admins, org owners |

If a PR's author is the only member of the required reviewer team, nobody else can approve it, so the only way to merge it is a bypass merge.

## Differences between the repos

These differences are what the snapshot shows. They are not decisions recorded anywhere else:

- `F1tenth_PoliMI` requires a review from `F1tenth_Team`, while the forks require one from `F1tenth_PoliMI_Admins`.
- `F1tenth_PoliMI` gives the bypass to a team, while the forks give it to the Admin repository role.
- Only the forks restrict updates.
- In `f1tenth_gym_ros`, the branches `main` and `dev-jazzy` are not protected.
