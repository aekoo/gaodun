### 构建步骤

1. 安装 `python3` 和 `pip`

2. 安装依赖（下面操作都在 app 目录下面执行）

   ```bash
   pip install -r requirements.txt
   ```

3. 安装打包工具

   ```bash
   pip install pyinstaller
   ```

4. 构建可执行文件

   ```bash
   pyinstaller -F app.py
   ```

   成功之后即可在当前的 dist目录下找到可执行文件