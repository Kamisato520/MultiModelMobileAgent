# MultiModelMobileAgent

## 项目简介
MultiModelMobileAgent 是一个智能自动化测试平台，旨在通过自然语言指令控制移动设备执行自动化任务。项目采用前后端分离架构，后端基于 Flask，前端计划使用 React，支持多模态输入（文本、语音、图像）和设备管理。

## 功能特性
- **设备管理**：支持 Android/iOS 设备连接状态追踪和信息查询。
- **任务系统**：创建、执行和追踪自动化任务，支持文本和语音输入。
- **自动化能力**：基于 uiautomator2 实现 Android 设备自动化（点击、输入、滑动等）。
- **大模型集成**：接入阿里云通义千问（Qwen）系列模型，支持多模态分析和指令生成。
- **实时通信**：通过 WebSocket 实现设备状态和任务进度同步。
- **测试界面**：提供基础测试页面（test.html），支持实时执行结果展示。

## 已优化内容
- **大模型通信**：优化提示词，定义动作模式，验证指令有效性。
- **动态界面处理**：集成 Qwen-VL 视觉模型，提升元素定位能力。
- **上下文管理**：支持多轮对话，完善状态存储。

## 待办事项
- 完善前端界面（设备管理、任务监控）。
- 增强错误处理和日志记录。
- 添加用户认证和 API 访问控制。
- 提高测试覆盖率（单元测试、集成测试）。
- 部署优化（Docker 容器化）。

## 技术栈
- **后端**：Python, Flask
- **数据库**：PostgreSQL
- **自动化**：uiautomator2
- **AI**：阿里云 DashScope API（Qwen 系列）
- **部署**：Docker

## 安装与运行
1. 克隆仓库：
   ```bash
   git clone https://github.com/Kamisato520/MultiModelMobileAgent.git
   cd MultiModelMobileAgent
2.安装依赖pip install -r requirements.txt
3.配置环境变量
4.运行后端
    python run.py
贡献
欢迎提交 Issues 或 Pull Requests，共同改进项目！

联系
GitHub: Kamisato520
