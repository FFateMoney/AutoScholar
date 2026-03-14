# 可行性评估报告

## 1. 评估结论

- 方向: OpenPQFormer Idea
- 当前建议: `not-ready`
- 生成时间: 2026-03-14T18:00:48.997264+00:00

Investigate whether unsupported spatial regions in medical image segmentation should be modeled as an explicit unknown-region or abstention map rather than being forced into a known-class prediction. 基于当前证据，OpenPQFormer Idea目前还不足以直接写成稳定的论文主线。 当前支撑相对最强的部分集中在 adjacent-literature support, unknown-region abstention。 目前最需要补证据或收窄表述的部分是 adjacent-literature support, unknown-region abstention。

## 2. 为什么值得继续做

当前最有把握继续推进的是 adjacent-literature support, unknown-region abstention，这些部分已经有可直接引用或可稳定借用的邻域文献支撑。

当前最薄弱的是 unknown-region abstention, adjacent-literature support。这意味着论文叙事应先收窄，不要把所有相邻问题都写成已经被同一批文献充分支撑。

## 3. 当前不足与风险

- Manual review is still required for claims: OPQ01, OPQ02.

## 4. 建议的收敛方向

- 优先把 strongest claims 写成论文主线，把 weak claims 降级为动机、风险或后续工作。
- 把邻域文献写成 support surface，而不是写成已经存在成熟同题主线。
- 在摘要、引言和贡献点里避免超过当前证据边界的宽泛表述。
- 对 unknown-region abstention, adjacent-literature support 先补检索或重写 query，再决定是否保留为正式 claim。

## 5. 关键证据摘要

### OPQ01 · unknown-region abstention
- 状态: review
- 证据强度: mixed
- Claim: Medical image segmentation systems should be allowed to abstain on unsupported spatial regions instead of forcing every region into a known label set.

当前证据能部分支撑“unknown-region abstention”，但更像邻域拼接而不是成熟主线，应重点核查 《Limitations of Out-of-Distribution Detection in 3D Medical Image Segmentation》 的适配边界。

- 备注: 相关 query 状态包含: review。

- 《Limitations of Out-of-Distribution Detection in 3D Medical Image Segmentation》 (2023), Journal of Imaging, citations=22  支撑类型: adjacent。《Limitations of Out-of-Distribution Detection in 3D Medical Image Segmentation》更像邻域支撑文献，适合用来说明相关问题真实存在、评价设置可行，当前引用数约为 22。

### OPQ02 · adjacent-literature support
- 状态: review
- 证据强度: mixed
- Claim: The most relevant prior work is spread across medical OOD localization, uncertainty-aware segmentation, and segmentation failure detection rather than a mature open-set segmentation line.

当前证据能部分支撑“adjacent-literature support”，但更像邻域拼接而不是成熟主线，应重点核查 《MOOD 2020: A Public Benchmark for Out-of-Distribution Detection and Localization on Medical Images》 的适配边界。

- 备注: Direct open-set segmentation support remains limited; validate framing manually.
- 备注: 相关 query 状态包含: keep。

- 《MOOD 2020: A Public Benchmark for Out-of-Distribution Detection and Localization on Medical Images》 (2022), IEEE TMI, citations=64  支撑类型: direct。《MOOD 2020: A Public Benchmark for Out-of-Distribution Detection and Localization on Medical Images》与“adjacent-literature support”的表述最接近，且已有 64 次引用，可以作为直接支撑或最靠近的对照文献。

## 6. 下一步建议

- Review claim statuses and rewrite weak queries before treating the idea as publication-ready.
- Validate the top supporting papers against the intended contribution and problem framing.
- Run another recommendation pass or rewrite the weakest claims after manual inspection.
