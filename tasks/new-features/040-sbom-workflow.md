# Software Bill of Materials (SBOM) Generation Workflow

**GitHub Issue**: #307 - https://github.com/bdperkin/nhl-scrabble/issues/307

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Implement automated SBOM (Software Bill of Materials) generation workflow that creates comprehensive dependency inventories in standard formats (CycloneDX, SPDX) for supply chain transparency and compliance. Generated on releases and stored as artifacts.

## Current State

**No SBOM Generation:**

Currently, there's no automated dependency inventory:

- No SBOM generation
- No supply chain transparency
- No compliance documentation
- Manual dependency tracking
- No vulnerability correlation

## Proposed Solution

Create `.github/workflows/sbom.yml`:

```yaml
name: SBOM Generation

on:
  release:
    types: [published]
  push:
    branches:
      - main
    paths:
      - pyproject.toml
      - uv.lock
  schedule:
    # Weekly SBOM generation (Mondays at 6 AM UTC)
    - cron: 0 6 * * 1
  workflow_dispatch:

permissions:
  contents: write  # For attaching to releases
  actions: read

jobs:
  generate-sbom:
    name: Generate SBOM
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install UV and cyclonedx-bom
        run: |
          pip install uv cyclonedx-bom

      - name: Install project dependencies
        run: |
          uv pip install -e . --system

      - name: Generate CycloneDX SBOM (JSON)
        run: |
          cyclonedx-py environment \
            --output-format json \
            --output-file sbom-cyclonedx.json \
            --gather-license-texts

      - name: Generate CycloneDX SBOM (XML)
        run: |
          cyclonedx-py environment \
            --output-format xml \
            --output-file sbom-cyclonedx.xml \
            --gather-license-texts

      - name: Generate SPDX SBOM
        uses: anchore/sbom-action@v0
        with:
          format: spdx-json
          output-file: sbom-spdx.json

      - name: Add metadata to SBOMs
        run: |
          # Add build metadata
          echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> sbom-metadata.txt
          echo "Repository: ${{ github.repository }}" >> sbom-metadata.txt
          echo "Commit: ${{ github.sha }}" >> sbom-metadata.txt
          echo "Ref: ${{ github.ref }}" >> sbom-metadata.txt

      - name: Upload SBOM artifacts
        uses: actions/upload-artifact@v4
        with:
          name: sbom-${{ github.sha }}
          path: |
            sbom-*.json
            sbom-*.xml
            sbom-metadata.txt
          retention-days: 90

      - name: Attach SBOMs to release
        if: github.event_name == 'release'
        uses: softprops/action-gh-release@v2
        with:
          files: |
            sbom-cyclonedx.json
            sbom-cyclonedx.xml
            sbom-spdx.json
            sbom-metadata.txt
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Vulnerability scan with Grype
        uses: anchore/scan-action@v3
        with:
          sbom: sbom-spdx.json
          fail-build: false
          severity-cutoff: high

      - name: Upload vulnerability results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: ${{ steps.scan.outputs.sarif }}
```

## Implementation Steps

1. **Create Workflow File** (1h)

   - Create `.github/workflows/sbom.yml`
   - Configure triggers (releases, schedule, manual)
   - Set up SBOM generation
   - Configure artifact uploads

1. **Configure SBOM Formats** (30min)

   - CycloneDX JSON (for tools)
   - CycloneDX XML (for compliance)
   - SPDX JSON (industry standard)
   - Add metadata

1. **Integrate Vulnerability Scanning** (30min)

   - Add Grype scanning
   - Upload SARIF results
   - Configure severity thresholds

1. **Test Workflow** (30min-1h)

   - Trigger manual run
   - Verify SBOMs generated
   - Verify formats valid
   - Test release attachment
   - Verify vulnerability scanning

1. **Add Documentation** (30min)

   - Document SBOM locations
   - Explain SBOM formats
   - Add compliance notes
   - Update SECURITY.md

## Testing Strategy

```bash
# Manual trigger
gh workflow run sbom.yml

# Monitor execution
gh run watch

# Download generated SBOMs
gh run download <run-id>

# Verify CycloneDX JSON
cat sbom-cyclonedx.json | jq .

# Verify SPDX JSON
cat sbom-spdx.json | jq .

# Validate CycloneDX
cyclonedx validate --input-file sbom-cyclonedx.json

# Test with release
git tag v0.0.1-test
git push --tags
# Verify SBOMs attached to release
gh release view v0.0.1-test
```

## Acceptance Criteria

- [ ] Workflow file created: `.github/workflows/sbom.yml`
- [ ] Generates CycloneDX JSON SBOM
- [ ] Generates CycloneDX XML SBOM
- [ ] Generates SPDX JSON SBOM
- [ ] Runs on releases
- [ ] Runs weekly on schedule
- [ ] Runs on dependency changes
- [ ] Includes license information
- [ ] Includes metadata (commit, date, etc.)
- [ ] Uploads artifacts
- [ ] Attaches to releases
- [ ] Vulnerability scanning integrated
- [ ] SARIF results uploaded
- [ ] Documentation updated
- [ ] Test run verified

## Related Files

**New Files:**

- `.github/workflows/sbom.yml` - SBOM generation workflow

**Modified Files:**

- `SECURITY.md` - Document SBOM availability
- `CLAUDE.md` - Document SBOM workflow
- `README.md` - Add SBOM badge (optional)

## Dependencies

**Tool Dependencies:**

- `cyclonedx-bom` - CycloneDX Python library
- `anchore/sbom-action` - SPDX generation
- `anchore/scan-action` - Vulnerability scanning

## Additional Notes

### SBOM Formats

**CycloneDX:**

- Industry standard
- Tool-friendly JSON/XML
- License information
- Vulnerability correlation

**SPDX:**

- Linux Foundation standard
- Compliance-focused
- Industry acceptance
- Tool integration

### Use Cases

**Compliance:**

- Software composition analysis
- License compliance
- Security audits
- Vendor requirements

**Security:**

- Vulnerability tracking
- Dependency monitoring
- Incident response
- Risk assessment

### SBOM Contents

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "components": [
    {
      "name": "requests",
      "version": "2.31.0",
      "type": "library",
      "licenses": [
        {
          "license": {
            "id": "Apache-2.0"
          }
        }
      ],
      "purl": "pkg:pypi/requests@2.31.0"
    }
  ]
}
```

## Implementation Notes

*To be filled during implementation:*

- Date started:
- Date completed:
- Number of components:
- License types found:
