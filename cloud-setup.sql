-- Kengūros treniruoklis – parent accounts (Supabase). Run once in the
-- project's SQL Editor. Safe to run again.
--
-- Model: a parent is a Supabase auth user (e-mail + password). Children
-- have no login: each child is one row in public.kids owned by the parent,
-- holding the app's saved progress (the same JSON as the browser copy).

create table if not exists public.kids (
  id         uuid primary key default gen_random_uuid(),
  parent     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  name       text not null check (char_length(name) between 1 and 24),
  store      jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint kids_store_size check (store is null or pg_column_size(store) < 2000000)
);
create index if not exists kids_parent_idx on public.kids(parent);

-- Every parent sees and changes only their own children.
alter table public.kids enable row level security;
drop policy if exists kids_select on public.kids;
drop policy if exists kids_insert on public.kids;
drop policy if exists kids_update on public.kids;
drop policy if exists kids_delete on public.kids;
create policy kids_select on public.kids for select to authenticated using (parent = auth.uid());
create policy kids_insert on public.kids for insert to authenticated with check (parent = auth.uid());
create policy kids_update on public.kids for update to authenticated using (parent = auth.uid()) with check (parent = auth.uid());
create policy kids_delete on public.kids for delete to authenticated using (parent = auth.uid());

-- updated_at is the sync version: set by the database on every change, so
-- the app can tell whether another device wrote since its last sync.
create or replace function public.kids_touch() returns trigger
language plpgsql as $$
begin
  new.updated_at := clock_timestamp();
  return new;
end $$;
drop trigger if exists kids_touch on public.kids;
create trigger kids_touch before update on public.kids
  for each row execute function public.kids_touch();

-- At most 8 children per parent account.
create or replace function public.kids_limit() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.kids where parent = new.parent) >= 8 then
    raise exception 'too many children for one account';
  end if;
  return new;
end $$;
drop trigger if exists kids_limit on public.kids;
create trigger kids_limit before insert on public.kids
  for each row execute function public.kids_limit();

-- "Ištrinti paskyrą": a parent deletes their own account; the children's
-- rows go with it (on delete cascade).
create or replace function public.delete_my_account() returns void
language sql security definer set search_path = public as $$
  delete from auth.users where id = auth.uid();
$$;
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;

-- Signed-in parents reach the table through the API (rows still filtered by the policies).
revoke all on public.kids from anon;
grant select, insert, update, delete on public.kids to authenticated;
