-- ダウンロード履歴
drop table if exists "dl_history" cascade;

create table "dl_history" (
  "id" serial not null
  , "uuid" character(36) not null
  , "data_division" character(1) not null
  , "dl_date_time" timestamp not null
  , "email_address" character varying(50) not null
  , "delete_flag" character(1)
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "dl_history_PKC" primary key ("id")
);

create index "idx_dl_history_001"
  on "dl_history"("dl_date_time");

create index "idx_dl_history_002"
  on "dl_history"("email_address");

alter table "dl_history" add constraint "constraint_dl_history_001"
  unique ("id") ;

create index "idx_dl_history_003"
  on "dl_history"("uuid");
  
alter table "dl_history"
  add constraint "dl_history_FK1" foreign key ("uuid") references "scenario_info"("uuid");
  
comment on table "dl_history" is 'ダウンロード履歴';
comment on column "dl_history"."id" is 'ID';
comment on column "dl_history"."uuid" is 'UUID';
comment on column "dl_history"."data_division" is 'データ区分:0:OpenDRIVE(xodr); 1:車両軌跡データ(csv);
2:SDMGシナリオ(xlm); 3:OpenSCENARIO (xosc);
4:機械学習(jpg)';
comment on column "dl_history"."dl_date_time" is 'DL日時';
comment on column "dl_history"."email_address" is 'メールアドレス';
comment on column "dl_history"."delete_flag" is '削除フラグ';
comment on column "dl_history"."create_time" is 'レコード作成日時';
comment on column "dl_history"."update_time" is 'レコード更新日時';