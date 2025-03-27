-- 場所マスタ
drop table if exists "location_master" cascade;

create table "location_master" (
  "id" serial not null
  , "location_id" character varying(10) not null
  , "location_name" character varying(300) not null
  , "section_id" character varying(10) not null
  , "delete_flag" character(1)
  , "remarks" character varying(256)
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "location_master_PKC" primary key ("id")
);

alter table "location_master" add constraint "constraint_location_master_001"
  unique ("location_id") ;
  
alter table "location_master"
  add constraint "location_master_FK1" foreign key ("section_id") references "section_master"("section_id");
  
comment on table "location_master" is '場所マスタ';
comment on column "location_master"."id" is 'ID';
comment on column "location_master"."location_id" is '場所ID';
comment on column "location_master"."location_name" is '場所名:最大入力100文字';
comment on column "location_master"."section_id" is '区間ID';
comment on column "location_master"."delete_flag" is '削除フラグ:0: 未削除;　1:削除';
comment on column "location_master"."remarks" is '備考';
comment on column "location_master"."create_time" is 'レコード作成日時';
comment on column "location_master"."update_time" is 'レコード更新日時';