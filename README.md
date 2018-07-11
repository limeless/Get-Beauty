# Get-Beauty
ptt.cc beauty board image downloader written in python 3+
![demo](https://user-images.githubusercontent.com/1501022/42469354-0599bb8e-83ea-11e8-93f0-482455e60cda.png)

## 簡易的流程圖
![SoftPic](https://user-images.githubusercontent.com/1501022/42471919-14733844-83f2-11e8-9074-1e7349eb9586.png)

`config.ini` 內的設定跑掉或少行會自動修正  
```
location: 'D:\\' (def) 
儲存文件的根目錄，下方設置的版面將在目錄下生成目錄 ie 'D:\root\path\Beauty'  

threads: 10 (def) 
訪問文章的線程數  

temp_page: 0 (def)
記憶用，第二次執行時直接從記錄的頁面開始  

end_page: 1200 (def)
必須比 temp_page 小，否則報錯，到達頁數後停止爬圖 

filter: '公告,男,帥哥,鮮肉' 
標題內容排除關鍵字，用半型 ',' 隔開

board: 'Beauty' 
預設版面，順從 https://www.ptt.cc/bbs/{}/ 的網址，限制級 bypass 內置。
```
