# Get-Beauty
ptt.cc beauty board image downloader written in python 3+
![demo](https://user-images.githubusercontent.com/1501022/42469354-0599bb8e-83ea-11e8-93f0-482455e60cda.png)

## 簡易的流程圖
![SoftPic](https://user-images.githubusercontent.com/1501022/42471919-14733844-83f2-11e8-9074-1e7349eb9586.png)

`config.ini` 內的設定跑掉或少行會自動修正  
```
location: 'D:\Beauty' (def) 儲存文件的位置  
threads: 10 (def) 訪問文章的線程數  
temp_page: 0 (def)記憶用，第二次執行時直接從記錄的頁面開始  
end_page: 1200 (def)必須比 temp_page 小，否則報錯，到達頁數後停止爬圖  
```
