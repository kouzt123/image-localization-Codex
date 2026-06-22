# Installation

[中文](#中文安装说明)

## Install For Codex

### Easiest Option

Copy this prompt into Codex:

```text
Help me install this Codex skill: https://github.com/kouzt123/ad-image-localization-codex
```

Codex can clone the repo into your local skills folder and tell you when to restart or refresh skills.

### Manual Option

Clone the repository into the Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/kouzt123/ad-image-localization-codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
```

If you already keep projects in `~/Developer`, clone there and symlink the whole directory:

```bash
git clone https://github.com/kouzt123/ad-image-localization-codex ~/Developer/ad-image-localization-codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn ~/Developer/ad-image-localization-codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
```

Restart Codex or refresh skills if your environment requires it.

## Verify

Ask Codex:

```text
Use ad-image-localization to inspect this image and propose localized ad sizes.
```

If the skill is available, Codex should read `SKILL.md` before acting.

To test the local helper script:

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

## Update

If installed by clone:

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
git pull --ff-only
```

If installed by symlink:

```bash
cd ~/Developer/ad-image-localization-codex
git pull --ff-only
```

## Notes

- No external image API key is required.
- Image generation uses Codex built-in image capabilities and your Codex subscription quota.
- Optional terminology memory lives in `brand_term_memory.json` or a project-local `.ad-image-localization/brand_term_memory.json`.

# 中文安装说明

## 安装到 Codex

### 最简单的方式

把下面这段话复制到 Codex：

```text
帮我安装这个 Codex skill：https://github.com/kouzt123/ad-image-localization-codex
```

Codex 可以把仓库克隆到本机 skills 目录，并告诉你是否需要重启或刷新 skills。

### 手动安装

直接克隆到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/kouzt123/ad-image-localization-codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
```

如果你习惯把项目放在 `~/Developer`，可以克隆后软链接整个目录：

```bash
git clone https://github.com/kouzt123/ad-image-localization-codex ~/Developer/ad-image-localization-codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn ~/Developer/ad-image-localization-codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
```

如果你的 Codex 环境需要刷新 Skill，安装后重启或刷新一次。

## 验证

在 Codex 中输入：

```text
使用 ad-image-localization，识别这张图片并建议本地化广告尺寸。
```

如果 Skill 生效，Codex 会先读取 `SKILL.md` 再行动。

测试本地辅助脚本：

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

## 更新

如果是直接克隆安装：

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/ad-image-localization"
git pull --ff-only
```

如果是软链接安装：

```bash
cd ~/Developer/ad-image-localization-codex
git pull --ff-only
```

## 说明

- 不需要额外图片 API Key。
- 图像生成使用 Codex 内置图像能力和你的 Codex 订阅额度。
- 可选术语记忆文件为 `brand_term_memory.json`，也可以使用项目内的 `.ad-image-localization/brand_term_memory.json`。
