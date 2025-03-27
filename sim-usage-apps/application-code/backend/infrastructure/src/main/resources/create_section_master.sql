-- 区間マスタ
drop table if exists "section_master" cascade;

create table "section_master" (
  "section_id" character varying(10) not null
  , "section_name" character varying(300) not null
  , "delete_flag" character(1)
  , "remarks" character varying(256)
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "section_master_PKC" primary key ("section_id")
);

comment on table "section_master" is '区間マスタ';
comment on column "section_master"."section_id" is '区間ID';
comment on column "section_master"."section_name" is '区間名:最大入力100文字';
comment on column "section_master"."delete_flag" is '削除フラグ:0: 未削除;　1:削除';
comment on column "section_master"."remarks" is '備考';
comment on column "section_master"."create_time" is 'レコード作成日時';
comment on column "section_master"."update_time" is 'レコード更新日時';