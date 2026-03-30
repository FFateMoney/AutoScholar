# 深度分析报告

## 1. 一页结论

- 方向: OpenPQFormer Idea
- 当前建议: `not-ready`
- Overall score: 0.332

Investigate whether unsupported spatial regions in medical image segmentation should be modeled as an explicit unknown-region or abstention map rather than being forced into a known-class prediction. 基于当前证据，OpenPQFormer Idea目前还不足以直接写成稳定的论文主线。 当前支撑相对最强的部分集中在 adjacent-literature support, unknown-region abstention。 目前最需要补证据或收窄表述的部分是 adjacent-literature support, unknown-region abstention。

当前更适合把这个方向写成“问题定义清晰、证据边界明确、相邻文献可支撑”的工作，而不是假设已经存在成熟且密集的同题主线。

## 2. 证据全景

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

## 3. 推荐的问题定义与边界

- 先把 strongest claims 写成主问题定义或主贡献，再围绕它们组织 related work。
- 明确指出哪些证据是 direct support，哪些只是 adjacent support，避免叙事越界。
- 如果某些 claim 只有 mixed/weak support，应把它们降级为动机、风险或未来工作。
- 当前尤其需要对 unknown-region abstention, adjacent-literature support 进行降级、重写或补证据。

## 4. 方法层建议

- 方法部分必须显式 operationalize 最核心的 problem claim，而不是只在动机里提出它。
- 优先做最小可解释改动，让每个模块都能回指到一条 claim 或一组证据。
- 把 top papers 当作设计信号、baseline 或对照，而不是宣称它们已经解决了完全同一问题。
- 当前方法叙事建议围绕 adjacent-literature support, unknown-region abstention 展开。

## 5. 实验与验证建议

- 至少设计一个实验直接验证 strongest claim，而不是只报告常规主指标。
- 对 mixed/weak claims 单独安排 stress test、ablation 或 falsification-style 实验。
- 比较对象优先选择 evidence map 中最靠前的 direct/adjacent papers。
- 若 unknown-region abstention, adjacent-literature support 仍要保留在论文里，就必须给出专门验证协议。

## 6. 论文中可以主张什么 / 不应主张什么

### 可以主张

- 当前方向具有继续推进价值，而且能被写成证据边界清楚的研究问题。
- 相邻文献已经足以支撑问题动机、风险建模或评价协议设计。
- 在收窄表述的前提下，可以把 strongest claims 作为论文主线。

### 不应主张

- 不要宣称已经存在成熟且密集的同题主线，除非 direct support 明显增多。
- 不要把所有邻域证据都写成完全同任务 prior art。
- 不要做“统一解决所有相邻问题”的宽泛主张。

## 7. 主要风险与应对

- 风险: Manual review is still required for claims: OPQ01, OPQ02.
  应对: Review claim statuses and rewrite weak queries before treating the idea as publication-ready.

## 8. 参考证据清单

- 《MOOD 2020: A Public Benchmark for Out-of-Distribution Detection and Localization on Medical Images》 (2022), IEEE TMI, DOI=10.1109/TMI.2022.3170077- 《Limitations of Out-of-Distribution Detection in 3D Medical Image Segmentation》 (2023), Journal of Imaging, DOI=10.3390/jimaging9090191
