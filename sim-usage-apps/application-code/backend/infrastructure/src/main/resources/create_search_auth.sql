-- 検索認可
drop table if exists "search_auth" cascade;

create table "search_auth" (
  "id" serial not null
  , "email_address" character varying(50) not null
  , "section_id" character varying(10) not null
  , "delete_flag" character(1)
  , "create_time" timestamp not null
  , "update_time" timestamp
  , constraint "search_auth_PKC" primary key ("id")
);

alter table "search_auth" add constraint "constraint_search_auth_001"
  unique ("id") ;
  alter table "search_auth"
  add constraint "search_auth_FK1" foreign key ("email_address") references "dl_auth"("email_address");
  
alter table "search_auth"
  add constraint "search_auth_FK2" foreign key ("section_id") references "section_master"("section_id");
  
  
comment on table "search_auth" is '検索認可';
comment on column "search_auth"."id" is 'ID';
comment on column "search_auth"."email_address" is 'メールアドレス';
comment on column "search_auth"."section_id" is '区間ID';
comment on column "search_auth"."delete_flag" is '削除フラグ:0: 未削除;　1:削除';
comment on column "search_auth"."create_time" is 'レコード作成日時';
comment on column "search_auth"."update_time" is 'レコード更新日時';