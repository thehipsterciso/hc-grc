# Codebook

A codebook documents the meaning of every variable in every dataset used by this project. It is different from a schema document. A schema says what type a field is. A codebook says what a field means — its semantic content, how it was measured, what its values represent, and what its known limitations are.

The codebook is the bridge between raw data and analysis. An analyst who has never seen the source data should be able to fully understand every variable from this document alone.

---

## Codebook Entry Format

```
### [Variable Name]

**Source dataset**: [filename and location]
**Source field name**: [exact name in the raw file, if different]
**Measurement level**: Nominal / Ordinal / Interval / Ratio
**Definition**: [What does this variable actually measure? Not the field name restated — the semantic content.]
**Values / Range**: [For categorical: all valid values with their meaning. For continuous: expected range, units.]
**Missing value codes**: [How is missingness represented in the source? NaN, empty string, "N/A", -1, etc.]
**Known limitations**: [Measurement error, ambiguity, undocumented conventions, edge cases]
**Provenance**: [How was this variable generated? Expert judgment? Automated? Formula?]
**Notes**: [Anything else an analyst needs to know]
```

---

## Datasets

### [Dataset 1 Name]

*Source*: [path in data/raw/]  
*Acquired*: [date]  
*N observations*: [count]  
*Unit of analysis*: [what is one row]  

#### Variables

[One entry per variable in the format above]

---

## Cross-Dataset Relationships

If multiple datasets are joined in this project, document the join keys and their semantics here. A join key that is not semantically identical across datasets is a data quality problem.

| Join key | Dataset A field | Dataset B field | Are they semantically identical? | Known discrepancies |
|----------|----------------|----------------|----------------------------------|---------------------|
| | | | | |

---

## Derived Variables

Variables computed from raw data are documented here in addition to the entry in the relevant dataset section. Include the formula or logic and the script that produces them.

| Variable name | Derived from | Logic / formula | Script |
|--------------|-------------|-----------------|--------|
| | | | |
