import os
import subprocess
import sys

def install_package(package_name):
    try:
        # 嘗試導入套件，如果成功則已安裝
        __import__(package_name)
        print(f"'{package_name}' 已安裝。")
    except ImportError:
        # 如果未安裝則自動安裝
        print(f"'{package_name}' 未安裝，正在安裝中...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"'{package_name}' 安裝成功！")
        except Exception as e:
            print(f"安裝 '{package_name}' 時發生錯誤：{e}")

def main():
    install_package("flask")
    # 檢查是否安裝成功
    try:
        import flask
        print(f"Flask 安裝完成，版本為：{flask.__version__}")
    except ImportError:
        print("Flask 安裝失敗，請手動檢查問題。")

if __name__ == "__main__":
    main()
