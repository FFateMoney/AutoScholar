# Deep Dive

## Idea Summary

- Idea: OpenPQFormer Idea
- Recommendation: `needs-revision`
- Overall score: 0.332

Investigate whether unsupported spatial regions in medical image segmentation should be modeled as an explicit unknown-region or abstention map rather than being forced into a known-class prediction.

## Claim-Level Evidence

### OPQ01

- Status: review
- Claim: Medical image segmentation systems should be allowed to abstain on unsupported spatial regions instead of forcing every region into a known label set.

- 1. Limitations of Out-of-Distribution Detection in 3D Medical Image Segmentation (2023)
  cite_count=22, support_score=2.25, final_score=17.44

### OPQ02

- Status: review
- Claim: The most relevant prior work is spread across medical OOD localization, uncertainty-aware segmentation, and segmentation failure detection rather than a mature open-set segmentation line.
- Note: Direct open-set segmentation support remains limited; validate framing manually.

- 1. MOOD 2020: A Public Benchmark for Out-of-Distribution Detection and Localization on Medical Images (2022)
  cite_count=64, support_score=3.25, final_score=28.19
