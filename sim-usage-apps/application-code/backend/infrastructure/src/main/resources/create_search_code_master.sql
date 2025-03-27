-- 検索条件コード値マスタ
drop table if exists "search_code_master" cascade;

create table "search_code_master" (
  "id" serial not null
  , "type" hstore not null
  , "choice" hstore not null
  , "delete_flag" character(1)
  , "remarks" character varying(256)
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "search_code_master_PKC" primary key ("id")
);

alter table "search_code_master" add constraint "constraint_search_code_master_001"
  unique ("id") ;
  
comment on table "search_code_master" is '検索条件コード値マスタ';
comment on column "search_code_master"."id" is 'ID';
comment on column "search_code_master"."type" is '種類';
comment on column "search_code_master"."choice" is '選択肢';
comment on column "search_code_master"."delete_flag" is '削除フラグ:0: 未削除;　1:削除';
comment on column "search_code_master"."remarks" is '備考';
comment on column "search_code_master"."create_time" is 'レコード作成日時';
comment on column "search_code_master"."update_time" is 'レコード更新日時';