# safeval_jd381

**算出模型安全评测负责人·量化位宽与精度回退里各项的占比与比值。**

`safeval_jd381` —— 从输入中抽取数值，计算模型安全评测负责人·量化位宽与精度回退相关的比值与占比，分母为零时明确报错

- 零依赖，Python 3.10+ 标准库即可运行
- 单文件，`safeval_jd381.py` 拷走就能用
- 不联网、不写文件

## 对应的岗位

- 目标岗位：**百度 · 负责人模型安全评测负责人**
- 技能主线：安全对齐、LLM评测、Agent
- 领域标签：AI安全对齐
- 研究方向：模型安全评测负责人·量化位宽与精度回退

工具里的规则表就是照着上面这条岗位要求建的——每条规则都挂在技能线或领域标签上，命中时能指回具体要求。

<!-- ipos:install -->
## 安装

零依赖，Python 3.10+ 即可：

```bash
pip install ucymideqou-safeval_jd381
```

装完直接用命令名调用：

```bash
safeval_jd381 --help
```

也可以不用安装，直接把 `safeval_jd381.py` 拷走用——它只依赖标准库。

## 为什么需要它

分母为零时明确报错，不返回 0 也不返回无穷，避免污染下游统计

它遵守下面几条自己定的规矩：

1. **只报告能定位到具体位置的结论**，不做语义猜测。
2. **规则表公开**，每条命中都能对应到岗位要求的一条明示规则。
3. **输入为空或格式不对时明确报错**，不静默返回空结果。

## 用法

```bash
python safeval_jd381.py --file input.txt
python safeval_jd381.py --text "示例内容"
python safeval_jd381.py --file input.txt --json
```

加 `--json` 可以拿到机器可读的结果，便于接到流水线里。

## 已知局限

- 比例的分母取自你给的口径，不替你选口径。
- 不判断比例高低是否合理。

## 跑测试

```bash
python test_safeval_jd381.py
```

测试用独立的断言与临时数据，不污染工作目录。

## 来源与参考

- Python 标准库文档：<https://docs.python.org/3/>
- GitHub 仓库：<https://github.com/ucymideqou/safeval_jd381>

---

## 关于作者

ucymideqou 做模型安全评测负责人·量化位宽与精度回退相关的问题，方向对标百度的负责人模型安全评测负责人岗位。这个工具先替你回答一个具体问题，再谈别的。

- 个人主页：<https://ucymideqou.github.io>
- 仓库：<https://github.com/ucymideqou/safeval_jd381>

## 许可

MIT，见 [LICENSE](LICENSE)。
