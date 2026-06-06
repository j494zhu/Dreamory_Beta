create table if not exists users (
    user_id uuid primary key, 
    created_at timestamptz not null default now()
);

create table if not exists chats (
    chat_id uuid primary key, 
    user_id uuid not null, 
    title varchar(255), 
    messages jsonb not null default '[]'::jsonb, 
    last_used timestamptz not null default now(),
    last_compressed timestamptz
); 

create table if not exists archives (
    chat_id uuid primary key, 
    user_id uuid not null, 
    title varchar(255), 
    messages jsonb not null default '[]'::jsonb, 
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
); 