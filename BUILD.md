# WordMaster — 构建指南

## 目录结构

```
wordmaster-web/
├── www/index.html          ← WordMaster 源码（修改这个文件）
├── android/                ← Capacitor Android 平台
├── resources/              ← 图标源文件 + 生成脚本
│   ├── icon-512.png
│   └── generate_icons.py
├── capacitor.config.json
├── package.json
└── .github/workflows/build-apk.yml  ← CI 自动构建
```

## 修改 Web 内容

改 `www/index.html`，然后：

```bash
npx cap sync          # 同步到 Android 平台
```

## 修改 App 图标

```bash
cd resources
python generate_icons.py   # 重新生成所有尺寸 PNG
```

## 本地构建 APK

需要安装：
- [Android Studio](https://developer.android.com/studio)
- JDK 17（Android Studio 自带）

```bash
# 方式一：命令行
cd android
./gradlew assembleDebug
# APK 在 android/app/build/outputs/apk/debug/app-debug.apk

# 方式二：Android Studio
# 打开 android/ 目录 → 点击绿色 ▶ 运行
```

## 自动构建（推荐）

推送代码到 GitHub `main` 分支，GitHub Actions 自动构建：

1. `git push origin main`
2. 打开 https://github.com/9854607/wordmaster/actions
3. 等构建完成 → 下载 artifact（APK）

也可手动触发：Actions → Build Android APK → Run workflow。

## 安装到手机

1. 下载 `app-debug.apk`
2. 传到手机（微信/数据线/网盘）
3. 手机设置 → 允许安装未知来源应用
4. 点击 APK 安装
5. 桌面出现 WordMaster 图标，点击打开

## 更新已安装的 App

直接安装新 APK 覆盖即可，localStorage 数据不丢（WebView 内部存储独立于 APK 更新）。
