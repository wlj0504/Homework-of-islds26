# 统计学习方法课后作业 (SCUT)

2026年春季学期，华南理工大学（SCUT）数学专业大二下学期《统计学习方法》课程相关练习。

这是我的机器学习与统计学习方法代码仓库，目前主要包含了基于《统计学习导论》(ISLP) 的课后习题 Python 实现。

## 包含的内容

* `boston_exercise.py`: 波士顿房价数据集的回归分析练习。
* `carseats_regression.py`: Carseats 数据集的多元线性回归与分类变量处理。
* `compare_linear_and_cubic_regression_rss.py`: 线性回归与三次回归的 RSS 对比分析。
* `stats_learning_concepts.py`: 统计学习基础概念（分类与回归、预测与推断）的场景判断脚本。

## 运行环境与依赖库

在运行本项目代码前，请确保安装了以下 Python 库：

* `pandas`
* `numpy`
* `statsmodels`
* `ISLP` (包含练习所需的数据集)

可以通过以下命令快速安装：

```bash
pip install pandas numpy statsmodels
pip install ISLP -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://pypi.tuna.tsinghua.edu.cn/simple)
