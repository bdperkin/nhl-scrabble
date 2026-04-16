#!/usr/bin/env bash
# Git hook to warn about committing directly to protected branches

set -e

BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
PROTECTED_BRANCHES="^(main|master)$"

# Check if running in CI environment
is_ci() {
    # GitHub Actions
    [[ -n "${GITHUB_ACTIONS}" ]] && return 0
    # GitLab CI
    [[ -n "${GITLAB_CI}" ]] && return 0
    # Travis CI
    [[ -n "${TRAVIS}" ]] && return 0
    # CircleCI
    [[ -n "${CIRCLECI}" ]] && return 0
    # Jenkins
    [[ -n "${JENKINS_URL}" ]] && return 0
    # Generic CI indicator
    [[ -n "${CI}" ]] && return 0

    return 1
}

if [[ "$BRANCH" =~ $PROTECTED_BRANCHES ]]; then
    # In CI: Allow the commit (it's already on main after PR merge)
    if is_ci; then
        echo "ℹ️  CI environment detected: Allowing commit to '$BRANCH' branch"
        exit 0
    fi

    # Local: Warn and prompt for confirmation
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  WARNING: You are committing directly to the '$BRANCH' branch!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ Best practice workflow:"
    echo "   1. Create a feature branch:"
    echo "      git checkout -b feature/your-feature-name"
    echo ""
    echo "   2. Make your commits on the feature branch"
    echo ""
    echo "   3. Push and create a PR:"
    echo "      git push -u origin feature/your-feature-name"
    echo "      gh pr create"
    echo ""
    echo "   4. Merge via PR after CI passes"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "To proceed anyway: Continue below (not recommended)"
    echo "To abort and create a feature branch: Press Ctrl+C"
    echo ""
    read -p "⚠️  Continue committing to '$BRANCH'? [y/N] " -n 1 -r
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Commit aborted."
        echo ""
        echo "💡 Quick fix if you already made commits to main:"
        echo "   # Move commits to a feature branch"
        echo "   git checkout -b feature/your-feature-name"
        echo "   git checkout main"
        echo "   git reset --hard origin/main"
        echo "   git checkout feature/your-feature-name"
        echo ""
        exit 1
    fi

    echo "✅ Proceeding with commit to '$BRANCH' (you chose to bypass protection)..."
    echo ""
fi

exit 0
