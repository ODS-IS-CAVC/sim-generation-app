# バックエンドアプリ

## 1.環境前提

| 主なライブラリ | バージョン |
|----------------|------------|
| Java           | 21         |
| Spring Boot    | 3.3.0      |
| AWS SDK for Java | 2.x        |
| PostgreSQL     | 16.3        |

## 2.設定のカスタマイズ
[**application.properties**](./web/src/main/resources/) の設定ファイルを環境に合わせて修正してください。

## 3.利用方法

### コンパイル・起動
```sh
gradle web:bootRun -Dprofile={local | dev | stg | prd}
```
### ビルド
```sh
gradle web:build -Dprofile={local | dev | stg | prd}
```