-- シナリオ情報
drop table if exists "scenario_info" cascade;

create table "scenario_info" (
  "id" serial not null
  , "uuid" character(36) not null
  , "location_id" character varying(10) not null
  , "longitude" character varying(10) not null
  , "latitude" character varying(10) not null
  , "scenario_create_time" timestamp not null
  , "delete_flag" character
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "scenario_info_PKC" primary key ("id")
);

alter table "scenario_info" add constraint "constraint_scenario_info_001"
  unique ("uuid") ;

create index "idx_scenario_info_001"
  on "scenario_info"("location_id");
  
alter table "scenario_info"
  add constraint "scenario_info_FK1" foreign key ("location_id") references "location_master"("location_id");
  
comment on table "scenario_info" is 'シナリオ情報';
comment on column "scenario_info"."id" is 'ID';
comment on column "scenario_info"."uuid" is 'UUID';
comment on column "scenario_info"."location_id" is '場所ID';
comment on column "scenario_info"."longitude" is '経度';
comment on column "scenario_info"."latitude" is '緯度';
comment on column "scenario_info"."scenario_create_time" is 'シナリオ作成日時';
comment on column "scenario_info"."delete_flag" is '削除フラグ:0: 未削除;　1:削除';
comment on column "scenario_info"."create_time" is 'レコード作成日時';
comment on column "scenario_info"."update_time" is 'レコード更新日時';