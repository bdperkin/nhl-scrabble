# SLSA Provenance Generation Workflow

**GitHub Issue**: #308 - https://github.com/bdperkin/nhl-scrabble/issues/308

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

Implement SLSA (Supply chain Levels for Software Artifacts) provenance generation workflow that creates cryptographically signed build attestations, verifying build integrity and providing supply chain security.

## Current State

**No Build Provenance:**

Currently, there's no build attestation:

- No build provenance
- No cryptographic verification
- No supply chain attestation
- Cannot verify build integrity
- No SLSA compliance

## Proposed Solution

Integrate provenance into publish workflow:

```yaml
# Add to .github/workflows/publish.yml

jobs:
  # ... existing build job ...

  provenance:
    name: Generate Provenance
    needs: build
    permissions:
      actions: read
      id-token: write
      contents: write
    uses: 
      slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.9.0
    with:
      base64-subjects: ${{ needs.build.outputs.hashes }}
      upload-assets: true

  # Add to build job:
  build:
    outputs:
      hashes: ${{ steps.hash.outputs.hashes }}

    steps:
      # ... existing steps ...

      - name: Generate hashes
        id: hash
        run: |
          cd dist
          sha256sum * > checksums.txt
          echo "hashes=$(cat checksums.txt | base64 -w0)" >> $GITHUB_OUTPUT
```

## Implementation Steps

1. **Modify Publish Workflow** (1h)

   - Add provenance job
   - Add hash generation
   - Configure SLSA generator
   - Set permissions

1. **Configure Signing** (30min)

   - Use Sigstore/Cosign
   - Configure keyless signing
   - Set up attestation

1. **Test Workflow** (1-1.5h)

   - Create test release
   - Verify provenance generated
   - Verify signatures valid
   - Test verification

1. **Add Documentation** (30min)

   - Document provenance availability
   - Add verification instructions
   - Update SECURITY.md

## Testing Strategy

```bash
# Verify provenance
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp="^https://github.com/bdperkin/nhl-scrabble" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  ghcr.io/bdperkin/nhl-scrabble:latest

# Download provenance
gh release download v2.1.0 --pattern "*.intoto.jsonl"  # codespell:ignore intoto

# Verify with slsa-verifier
slsa-verifier verify-artifact \
  nhl_scrabble-2.1.0-py3-none-any.whl \
  --provenance-path nhl_scrabble-2.1.0.intoto.jsonl \  # codespell:ignore intoto
  --source-uri github.com/bdperkin/nhl-scrabble
```

## Acceptance Criteria

- [ ] Provenance job added to publish workflow
- [ ] SLSA Level 3 compliance
- [ ] Cryptographic signing enabled
- [ ] Provenance attached to releases
- [ ] Verification instructions documented
- [ ] Test verification successful
- [ ] SECURITY.md updated

## Related Files

**Modified Files:**

- `.github/workflows/publish.yml` - Add provenance
- `SECURITY.md` - Document provenance
- `docs/RELEASING.md` - Add verification steps

## Dependencies

**Task Dependencies:**

- **Depends on**: new-features/032-pypi-publish-workflow
- **Integrated with**: Publishing workflow

**Tool Dependencies:**

- `slsa-framework/slsa-github-generator` - SLSA generator
- `sigstore/cosign` - Signing and verification

## Additional Notes

### SLSA Levels

**Level 1**: Documentation
**Level 2**: Hosted build platform
**Level 3**: Provenance + non-falsifiable (this implementation)
**Level 4**: Two-party review

### Provenance Contents

```json
{
  "predicate": {
    "buildType": "https://github.com/slsa-framework/slsa-github-generator/generic@v1",
    "builder": {
      "id": "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@refs/tags/v1.9.0"
    },
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/bdperkin/nhl-scrabble@refs/tags/v2.1.0"
      }
    }
  }
}
```

### Benefits

- Build integrity verification
- Supply chain security
- Non-repudiation
- Compliance (NIST SSDF, EO 14028)

## Implementation Notes

*To be filled during implementation:*

- SLSA level achieved:
- Verification test results:
