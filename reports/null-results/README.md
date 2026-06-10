# Null Results

This directory exists because null results are results.

A null result — a pre-registered hypothesis where H0 was not rejected — is scientific information. It tells the field what is not true, which is often as valuable as what is. The suppression of null results is publication bias. It distorts the evidence base. It is not done here.

## What Goes Here

Every hypothesis test where H0 was not rejected gets a file in this directory. The file contains:

- The hypothesis ID and full statement
- The test statistic, p-value, effect size, and CI
- An interpretation: what does this null result mean?
- An assessment of power: was the test adequately powered? If not, the null result is uninformative (a negative finding from an underpowered test cannot be interpreted as evidence for H0)
- Whether the null result is itself informative or merely inconclusive

## File Format

`H[module].[number]_null.md`

```markdown
## Null Result: H[module].[number]

**Hypothesis (H1)**: [statement]
**Null (H0)**: [statement]
**Test**: [named test]
**Result**: [test statistic], p = [value], [effect size measure] = [value], 95% CI [lower, upper]
**Powered**: [yes / no — from power analysis]
**Interpretation**: [what this means]
**Is this result informative?**: [yes if adequately powered; no if underpowered]
**Future work**: [what test or dataset would resolve the question]
```
