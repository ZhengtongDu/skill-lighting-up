# Concept note template

Use this template for the final Obsidian Markdown. Adjust section depth to the concept, but keep the mathematical and executable parts strong for ML topics.

```markdown
# {概念中文名} ({English Name})

## 概念定义

用 2-4 段说明这个概念是什么、它属于哪个问题域、最核心的对象和关系是什么。术语首次出现时给中英对照。

## 问题背景：它解决什么数学 / 建模问题

说明如果没有这个概念，会遇到什么建模、优化、概率推断、表示学习、检索或工程问题。尽量写成具体问题，而不是泛泛而谈。

## 前置知识补齐

只补真正需要的基础：

- 线性代数对象：向量、矩阵、范数、内积、投影、特征值等。
- 数学分析对象：极限、导数、梯度、链式法则、凸性等。
- 概率对象：随机变量、条件概率、期望、似然、KL、熵等。
- CS/ML 对象：token、batch、tensor、loss、optimizer、autograd、embedding 等。

## 符号约定与张量形状

列出核心符号、shape、含义和单位。例：

| 符号 | shape | 含义 |
|------|-------|------|
| $X$ | $n \times d$ | $n$ 个样本，每个样本 $d$ 维 |
| $w$ | $d$ | 线性模型参数 |
| $y$ | $n$ | 标签 |

## 核心数学推导

从定义推到可计算形式。优先覆盖：

- 目标函数 / 损失函数；
- 矩阵形式；
- 概率解释或似然推导；
- 梯度、更新式或反向传播关键步骤；
- 复杂度、稳定性或边界条件。

不要只给结论。每一步都说明为什么可以这样变形。

## 从公式到算法步骤

把数学式翻译成算法：

1. 输入是什么。
2. 中间量怎么计算。
3. 输出是什么。
4. 训练或推理阶段有什么不同。
5. 哪些实现细节会影响结果。

## Python 最小实现

代码块前说明变量 shape 和示例目标。优先给可运行代码。

```python
# minimal runnable example
```

代码后解释：

- 哪几行对应哪个公式；
- 输出应该如何理解；
- 如果换成真实 ML 任务，需要补哪些部分。

## 真实 ML 应用例子

给 1-3 个真实场景，说明该概念如何进入模型、训练、评测或系统实现。例子要尽量来自论文、官方文档、课程或可信博客。

## 常见误区和边界条件

列出容易混淆的概念、错误直觉、实现坑、数值稳定性问题、数据泄露风险或评测误读。

## 与相关概念的关系

用短段或表格说明它和相邻概念的区别。可使用 Obsidian wiki 链接：

- [[相关概念 A]]
- [[相关概念 B]]

## 小结

用几句话收束：这个概念的本质、最重要公式、最值得记住的实现细节。

## 参考资料

- 作者或机构. 标题. URL. 访问日期或发布日期.
```

## Style rules

- Prefer precise Chinese prose over tutorial filler.
- Keep formulas in Markdown math: inline `$...$`, display `$$...$$`.
- Use tables when they clarify symbols, shapes, source comparisons, or failure modes.
- Keep code short enough to read in one screen when possible.
- Preserve exact technical names, paper titles, function names, and package names.
