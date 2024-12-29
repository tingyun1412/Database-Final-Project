import subprocess
import os
import time
import webbrowser


def run_favlist_script():
    """執行 favList_into_csv.py 並檢查結果"""
    print("正在執行 favList_into_csv.py...")
    subprocess.run(['python', 'favList_into_csv.py'], text=True, encoding='utf-8')
    time.sleep(10)
    # 檢查 playlist.csv 是否生成
    if os.path.exists('playlist.csv'):
        print("成功生成 playlist.csv！")
        return True
    else:
        print("錯誤：未生成 playlist.csv，請檢查 favList_into_csv.py 是否正確運行。")
        return False

def run_interface_script():
    """啟動 interface.py"""
    print("正在啟動 interface.py...")
    try:
        subprocess.Popen(['python', 'interface.py'], text=True, encoding='utf-8')
        # 自動打開 interface.py 的頁面
        time.sleep(5)
        webbrowser.open("http://127.0.0.1:8888")
        print("interface.py 已啟動，請在瀏覽器中查看！")
    except Exception as e:
        print(f"啟動 interface.py 時發生錯誤：{e}")

def main():
    # Step 1: 執行 favList_into_csv.py 並檢查是否成功
    if run_favlist_script():
        # Step 2: 如果成功生成 playlist.csv，啟動 interface.py
        run_interface_script()
    else:
        print("流程中止。")

if __name__ == '__main__':
    main()
