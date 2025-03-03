#!/bin/bash

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 运行端到端测试
pytest tests/e2e/ -v

# 生成覆盖率报告
pytest --cov=app tests/ --cov-report=html 