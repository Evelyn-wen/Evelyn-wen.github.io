# 在外置硬盘安装 Two-Seller Competition

在旧终端按 `Control + C` 停止服务器。

解压 `casa_oliva_competition_upgrade_v01.zip`，找到 `install_competition.py`。

在原来的 Terminal 依次操作：

```bash
cd "/Volumes/evelynwen/Evelyn-wen.github.io-main/seller-interface-sandbox"
```

输入 `python `（带空格），然后把下载解压的 `install_competition.py` 拖入终端，按回车。

看见 `TWO-SELLER COMPETITION INSTALLED SUCCESSFULLY` 后运行：

```bash
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --reload
```

打开 `http://127.0.0.1:8000/demo`，选择 Two-Seller Competition。

第一次可以这样设定：Casa Oliva Website、Casa Verde Website、两人、USD 75、偏好蘑菇＋芝士＋意面、Buyer Mode 选择 LLM、Seller Agent Mode 选 Mock（此时不使用）。

旧版 Seller Agent 仍然存在，配置 Key 的方法没有变化。不要把 Key 发到聊天里或提交 GitHub。若重开 Terminal，原来的 export 变量可能不再存在，需要安全地重新配置新生成的 Key。
