# PetCare DevOps 指南

## 📋 目录

- [概述](#概述)
- [基础设施](#基础设施)
- [CI/CD 流程](#cicd-流程)
- [自动备份](#自动备份)
- [健康监控](#健康监控)
- [一键回滚](#一键回滚)
- [告警通知](#告警通知)
- [故障排查](#故障排查)

## 概述

PetCare 采用轻量级 DevOps 方案，核心特性：

- ✅ **GitHub Actions CI/CD** - 推送 main 分支自动部署
- ✅ **自动备份** - 每日凌晨备份数据库，保留7天
- ✅ **健康监控** - 每小时检查服务状态，异常时告警
- ✅ **一键回滚** - 快速恢复到任意历史版本
- ✅ **微信告警** - 服务异常时自动通知

## 基础设施

### 服务器配置
- **服务器**: 单台阿里云 ECS
- **域名**: petcare.yjyblog.xyz
- **SSL**: Let's Encrypt 自动证书
- **反向代理**: Nginx + HTTP/2 + HTTP/3

### 服务架构
```
用户 → Nginx (443) → PetCare Backend (8000)
                  → 静态资源 (frontend/dist)
```

### 目录结构
```
/root/workspace/petcare/
├── .github/workflows/    # CI/CD 配置
├── scripts/              # 运维脚本
│   ├── backup.sh         # 数据库备份
│   ├── health-check.sh   # 健康检查
│   ├── rollback.sh       # 一键回滚
│   └── sync-deploy.sh    # 手动同步
├── backend/              # FastAPI 后端
├── frontend/             # React 前端
└── logs/                 # 应用日志
```

## CI/CD 流程

### GitHub Actions 工作流

**触发条件**:
- 推送到 `main` 分支
- 手动触发 (`workflow_dispatch`)

**流程**:
```
1. 代码检查 (Lint)
   ├─ 前端: ESLint
   └─ 后端: Ruff

2. 构建测试
   ├─ 前端: npm run build
   └─ 后端: pytest (如有)

3. 部署到生产
   ├─ SSH 到服务器
   ├─ git pull
   ├─ npm run build (前端)
   ├─ systemctl restart petcare
   └─ 健康检查
```

### 需要配置的 GitHub Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions 添加：

| Secret 名称 | 说明 |
|------------|------|
| `SSH_PRIVATE_KEY` | 服务器 SSH 私钥 |
| `SERVER_HOST` | 服务器 IP 或域名 |
| `SERVER_USER` | SSH 用户名（通常是 root） |

**生成 SSH 密钥**:
```bash
# 在本地生成
ssh-keygen -t ed25519 -C "petcare-deploy"
# 将公钥添加到服务器的 ~/.ssh/authorized_keys
```

## 自动备份

### 备份策略
- **频率**: 每日凌晨 2:00
- **保留时间**: 7天
- **存储位置**: `/root/backups/petcare/`
- **压缩**: gzip 压缩

### 手动备份
```bash
cd /root/workspace/petcare
./scripts/backup.sh
```

### 恢复备份
```bash
# 1. 停止服务
sudo systemctl stop petcare.service

# 2. 解压备份
gunzip /root/backups/petcare/petcare_20240101_020000.db.gz

# 3. 恢复数据库
cp /root/backups/petcare/petcare_20240101_020000.db \
   /root/workspace/petcare/backend/petcare.db

# 4. 重启服务
sudo systemctl start petcare.service
```

## 健康监控

### 监控项目
- ✅ systemd 服务状态
- ✅ API 响应时间
- ✅ 数据库连接
- ✅ 磁盘使用率

### 手动检查
```bash
cd /root/workspace/petcare
./scripts/health-check.sh
```

### 告警阈值
- 连续失败 **3次** 触发微信告警
- 状态文件: `/tmp/petcare_health_state`

## 一键回滚

### 使用方法
```bash
cd /root/workspace/petcare

# 查看最近的提交
git log --oneline -10

# 回滚到指定提交
./scripts/rollback.sh abc1234
```

### 回滚流程
```
1. 备份当前状态
2. git checkout <commit>
3. npm install && npm run build
4. systemctl restart petcare
5. 健康检查
```

## 告警通知

### 当前告警渠道
- ✅ 微信通知（通过 Hermes Agent）

### 告警场景
- 🔴 服务连续失败 3 次
- 🔴 磁盘使用率 > 90%
- 🔴 数据库连接失败
- 🟡 API 响应超时

### 配置微信告警

健康检查脚本已集成告警逻辑，当检测到异常时会自动发送到你的微信。

## 故障排查

### 服务无法启动
```bash
# 查看日志
sudo journalctl -u petcare.service -n 50

# 常见原因
# 1. 端口被占用
lsof -i :8000

# 2. Python 依赖缺失
cd /root/workspace/petcare/backend
./venv/bin/pip install -r requirements.txt
```

### 前端构建失败
```bash
# 清理缓存
cd /root/workspace/petcare/frontend
rm -rf node_modules package-lock.json

# 重新安装
npm install
npm run build
```

### 数据库锁定
```bash
# 检查是否有进程占用
lsof /root/workspace/petcare/backend/petcare.db

# 强制释放（谨慎使用）
fuser -k /root/workspace/petcare/backend/petcare.db
```

### Nginx 502/504
```bash
# 检查后端服务
systemctl status petcare.service

# 检查 Nginx 日志
tail -f /var/log/nginx/error.log

# 重启服务
sudo systemctl restart petcare.service
sudo systemctl restart nginx
```

## 定时任务

当前已配置的 cron 任务：

```bash
# 查看当前 cron 任务
crontab -l

# PetCare 定时任务
# 每2小时自动同步部署
0 */2 * * * cd /root/workspace/petcare && ./scripts/sync-deploy.sh >> /var/log/petcare-sync.log 2>&1

# 每日凌晨2点备份数据库
0 2 * * * cd /root/workspace/petcare && ./scripts/backup.sh >> /var/log/petcare-backup.log 2>&1

# 每小时健康检查
0 * * * * cd /root/workspace/petcare && ./scripts/health-check.sh >> /var/log/petcare-health.log 2>&1
```

## 最佳实践

### 1. 部署前测试
```bash
# 本地构建测试
cd /root/workspace/petcare/frontend
npm run build

# 后端语法检查
cd /root/workspace/petcare/backend
./venv/bin/python -m py_compile app/main.py
```

### 2. 回滚策略
- 发现问题立即回滚，不要尝试热修复
- 回滚后检查日志确认问题
- 修复后重新走 CI/CD 流程

### 3. 日志管理
```bash
# 查看应用日志
tail -f /root/workspace/petcare/logs/app.log

# 查看系统日志
sudo journalctl -u petcare.service -f

# 查看 Nginx 访问日志
tail -f /var/log/nginx/access.log
```

### 4. 性能监控
```bash
# 查看实时资源使用
htop

# 查看磁盘使用
df -h

# 查看数据库大小
ls -lh /root/workspace/petcare/backend/petcare.db
```

## 扩展建议

### 短期（1-2周）
- [ ] 添加前端构建体积监控
- [ ] 集成错误追踪（Sentry）
- [ ] 添加 API 性能监控

### 中期（1-2月）
- [ ] 引入 Redis 缓存热点数据
- [ ] 添加单元测试覆盖
- [ ] 实现蓝绿部署

### 长期（3-6月）
- [ ] 容器化部署（Docker + Docker Compose）
- [ ] 引入 Prometheus + Grafana 监控
- [ ] 实现自动扩缩容

---

**最后更新**: 2026-01-21  
**维护者**: PetCare DevOps Team
