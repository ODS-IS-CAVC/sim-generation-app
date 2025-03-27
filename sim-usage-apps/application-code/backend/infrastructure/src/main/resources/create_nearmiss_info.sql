-- ヒヤリハット情報
drop table if exists "nearmiss_info" cascade;

create table "nearmiss_info" (
  "id" serial not null
  , "uuid" character(36) not null
  , "nearmiss_type" character varying(10) not null
  , "delete_flag" character(1)
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "nearmiss_info_PKC" primary key ("id")
);

create index "idx_nearmiss_info_001"
  on "nearmiss_info"("nearmiss_type");
  
alter table "nearmiss_info"
  add constraint "nearmiss_info_FK1" foreign key ("uuid") references "scenario_info"("uuid");
  
comment on table "nearmiss_info" is 'ヒヤリハット情報';
comment on column "nearmiss_info"."id" is 'ID';
comment on column "nearmiss_info"."uuid" is 'UUID';
comment on column "nearmiss_info"."nearmiss_type" is 'ヒヤリハット種別';
comment on column "nearmiss_info"."delete_flag" is '削除フラグ:0: 未削除;　1:削除';
comment on column "nearmiss_info"."create_time" is 'レコード作成日時';
comment on column "nearmiss_info"."update_time" is 'レコード更新日時';