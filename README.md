# Get-Beauty
ptt.cc beauty board image downloader written in python 3+

`config.ini` 內的設定跑掉或少行會自動修正  
```
location: 'D:\Beauty' (def) 儲存文件的位置  
threads: 10 (def) 訪問文章的線程數  
temp_page: 0 (def)記憶用，第二次執行時直接從記錄的頁面開始  
end_page: 1200 (def)必須比 temp_page 小，否則報錯，到達頁數後停止爬圖  
```
