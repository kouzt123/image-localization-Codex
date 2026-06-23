# 广告图片本地化 Codex Skill

**使用 Codex 内置图像生成能力进行广告图片本地化，不需要额外图片 API。**

[English](./README.md) · [安装说明](./install.md) · [Skill 文件](./SKILL.md) · [许可证](./LICENSE)

Ad Image Localization 是一个 Codex Skill，用于把源广告图片素材处理成可直接投放的多语言广告和社交平台素材。它适合市场、投放、运营、电商和创作者，用来批量生成多语言、多尺寸创意。

![广告图片本地化工作流总览](./examples/workflow-split-overview.zh-CN.png)

## 核心卖点

- **使用 Codex 订阅额度**进行图片生成和编辑。
- **不需要额外 API 配置**：不需要图片 API Key，不需要单独的计费账户，也不需要接入额外生成服务。
- **原生视觉效果**：优先使用 Codex 内置视觉理解、图像生成和图像编辑，而不是简单蒙版换字或机械拉伸。
- **Imagegen-first 工作流**：涉及像素变化的生成、改字、扩图和版式适配，应先调用 Codex 的 `imagegen` skill 和内置 `image_gen` 路径；本地脚本只做确定性的收尾处理。
- **适合投放工作流**：规范命名、manifest、常见广告尺寸、交付前视觉 QA 和 Culture-Aware QA。
- **适合长期跑任务**：虽然速度不如专门的批量图片 API，但配置成本低、质量好、综合性价比高，适合市场同学后台长期跑。

## 取舍

Codex 内置图像流程相对慢，不适合追求极限吞吐量的场景。这个 Skill 优先优化的是低配置成本、原生视觉质量和可交付性。

未来可能会更新另一个基于 Nano Banana API 的高吞吐版本，用于更快的大批量产出。

## 能做什么

- 翻译图片中的可见文字。
- 对阿拉伯语等 RTL 语言默认尝试 RTL-aware 版式适配；如果 QA 判断适配后效果更差，则回退到仅翻译文案的保守模式。
- 保留品牌名、产品名、Logo、主体和视觉层级。
- 输出常见广告/社交尺寸：
  - `1200x1200`
  - `1920x1080`
  - `1080x1350`
  - `1080x1920`
  - `1200x628`
- 标准广告比例用 `imagegen` 原生生成；特殊近似比例只从安全的模型原生输出里做确定性裁切。
- 维护品牌/产品术语记忆。
- 输出规范命名的文件和 manifest。
- 交付前进行视觉 QA，不合格图片会尝试重做一次。
- 在 QA 阶段执行 Culture-Aware QA，把可能存在目标市场文化风险的文件移入 `Flagged by Culture-Aware QA/`，提醒用户投放前复核。
- 内置确定性辅助脚本，用于安全派生裁切、manifest、文件名/尺寸检查、QA 总览图、文化风险分拣和术语记忆更新。

![规范命名输出文件夹 demo](./examples/organized-output-folder.png)

## 它有什么不同

这不是一个通用的图片翻译工具。

大多数图片翻译项目主要关注 OCR、文字擦除、翻译和重新渲染。而这个 skill 更关注 **广告创意本地化交付**：翻译图片中的营销文案，保留品牌词和产品词，适配常见广告尺寸，生成可直接上传的文件命名，输出 manifest，并在 Codex 工作流中完成视觉 QA。

![虚构广告本地化 demo](./examples/demo-localization-grid.zh-CN.png)

对于阿拉伯语等 RTL 语言，skill 会优先尝试符合 RTL 阅读习惯的版式适配；如果 QA 判断适配后效果更差，则回退到仅翻译文案的版本。

## RTL 感知本地化

对于阿拉伯语等从右到左阅读的语言，这个 skill 采用质量优先的回退策略：默认先尝试 RTL-aware 本地化；如果适配后的版式不自然、阅读效率更差或影响品牌识别，则回退到仅翻译文案的保守模式。

![RTL 感知本地化 QA 回退 demo](./examples/rtl-aware-localization.zh-CN.png)

- **方案 A：开启 RTL-aware（RTL 语言默认）**：在有收益时，按从右到左的阅读习惯适配排版和信息层级，包括文字方向、右对齐、CTA 阅读流、局部文案块、对话气泡或少量 UI 局部布局。
- **方案 B：关闭 RTL-aware / 回退模式**：只翻译可见文案，尽量保留原始构图和整体布局。

建议阿拉伯语等 RTL 语言默认使用方案 A；当版式适配导致构图失衡、品牌识别受损或文字排版变差时，使用方案 B。这是一个默认启用、但受 QA 控制的策略，不是强制对所有阿语素材进行整图镜像，也不会默认翻转 logo 或大幅移动品牌识别。

## Culture-Aware QA

在 QA 阶段，skill 还会检查本地化后的创意在目标市场是否可能存在文化、法律、宗教、社会习俗或政治风险。这个环节只做风险提示和文件分拣，不会自动修改创意，也不构成法律合规意见。

它会结合目标市场、语言、产品品类和画面语境来判断，例如宗教敏感、受监管宣称、国境线或地图争议、政治符号、手势、食物或动物意象、着装/审美习俗、本地广告限制等。它不会使用固定黑名单；如果风险依赖当前法律、政治语境或平台规则，Codex 应该现场搜索当前资料后再说明。

如果某个变体被标记，skill 会把受影响文件移动到：

```text
Flagged by Culture-Aware QA/
```

用户应在投放前二次确认，或额外要求 Codex 生成更安全的修改版本。默认情况下，skill 不会主动改这些被标记的创意。

## 辅助脚本

仓库内置的 Python 辅助脚本只在模型原生产出之后处理确定性的交付收尾工作。它**不会**调用图片 API，也不会替代 Codex `imagegen` 或内置图像生成。

```bash
python -m pip install -r requirements.txt
python scripts/ad_image_localization_tools.py cover-crop input.png output.jpg --size 1200x628
python scripts/ad_image_localization_tools.py manifest localized_output/
python scripts/ad_image_localization_tools.py verify localized_output/
python scripts/ad_image_localization_tools.py contact-sheet localized_output/ qa_contact_sheet.jpg
python scripts/ad_image_localization_tools.py flag-culture-aware localized_output/ rabbit-social-networks_ar_1200x628_20260622.jpg --market "GCC" --reason "Needs local cultural review"
python scripts/ad_image_localization_tools.py memory-add brand_term_memory.json --brand openai --term Codex --action preserve
```

建议在模型原生生成之后使用它，完成可复用的安全派生裁切、manifest、文件名/尺寸检查、视觉 QA 总览图、Culture-Aware QA 风险分拣，以及品牌/产品术语记忆维护。不要用辅助脚本生成主要的 `1:1`、`16:9`、`4:5` 或 `9:16` 版本；这些尺寸应由 `imagegen` 原生生成。脚本依赖 Pillow；如果不使用 Codex 自带 Python 运行时，本地可用 `python -m pip install -r requirements.txt` 安装依赖。

本地辅助脚本测试：

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python scripts/ad_image_localization_tools.py verify examples/verified-delivery-pack
```

## 安装

### 让 Codex 帮你安装

推荐方式：让 Codex 帮你安装。

```text
帮我安装这个 Codex skill：https://github.com/kouzt123/ad-image-localization-codex
```

Codex 可以把仓库克隆到本机 skills 目录，并告诉你是否需要重启或刷新 skills。

### 手动安装

直接安装到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/kouzt123/ad-image-localization-codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
```

如果你想把仓库放在其他位置，可以用软链接：

```bash
git clone https://github.com/kouzt123/ad-image-localization-codex ~/Developer/ad-image-localization-codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn ~/Developer/ad-image-localization-codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
```

如果你的 Codex 环境需要刷新 Skill，安装后重启或刷新一次即可。

更多说明见 [install.md](./install.md)。

## 使用示例

在 Codex 中明确调用这个 Skill：

```text
使用 ad-image-localization，把这张游戏广告翻译成德语、法语、西班牙语、日语、韩语，并输出 1200x1200、1920x1080、1080x1350、1080x1920 和 1200x628。
```

其他示例：

```text
把这张海报本地化成阿拉伯语和越南语。产品名保持英文，1200x628 不要拉伸文字。
```

阿拉伯语默认优先尝试 RTL-aware 版式适配；如果 QA 判断适配后效果更差，则回退到仅翻译文案、保留原整体布局的版本。

QA 阶段请同时执行 Culture-Aware QA。如果某个本地化变体可能需要目标市场复核，请把受影响尺寸移入 `Flagged by Culture-Aware QA/`，并说明原因。

如果要维护术语记忆，请说明品牌或产品范围：

```text
记住这个术语规则：Example Brand 的素材里，PixelPass 保持英文，不要翻译。
```

## Prompt Cookbook

### 游戏广告

```text
使用 ad-image-localization，把这张游戏广告本地化成德语、西班牙语、日语和阿拉伯语。保留游戏标题，翻译所有角色属性和 UI 标签，并输出 1200x1200、1920x1080、1080x1350、1080x1920 和 1200x628。
```

对于阿拉伯语等 RTL 语言，skill 会优先尝试符合 RTL 阅读习惯的版式适配；如果 QA 判断适配后效果更差，则回退到仅翻译文案的版本。

### 电商商品图

```text
使用 ad-image-localization，生成这张商品 banner 的法语和葡萄牙语版本。品牌名保持不变，本地化优惠文案，并输出 Meta feed、story 和 1200x628 link-ad 尺寸。
```

### SaaS Banner

```text
使用 ad-image-localization，把这个 SaaS 发布 banner 本地化成日语和韩语。保持产品 UI 可读，保留 logo，并生成 16:9 和带安全边的 1200x628。
```

### App Store / 社媒截图

```text
使用 ad-image-localization，把这些 app 截图做成印尼语和越南语投放素材。翻译可见营销文案，保持 UI 标签自然，并输出规范文件名和 manifest.json。
```

## 尺寸处理

标准广告比例应分别用 `imagegen` 原生生成，让文字、构图、主体位置和安全区都自然适配。

以 `1200x628` 这类特殊近似比例为例，推荐的确定性派生流程是：

1. 先让模型生成带上下安全边的 `16:9` 版本。
2. 将 `1920x1080` 等比缩放到 `1200x675`。
3. 再裁掉上下多余像素，得到 `1200x628`。

这样可以保持几何比例，避免非等比压缩导致文字或主体变形。

辅助脚本已经把这个逻辑做成可复用命令：

```bash
python scripts/ad_image_localization_tools.py cover-crop 1920x1080.png 1200x628.jpg --size 1200x628
```

## 术语记忆

Skill 支持用 JSON 文件保存用户确认过的术语规则：

```json
{
  "version": 1,
  "brands": {
    "example-brand": {
      "display_name": "Example Brand",
      "rules": [
        {"term": "Example Brand", "action": "preserve"}
      ],
      "products": {}
    }
  }
}
```

品牌级规则适用于该品牌下的所有产品。产品级规则可以覆盖品牌级规则。

## 仓库结构

```text
ad-image-localization-codex/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── install.md
├── LICENSE
├── requirements.txt
├── scripts/
│   └── ad_image_localization_tools.py
├── tests/
├── examples/
├── brand_term_memory.json
└── agents/
    └── openai.yaml
```

## 许可证

MIT。见 [LICENSE](./LICENSE)。
