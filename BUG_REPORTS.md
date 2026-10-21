# Bug reports — FashionGram

Found while building this suite against [FashionGram](https://github.com/andrew84eg-ops/FashionGram) (commit on `main`, October 2026), running locally on Chromium.

Each UI defect has a test in [`tests/ui/test_known_defects.py`](tests/ui/test_known_defects.py) that asserts the **correct** behaviour and is marked `xfail(strict=True)`. The suggested fix for FG-002 to FG-005 is in [`docs/suggested-fix.patch`](docs/suggested-fix.patch); with it applied, all four tests pass.

| ID | Title | Severity | Status |
| --- | --- | --- | --- |
| FG-001 | `npm ci` fails: lock file out of sync with `package.json` | High (blocks clean CI installs) | Open |
| FG-002 | New member's feed and closet can appear empty after sign-up | High (first impression) | Open, fix verified |
| FG-003 | White-top warning stays after switching to another category | Medium | Open, fix verified |
| FG-004 | White-top warning missing when colour is picked before category | Medium | Open, fix verified |
| FG-005 | Cream tops count as "white" in insights but not in the warning | Low | Open, fix verified |

---

## FG-001 · `npm ci` fails: lock file out of sync

**Severity:** High. A clean, reproducible install is impossible, so any CI that uses `npm ci` breaks.

**Steps**
1. Clone the repository.
2. Run `npm ci`.

**Expected:** dependencies install exactly as locked.
**Actual:** exits with `EUSAGE`: *lock file's ajv@6.15.0 does not satisfy ajv@8.20.0*, plus missing entries for `fast-uri`, `json-schema-traverse` and `require-from-string`.

**Workaround in this suite:** CI uses `npm install` (see `.github/workflows/e2e.yml`).
**Fix:** run `npm install` once and commit the regenerated `package-lock.json`.

---

## FG-002 · New member's feed and closet can appear empty after sign-up

**Severity:** High. The first screen a new member sees can say *"Follow members from Explore to fill this timeline"* although they already follow four members with 12 public pieces.

**Steps**
1. Sign up a new account.
2. Land on `/feed` (or go straight to `/closet`).

**Expected:** the feed shows the followed members' public pieces; the closet shows the 8-piece starter closet.
**Actual:** intermittently (2 of 5 runs on a warm server, more often on a cold one) the feed shows the empty state and the closet shows *"0 pieces"*. A page reload fixes it.

**Root cause**
- `src/routes/_app.tsx` fires `ensureProfile()` (which creates the starter closet and the follows) in a `useEffect`, without waiting for it.
- The feed, closet and insights queries start in parallel. If they return first, they cache empty results.
- Nothing invalidates those queries when `ensureProfile` finishes, and `staleTime` is 15 s (`src/routes/__root.tsx`), so the empty state stays.

**How the test makes it deterministic:** it holds the `ensureProfile` request until the feed has rendered, releases it, then expects the posts to appear without a reload.

**Fix (verified):** invalidate queries once setup resolves: `ensureProfile().then(() => qc.invalidateQueries())`.

---

## FG-003 · White-top warning stays after switching to another category

**Severity:** Medium. The warning that powers the product's main promise gives wrong information.

**Steps**
1. Open **Add item**. Category is *Tops*.
2. Pick colour **White**. The warning *"You already have Ivory Silk Blouse in the closet."* appears (correct).
3. Change category to **Shoes**.

**Expected:** the warning disappears; white shoes are not a duplicate white top.
**Actual:** the warning stays on screen.

**Root cause:** the duplicate check only runs inside the colour click handler (`onColor` in `src/routes/_app/add.tsx`); changing the category never re-evaluates it.

**Fix (verified):** derive the warning from `category` and `color` together, in an effect that runs when either changes.

---

## FG-004 · White-top warning missing when colour is picked before category

**Severity:** Medium. Same root cause as FG-003, opposite symptom: the user is not warned at all.

**Steps**
1. Open **Add item**. Change category to **Dresses**.
2. Pick colour **White** (no warning, correct).
3. Change category back to **Tops**.

**Expected:** the warning appears, because the member already owns a white top.
**Actual:** no warning. The result depends on the order the fields are filled in.

**Fix (verified):** same as FG-003.

---

## FG-005 · Cream tops count as "white" in insights but not in the warning

**Severity:** Low. Two parts of the app disagree about the same rule.

**Steps**
1. Open **Closet**: the summary says *"You already have 2 ivory/white tops"* (Ivory Silk Blouse and Cream Cashmere).
2. Open **Add item**, keep *Tops*, pick **Cream**.

**Expected:** a warning naming the cream top, consistent with the closet summary.
**Actual:** no warning. Picking **White** names only *Ivory Silk Blouse*, never *Cream Cashmere*.

**Root cause:** `closetInsights` in `src/lib/server/fashion.ts` treats `ivory`, `white` and `cream` as white; the add form checks only `ivory` and `white`.

**Fix (verified):** use one shared rule for "white-ish" colours in both places.
