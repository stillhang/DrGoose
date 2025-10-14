# 多语言设置指南

## 配置说明

我已经为你的Hugo网站配置了多语言支持，包括中文和英文。

### 1. 配置文件

使用 `hugo-multilang.toml` 作为你的配置文件，它包含了完整的多语言设置：

```toml
[languages]
[languages.zh]
title = "Dr.Goose"
languageName = "中文"
weight = 1

[languages.en]
title = "Dr.Goose"
languageName = "English"
weight = 2
```

### 2. 语言切换器

在导航栏右侧添加了语言切换器，用户可以点击切换语言。

### 3. 内容结构

```
content/
├── about/           # 中文内容
│   ├── index.md
│   └── about.md
├── posts/           # 中文文章
│   └── test-post.md
├── search/          # 中文搜索页面
│   └── _index.md
└── en/              # 英文内容
    ├── about/
    │   ├── index.md
    │   └── about.md
    ├── posts/       # 英文文章
    │   └── test-post.md
    └── search/      # 英文搜索页面
        └── _index.md
```

### 4. 使用方法

1. **替换配置文件**：
   ```bash
   mv hugo.toml hugo.toml.backup
   mv hugo-multilang.toml hugo.toml
   ```

2. **启动服务器**：
   ```bash
   hugo server -D
   ```

3. **访问网站**：
   - 中文版本：`http://localhost:1313/`
   - 英文版本：`http://localhost:1313/en/`

### 5. 添加新内容

- **中文内容**：直接放在 `content/` 目录下
- **英文内容**：放在 `content/en/` 目录下

### 6. 自定义语言

如需添加其他语言，在配置文件中添加：

```toml
[languages.ja]
title = "Dr.Goose"
languageName = "日本語"
weight = 3
```

然后创建对应的内容目录 `content/ja/`。

## 注意事项

- 语言切换器会自动检测可用的语言
- 每种语言都需要对应的内容文件
- 建议保持内容结构的一致性
