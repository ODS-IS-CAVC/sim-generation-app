-- ダウンロード認可
drop table if exists "dl_auth" cascade;

create table "dl_auth" (
  "id" serial not null
  , "email_address" character varying(50) not null
  , "scenario_possibility_flag" character(1) not null
  , "ml_possibility_flag" character(1) not null
  , "delete_flag" character(1)
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "dl_auth_PKC" primary key ("id")
);

alter table "dl_auth" add constraint "constraint_dl_auth_001"
  unique ("id") ;
  
create unique index "constraint_dl_auth_002"
  on "dl_auth"("email_address");
  
  
comment on table "dl_auth" is 'ダウンロード認可';
comment on column "dl_auth"."id" is 'ID';
comment on column "dl_auth"."email_address" is 'メールアドレス';
comment on column "dl_auth"."scenario_possibility_flag" is 'シナリオ可否フラグ:0: ダウンロード可;　1ダウンロード不可';
comment on column "dl_auth"."ml_possibility_flag" is '機械学習可否フラグ:0: ダウンロード可;　1ダウンロード不可';
comment on column "dl_auth"."delete_flag" is '削除フラグ:0: 未削除;　1:削除';
comment on column "dl_auth"."create_time" is 'レコード作成日時';
comment on column "dl_auth"."update_time" is 'レコード更新日時';