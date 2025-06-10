## server
框架使用示例

## 启动
### conda 环境
```sh
conda create -n server_py python=3.13 # 创建环境
conda activate server_py # 激活环境
pip install requirements.txt # 安装依赖
python src/server_main.py #  启动服务

# 导出环境
conda list -e > requirements.txt
```
### uv 环境

```sh
uv sync # 创建环境/激活环境/安装依赖
uv run src/server_main.py #  启动服务
```

### 设置 launch.json debug

```sh
# 进入环境
conda activate server_py
# 查看python 路径 
which python # linux
where.exe python # windows
```
路径放在.vscode/launch.json下python

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "server_main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "1666"
      ],
      // "python": "/home/here/D/a_code/server-example/.venv/bin/python",
      "python": ".venv/bin/python",
      "jinja": true,
      "justMyCode": true,
      "env": { "PYTHONPATH": "${workspaceRoot}/src" }
    }
  ]
}

```

### 调试

vscode debug
或
npm activate_env



## 打包配置

```sh
pyinstaller options src/server_main.py
```


server_main.spec
```conf
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\server_main.py'],
    pathex=[],
    binaries=[],
    datas=[('source', 'source')], # 列表，用于指定需要包含的额外文件。每个元素都是一个元组：（文件的源路径, 在打包文件中的路径)
    hiddenimports=['aiosqlite'], # 用于指定一些 PyInstaller 无法自动检测到的模块
    hookspath=[],# python 脚本 hook ，它会在我们的主代码执行之前运行，为我们准备环境。
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,# 若为 True，所有的二进制文件将被排除在 exe 之外，转而被 COLLECT 函数收集
    name='server_main',
    debug=False,# 打包过程中是否打印调试信息？
    bootloader_ignore_signals=False,
    strip=False,# 是否移除所有的符号信息，使打包出的 exe 文件更小
    upx=True, # 是否用 upx 压缩 exe 文件
    console=True, # 若为 True 则在控制台窗口中运行，否则作为后台进程运行
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['source\\img\\ion\\favicon.ico'],
    contents_directory='.',# 生成的所有依赖文件位置
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='code_tm_server_py',
)

```

## 测试
```sh
pytest

# .vscode\settings.json里添加
{
  "python.testing.pytestArgs": [
    "-v",          // 显示详细输出
    "-s",          // 禁用输出捕获（关键！）
    "--log-cli-level=INFO"  //  启用日志输出到控制台
  ]
}
```

## doc
[TODO list](doc/todo.md)