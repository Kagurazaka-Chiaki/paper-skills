# Matching Evidence

Use these signals in descending order of trust:

1. DOI match
2. exact title match
3. title plus first author plus year
4. title plus venue
5. first-page text fragments that uniquely identify the paper

Use filenames only as weak hints.

Treat these as duplicate indicators:

- same DOI
- same bibkey in local records
- exact or near-exact title plus author/year agreement

Stop and report ambiguity when:

- multiple candidates remain plausible
- the PDF is a proceedings volume rather than the target paper
- extracted metadata conflicts with first-page evidence
