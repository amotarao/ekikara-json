# ekikara-json
えきから時刻表の時刻表をjson形式に変換して表示させる。

## 注意事項
- えきから時刻表及び運営会社は無関係です。
- このツールを使用することで発生したトラブルや損失、損害に対して一切責任を負いません。
- このツールを使用することで得たデータは、公開しないようお願いします。

## Run Program
```
source env/bin/activate
make dev
deactivate
```

## Example

### Station
```
http://www.ekikara.jp/newdata/ekijikoku/1301361/down1_14101011.htm
↓
http://localhost:3000/station/1301361/down1_14101011
```

### Line
```
http://www.ekikara.jp/newdata/line/1212011/down1_1.htm
↓
http://localhost:3000/line/1212011/down1_1
```
