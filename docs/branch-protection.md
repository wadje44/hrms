# Branch protection (apply when available)

Branch protection / rulesets are **not available on the free plan for private repos**.
Apply this once the repo is public, or after upgrading to GitHub Pro/Team.

Policy: require a PR (0 approvals — solo repo, so self-merge is allowed), require the
three CI checks to pass with branches up to date, require conversation resolution, and
enforce the rules on admins too.

```bash
gh api --method PUT "repos/wadje44/hrms/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  --input docs/branch-protection.json
```

`docs/branch-protection.json`:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Backend (lint + tests)",
      "Frontend (lint + build)",
      "Terraform (fmt + validate)"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "required_conversation_resolution": true,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false
}
```

> The `contexts` are the CI job display names from `.github/workflows/ci.yml`. If you
> rename those jobs, update them here too. To require an approving review later (once you
> have a second collaborator), bump `required_approving_review_count` to `1`.
