create table if not exists users (
    user_id uuid primary key, 
    created_at timestamptz not null default now()
);

create table if not exists chats (
    chat_id uuid primary key,
    user_id uuid not null,
    title varchar(255),
    messages jsonb not null default '[]'::jsonb,
    params jsonb not null default '{}'::jsonb,
    affect jsonb not null default '{}'::jsonb,
    persona jsonb,
    last_used timestamptz not null default now(),
    last_compressed timestamptz
);

alter table chats add column if not exists params jsonb not null default '{}'::jsonb;
-- affect_engine: affect 存 AffectState.to_dict(),persona 存 Persona.to_dict()(null 则用预设)
alter table chats add column if not exists affect jsonb not null default '{}'::jsonb;
alter table chats add column if not exists persona jsonb;

create table if not exists archives (
    chat_id uuid primary key, 
    user_id uuid not null, 
    title varchar(255), 
    messages jsonb not null default '[]'::jsonb, 
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
); 