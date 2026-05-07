# Set Up Community Translation Platform (Weblate/Crowdin)

**GitHub Issue**: #522 - https://github.com/bdperkin/nhl-scrabble/issues/522

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

4-6 hours

## Description

Set up a community translation platform (Weblate or Crowdin) to enable community-driven translations for all 12 supported locales. This will democratize translation work, leverage community expertise, and maintain translation quality through collaborative review processes.

## Current State

Translation workflow is manual and developer-centric:
- Translators must edit .po files directly
- No web-based translation interface
- No community collaboration features
- No translation memory or suggestions
- No quality checks or validation in UI
- Difficult for non-technical contributors

Current workflow:
```bash
# Manual process - requires git, text editor, command line
git clone repo
vim src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po
make i18n-compile
git commit && git push
```

## Proposed Solution

### Option 1: Weblate (Recommended - Free for Open Source)

**Advantages:**
- Free hosted service for open source projects: https://hosted.weblate.org
- GitHub integration (automatic sync)
- Translation memory and suggestions
- Quality checks (placeholders, formatting, consistency)
- Community collaboration (comments, suggestions, voting)
- Glossary support for hockey terminology
- Supports GNU gettext .po files natively
- API for automation
- User roles and permissions

**Setup:**
1. Create project on Weblate hosted service
2. Connect to GitHub repository
3. Configure component for each locale
4. Set up automatic sync (Weblate ↔ GitHub)
5. Add quality checks configuration
6. Create glossary for hockey terms
7. Document contribution process

**Configuration:**
```yaml
# .weblate
[nhl-scrabble]
url = https://hosted.weblate.org/projects/nhl-scrabble/
repo = https://github.com/bdperkin/nhl-scrabble.git
filemask = src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po
file_format = po
```

### Option 2: Crowdin (Free for Open Source)

**Advantages:**
- Free for open source projects
- Modern web UI
- GitHub integration
- Translation memory
- Quality checks
- Community features

**Setup:**
1. Create project on Crowdin
2. Upload .po files
3. Configure GitHub integration
4. Set up quality checks
5. Invite community translators

## Implementation Steps

1. **Choose Platform**: Weblate (recommended for gettext support)

2. **Create Project on Weblate**:
   - Sign up at https://hosted.weblate.org
   - Create "NHL Scrabble" project
   - Add component for each locale (12 components)
   - Configure file paths and formats

3. **Configure GitHub Integration**:
   - Enable Weblate GitHub app
   - Set up automatic push/pull
   - Configure merge strategy
   - Set up commit author mapping

4. **Set Up Quality Checks**:
   ```python
   # Weblate quality checks configuration
   checks:
     - "python-format"          # Verify {count}, %(name)s placeholders
     - "same"                   # Warn if translation = source
     - "end-space"              # Check trailing whitespace
     - "bbcode"                 # Check [green], [/green] markup
     - "max-length"             # Warn on overly long translations
     - "inconsistent"           # Check terminology consistency
   ```

5. **Create Hockey Terminology Glossary**:
   | English | Context | Notes |
   |---------|---------|-------|
   | Goalie | Player position | Region-specific: gardien (fr_CA), målvakt (sv_SE) |
   | Faceoff | Game event | mise au jeu (fr_CA), nedsläpp (sv_SE) |
   | Power play | Game situation | avantage numérique (fr_CA), powerplay (sv_SE) |
   | Playoff | Tournament | séries éliminatoires (fr_CA), slutspel (sv_SE) |

6. **Document Contribution Process**:
   - Update CONTRIBUTING.md with Weblate instructions
   - Add TRANSLATING.md section on using Weblate
   - Create video tutorial (optional)
   - Add badges to README.md

7. **Invite Community Translators**:
   - Post on r/hockey, r/Habs, r/SwedenHockey
   - Share on social media
   - Add "Help translate" link to documentation
   - Credit contributors in releases

8. **Configure Automation**:
   - Auto-approve translations from trusted users
   - Auto-merge when checks pass
   - Weekly digest of translation activity
   - Notify maintainers of new languages

## Testing Strategy

1. **Test Translation Workflow**:
   ```bash
   # Make translation on Weblate
   # Wait for auto-sync to GitHub
   # Verify .po file updated in repo
   # Verify .mo file compiled in CI
   # Test in application: NHL_SCRABBLE_LANG=fr_CA nhl-scrabble analyze
   ```

2. **Test Quality Checks**:
   - Submit translation with missing placeholder → Should warn
   - Submit translation with wrong markup → Should warn
   - Submit overly long translation → Should warn
   - Submit good translation → Should accept

3. **Test Community Features**:
   - Add suggestion as contributor → Should allow
   - Comment on translation → Should appear
   - Vote on suggestions → Should work
   - View glossary → Should show terms

## Acceptance Criteria

- [ ] Weblate project created and configured
- [ ] All 12 locales added as components
- [ ] GitHub integration working (bidirectional sync)
- [ ] Quality checks enabled and tested
- [ ] Hockey terminology glossary created (50+ terms)
- [ ] CONTRIBUTING.md updated with Weblate instructions
- [ ] TRANSLATING.md updated with community translation section
- [ ] README.md has translation status badge
- [ ] At least 3 community translators invited
- [ ] Test translation submitted and synced successfully
- [ ] Documentation complete

## Related Files

- `CONTRIBUTING.md` - Add Weblate contribution guide
- `TRANSLATING.md` - Add community translation section
- `README.md` - Add translation status badge
- `.github/ISSUE_TEMPLATE/translation.md` - New template for translation issues
- `docs/contributing/translating.md` - Detailed Weblate guide

## Dependencies

- GitHub repository (exists)
- All 12 locale .po files initialized (complete)
- Weblate hosted account (free for open source)

## Additional Notes

### Weblate Features

**Translation Memory**:
- Suggests similar translations from this project
- Can import translations from other projects
- Learns from accepted translations

**Quality Checks**:
- Automatic validation of placeholders
- Consistency checks across locales
- Grammar and style checks (limited)
- Custom checks can be added

**Community Features**:
- Public project visibility
- Anyone can suggest translations
- Voting on suggestions
- Comments and discussion
- Translation credits

**Automation**:
- Auto-sync with GitHub (every hour or on push)
- Auto-compile .mo files in CI
- Auto-create PRs for translation updates
- Notifications for maintainers

### Crowdin vs Weblate Comparison

| Feature | Weblate | Crowdin |
|---------|---------|---------|
| **Cost** | Free (OSS) | Free (OSS) |
| **GitHub Sync** | ✅ Bidirectional | ✅ Bidirectional |
| **gettext Support** | ✅ Native | ✅ Good |
| **Translation Memory** | ✅ Yes | ✅ Yes |
| **Quality Checks** | ✅ Extensive | ✅ Good |
| **Community** | ✅ Strong | ✅ Strong |
| **Self-Hosting** | ✅ Yes | ❌ No |
| **API** | ✅ Full API | ✅ Full API |
| **Glossary** | ✅ Yes | ✅ Yes |
| **Recommendation** | ✅ **Best for gettext** | Good alternative |

### Translation Badges

Add to README.md:
```markdown
[![Translation Status](https://hosted.weblate.org/widgets/nhl-scrabble/-/svg-badge.svg)](https://hosted.weblate.org/engage/nhl-scrabble/)

[![Translation Status](https://hosted.weblate.org/widgets/nhl-scrabble/-/multi-auto.svg)](https://hosted.weblate.org/engage/nhl-scrabble/)
```

### Expected Impact

**Before:**
- Only developers can translate
- High barrier to contribution
- Slow translation updates
- No community involvement

**After:**
- Anyone can contribute translations
- Web-based, no technical skills required
- Fast community-driven updates
- Quality checks prevent errors
- Translation memory improves consistency
- Hockey terminology glossary ensures accuracy

### Community Engagement

**Outreach:**
- r/hockey, r/Habs, r/SwedenHockey subreddits
- Hockey forums (hfboards.com, etc.)
- Open source communities
- University hockey clubs
- International NHL fan groups

**Incentives:**
- Credit in CONTRIBUTORS.md
- GitHub commit attribution
- Translation leaderboard
- Special thanks in release notes
- Community recognition

### Maintenance

**Weekly:**
- Review new translations
- Approve/reject suggestions
- Answer questions

**Monthly:**
- Update glossary with new terms
- Audit translation quality
- Thank top contributors
- Share progress updates

**Per Release:**
- Sync all translations
- Credit contributors
- Post translation completion stats
- Invite feedback

## Implementation Notes

*To be filled during implementation:*
- Platform chosen (Weblate/Crowdin)
- Project URL
- Number of community translators
- Translation coverage achieved
- Challenges encountered
- Actual effort vs estimated
