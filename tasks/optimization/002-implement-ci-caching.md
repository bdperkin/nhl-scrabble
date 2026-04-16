# Implement CI, Tox, Pre-commit, and Related Tools Caching

**GitHub Issue**: #60 - https://github.com/bdperkin/nhl-scrabble/issues/60

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-5 hours

## Description

Implement comprehensive caching strategies across GitHub Actions CI workflows to significantly reduce CI execution time and minimize redundant downloads and compilations. Currently, only UV caching is partially enabled, leaving substantial optimization opportunities on the table.

## Current State

### Existing Caching

The project currently has minimal caching implemented in `.github/workflows/ci.yml`:

**UV Caching (Enabled in test and tox jobs):**

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
    cache-dependency-glob: "pyproject.toml"
```

**UV Caching (DISABLED in pre-commit job):**

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: false  # ❌ Caching disabled!
```

### Missing Caching Opportunities

**1. Pre-commit Hooks Environment**

- Pre-commit downloads and builds hook repositories on every CI run
- These environments are stored in `~/.cache/pre-commit`
- Rebuilding 55+ hooks takes significant time (2-3 minutes)
- Hook repositories rarely change between commits

**2. Python Dependency Cache**

- Pip cache directory (`~/.cache/pip`) not cached
- UV cache directory not explicitly cached beyond setup-uv action
- Dependencies re-downloaded even when unchanged

**3. Tool-Specific Caches**

- **Pytest cache** (`.pytest_cache/`) - Test result caching and deselection
- **MyPy cache** (`.mypy_cache/`) - Incremental type checking
- **Ruff cache** (`.ruff_cache/`) - Incremental linting
- **Tox environments** (`.tox/`) - Virtual environments per testenv

**4. GitHub Actions Cache**

- No use of `actions/cache@v3` for any directories
- Missing cache key strategies for dependency files

### Performance Impact

Current CI times without comprehensive caching:

- **Test job** (per Python version): ~2-3 minutes
- **Tox job** (per environment): ~1-2 minutes
- **Pre-commit job**: ~3-4 minutes (rebuilds all hooks)

**Total CI time**: ~12-15 minutes for full matrix

## Proposed Solution

Implement multi-level caching strategy for all CI jobs:

### 1. Enable UV Caching in Pre-commit Job

**File**: `.github/workflows/ci.yml` (pre-commit job)

**Change**:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true  # ✅ Enable caching
    cache-dependency-glob: "pyproject.toml"
```

**Benefit**: Cache UV packages for pre-commit dependencies

### 2. Add Pre-commit Hooks Cache

**File**: `.github/workflows/ci.yml` (pre-commit job)

**Add after checkout step**:

```yaml
- name: Cache pre-commit hooks
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      pre-commit-${{ runner.os }}-

- name: Cache Python dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'uv.lock') }}
    restore-keys: |
      pip-${{ runner.os }}-
```

**Cache Key Strategy**:

- Primary key: Hash of `.pre-commit-config.yaml` (changes when hooks update)
- Restore key: OS-specific fallback (reuse even if config changed slightly)
- Invalidates automatically when hook versions change

**Benefit**:

- Avoid rebuilding 55+ hook environments every run
- Reduce pre-commit job from ~3-4 minutes to ~30-60 seconds
- **5-6x speedup** on pre-commit job

### 3. Add Tool-Specific Caches to Test Jobs

**File**: `.github/workflows/ci.yml` (test job)

**Add after setup-python step**:

```yaml
- name: Cache tool directories
  uses: actions/cache@v4
  with:
    path: |
      .pytest_cache
      .mypy_cache
      .ruff_cache
    key: tools-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('src/**/*.py', 'tests/**/*.py') }}
    restore-keys: |
      tools-${{ runner.os }}-py${{ matrix.python-version }}-
      tools-${{ runner.os }}-
```

**Cache Key Strategy**:

- Primary key: Hash of all Python source files
- Restore keys: Fallback to same Python version, then any version
- Invalidates when code changes

**Benefit**:

- MyPy incremental mode reuses previous type checking results
- Ruff skips unchanged files
- Pytest can use previous test results for smarter execution
- **20-30% speedup** on test jobs

### 4. Add Tox Environment Caching

**File**: `.github/workflows/ci.yml` (tox job)

**Add after checkout step**:

```yaml
- name: Cache tox environments
  uses: actions/cache@v4
  with:
    path: .tox
    key: tox-${{ runner.os }}-${{ matrix.tox-env }}-${{ hashFiles('pyproject.toml', 'tox.ini', 'uv.lock') }}
    restore-keys: |
      tox-${{ runner.os }}-${{ matrix.tox-env }}-
      tox-${{ runner.os }}-
```

**Cache Key Strategy**:

- Primary key: Hash of dependency files (pyproject.toml, tox.ini, uv.lock)
- Restore keys: Fallback to same tox env, then any env
- Per-environment caching (py310, py311, etc.)

**Benefit**:

- Reuse tox virtual environments when dependencies unchanged
- Skip environment creation step (~30-60 seconds per env)
- **30-50% speedup** on tox jobs

### 5. Comprehensive Caching Strategy

**Cache Hierarchy**:

1. **UV Cache** (via setup-uv) - Package downloads
1. **Pip Cache** (via actions/cache) - Compiled wheels
1. **Pre-commit Cache** (via actions/cache) - Hook environments
1. **Tool Caches** (via actions/cache) - Incremental checks
1. **Tox Environments** (via actions/cache) - Virtual environments

**Cache Invalidation**:

- Automatic when dependency files change
- Manual via repository cache deletion
- 7-day expiration for unused caches (GitHub default)

**Cache Size Estimates**:

- Pre-commit hooks: ~200-500 MB (55 hook repos)
- Tox environments: ~100-200 MB per env
- Tool caches: ~10-50 MB
- UV/pip caches: ~50-100 MB

**Total cache storage**: ~2-3 GB (well within GitHub's 10 GB limit per repo)

## Implementation Steps

### Step 1: Enable UV Caching in Pre-commit Job

1. Edit `.github/workflows/ci.yml`
1. Locate pre-commit job (line ~115)
1. Find "Install uv" step (line ~129)
1. Change `enable-cache: false` to `enable-cache: true`

### Step 2: Add Pre-commit Hooks Cache

1. In `.github/workflows/ci.yml`, pre-commit job

1. After checkout step, add cache step:

   ```yaml
   - name: Cache pre-commit hooks
     uses: actions/cache@v4
     with:
       path: ~/.cache/pre-commit
       key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}
       restore-keys: |
         pre-commit-${{ runner.os }}-
   ```

### Step 3: Add Python Dependency Cache

1. In same pre-commit job, add pip cache:

   ```yaml
   - name: Cache Python dependencies
     uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: pip-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'uv.lock') }}
       restore-keys: |
         pip-${{ runner.os }}-
   ```

### Step 4: Add Tool Caches to Test Job

1. In `.github/workflows/ci.yml`, test job

1. After setup-python step, add:

   ```yaml
   - name: Cache tool directories
     uses: actions/cache@v4
     with:
       path: |
         .pytest_cache
         .mypy_cache
         .ruff_cache
       key: tools-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('src/**/*.py', 'tests/**/*.py') }}
       restore-keys: |
         tools-${{ runner.os }}-py${{ matrix.python-version }}-
         tools-${{ runner.os }}-
   ```

### Step 5: Add Tox Environment Cache

1. In `.github/workflows/ci.yml`, tox job

1. After checkout step, add:

   ```yaml
   - name: Cache tox environments
     uses: actions/cache@v4
     with:
       path: .tox
       key: tox-${{ runner.os }}-${{ matrix.tox-env }}-${{ hashFiles('pyproject.toml', 'tox.ini', 'uv.lock') }}
       restore-keys: |
         tox-${{ runner.os }}-${{ matrix.tox-env }}-
         tox-${{ runner.os }}-
   ```

### Step 6: Update .gitignore (if needed)

Ensure cache directories are ignored:

```gitignore
# Tool caches (already present but verify)
.pytest_cache/
.mypy_cache/
.ruff_cache/
.tox/
```

### Step 7: Document Caching Strategy

1. Update `docs/DEVELOPMENT.md` with cache information
1. Add section "CI Caching Strategy"
1. Document cache keys, invalidation, and troubleshooting

### Step 8: Test Cache Effectiveness

1. Create test PR
1. Observe cache misses on first run
1. Push trivial commit (e.g., comment change)
1. Verify cache hits on second run
1. Measure time savings

## Testing Strategy

### Manual Testing

**Test 1: Cache Miss Scenario**

1. Create new PR branch
1. Push changes that modify dependencies
1. Check CI logs for "Cache not found" messages
1. Verify caches are saved at end of jobs
1. **Expected**: No cache hits, full execution time

**Test 2: Cache Hit Scenario**

1. Push trivial change (e.g., update comment in code)
1. Check CI logs for "Cache restored successfully" messages
1. Verify reduced execution time
1. **Expected**: Cache hits, 30-50% faster execution

**Test 3: Pre-commit Cache**

1. Update `.pre-commit-config.yaml` (change hook version)
1. Push commit
1. Check CI logs for pre-commit cache miss
1. Verify new hooks are built and cached
1. **Expected**: Cache miss, new cache created

**Test 4: Dependency Change**

1. Modify `pyproject.toml` (add/update dependency)
1. Push commit
1. Check CI logs for cache invalidation
1. Verify new caches created with new keys
1. **Expected**: Relevant caches invalidated, new caches built

### Automated Testing

**Metrics to Track**:

1. **Job execution times** (before vs after):

   - Test job per Python version
   - Tox job per environment
   - Pre-commit job

1. **Cache statistics**:

   - Cache hit rate (%)
   - Cache size (MB)
   - Cache restore time (seconds)

1. **Overall CI time**:

   - Total CI duration for full matrix
   - Time to first failure
   - Time to all green

### Verification

**Success Criteria**:

- ✅ Pre-commit job time reduced by 50%+
- ✅ Test job time reduced by 20%+
- ✅ Tox job time reduced by 30%+
- ✅ Overall CI time reduced by 30-40%
- ✅ No CI failures due to stale caches
- ✅ Caches invalidate correctly on dependency changes

**Rollback Plan**:

If caching causes issues:

1. Identify problematic cache
1. Remove cache step from workflow
1. Clear repository caches via GitHub UI
1. Re-run CI

## Acceptance Criteria

- [ ] UV caching enabled in pre-commit job
- [ ] Pre-commit hooks cache implemented with correct key strategy
- [ ] Python dependency (pip) cache implemented
- [ ] Tool-specific caches (pytest, mypy, ruff) implemented in test job
- [ ] Tox environment cache implemented with per-env keys
- [ ] Cache restore logs show "Cache restored successfully" on cache hits
- [ ] Cache save logs show cache sizes and keys
- [ ] Documentation updated in docs/DEVELOPMENT.md
- [ ] Tested with cache miss scenario (no errors)
- [ ] Tested with cache hit scenario (reduced execution time)
- [ ] Tested with dependency change (cache invalidation works)
- [ ] Overall CI time reduced by at least 30% on cache hits
- [ ] No CI failures due to stale or corrupted caches
- [ ] All 35 existing CI checks still pass

## Related Files

- `.github/workflows/ci.yml` - Main CI workflow (all three jobs)
- `docs/DEVELOPMENT.md` - Development documentation (add caching section)
- `.gitignore` - Verify cache directories excluded
- `.pre-commit-config.yaml` - Pre-commit configuration (cache key dependency)
- `pyproject.toml` - Dependency configuration (cache key dependency)
- `tox.ini` - Tox configuration (cache key dependency)
- `uv.lock` - UV lock file (cache key dependency)

## Dependencies

**Required**:

- GitHub Actions `actions/cache@v4` (already available)
- GitHub Actions `setup-uv@v4` (already in use)
- Repository cache storage (10 GB limit, currently ~0 GB used)

**No blocking dependencies**: This task can be implemented immediately.

## Additional Notes

### Performance Expectations

**Before Caching** (current state):

```
Test job (py3.10):     ~2.5 min
Test job (py3.11):     ~2.5 min
Test job (py3.12):     ~2.5 min
Test job (py3.13):     ~2.5 min
Tox matrix (31 envs):  ~45-60 min
Pre-commit:            ~3-4 min
──────────────────────────────
Total CI time:         ~12-15 min (excluding parallel matrix)
```

**After Caching** (expected with cache hits):

```
Test job (py3.10):     ~2.0 min  (20% faster)
Test job (py3.11):     ~2.0 min  (20% faster)
Test job (py3.12):     ~2.0 min  (20% faster)
Test job (py3.13):     ~2.0 min  (20% faster)
Tox matrix (31 envs):  ~25-35 min (40% faster)
Pre-commit:            ~1.0 min  (70% faster!)
──────────────────────────────
Total CI time:         ~7-10 min (35-40% faster)
```

### Cache Size Management

GitHub Actions cache limits:

- **Per repository**: 10 GB total
- **Per cache entry**: No explicit limit
- **Retention**: 7 days for unused caches

**Expected cache usage**:

- Pre-commit: ~300 MB (1 entry)
- Pip: ~100 MB (1 entry per OS)
- Tools: ~50 MB (4 entries, one per Python version)
- Tox: ~2 GB (31 entries, one per tox env)

**Total**: ~2.5 GB (well within 10 GB limit)

### Cache Invalidation Strategies

**Automatic invalidation** (via cache keys):

1. **Dependency changes**: Hash of pyproject.toml, uv.lock, tox.ini
1. **Hook updates**: Hash of .pre-commit-config.yaml
1. **Code changes**: Hash of src/**/\*.py, tests/**/\*.py (for tools)

**Manual invalidation** (when needed):

1. GitHub UI: Settings → Actions → Caches → Delete cache
1. Or: Use GitHub CLI: `gh cache delete <cache-key>`

### Security Considerations

**Cache poisoning prevention**:

- Cache keys include file hashes (tamper detection)
- Caches are scoped to repository (no cross-repo access)
- GitHub Actions cache is signed and verified
- Cache restore failures fall back to fresh builds

**No sensitive data in caches**:

- All cached content is from public package indexes
- Pre-commit hooks from public repositories
- Tool caches contain only build artifacts

### Trade-offs

**Pros**:

- ✅ 30-40% faster CI on cache hits
- ✅ Reduced bandwidth usage
- ✅ Faster feedback on PRs
- ✅ Lower GitHub Actions compute usage
- ✅ Better developer experience

**Cons**:

- ❌ Added complexity to workflow YAML
- ❌ 2.5 GB cache storage used
- ❌ Potential for stale cache issues
- ❌ Cache management overhead
- ❌ Slightly slower on cache misses (cache save time)

**Mitigation**:

- Document cache strategy thoroughly
- Implement robust cache key strategies
- Monitor cache hit rates
- Clear caches if issues arise

### Future Enhancements

After implementing basic caching, consider:

1. **Conditional caching**: Skip cache on main branch merges
1. **Cache warming**: Pre-populate caches on schedule
1. **Advanced cache keys**: More granular invalidation
1. **Cache analytics**: Track hit rates and effectiveness
1. **Compression**: Compress cache artifacts for faster transfer

### References

- GitHub Actions Cache Documentation: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
- actions/cache@v4: https://github.com/actions/cache
- UV Caching: https://github.com/astral-sh/setup-uv#caching
- Pre-commit CI: https://pre-commit.com/#github-actions-example
- Tox and caching: https://tox.wiki/en/latest/example/basic.html#caching

## Implementation Notes

*To be filled during implementation:*

- Actual cache sizes observed
- Actual time savings measured
- Cache hit rates on typical PRs
- Any issues encountered
- Deviations from plan
- Actual effort vs estimated
