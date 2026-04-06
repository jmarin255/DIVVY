-- postgres create tables
create table if not exists users (
    id serial primary key,
    first_name varchar(100) not null,
    last_name varchar(100) not null,
    email varchar(255) not null unique,
    phone varchar(20) unique,
    password_hash text not null,
    created_at timestamp default current_timestamp
);

create table if not exists groups (
    id serial primary key,
    name varchar(255) not null,
    join_code varchar(5) not null unique,
    created_at timestamp default current_timestamp
);

CREATE TABLE if not exists group_memberships (
    id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,

    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'member')),

    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_group
        FOREIGN KEY (group_id)
        REFERENCES groups(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_membership
        UNIQUE (user_id, group_id)
);
CREATE UNIQUE INDEX if not exists one_owner_per_group
ON group_memberships (group_id)
WHERE role = 'owner';

CREATE TABLE IF NOT EXISTS refresh_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_refresh_session_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

create table if not exists categories (
    id serial primary key,
    name varchar(50) not null,
    group_id integer not null,
    created_at timestamp default current_timestamp,
    CONSTRAINT fk_category_group
        FOREIGN KEY (group_id)
        REFERENCES groups(id)
        ON DELETE CASCADE,
    CONSTRAINT unique_category_name_per_group
        UNIQUE (name, group_id)
);

create table if not exists expenses (
    id serial primary key,
    group_id integer not null,
    created_by integer not null,
    total_amount numeric(10, 2) not null,
    description text,
    created_at timestamp default current_timestamp,
    category_id integer,
    CONSTRAINT fk_expense_group
        FOREIGN KEY (group_id)
        REFERENCES groups(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_expense_user
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_expense_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE SET NULL,
    CONSTRAINT check_total_amount
        CHECK (total_amount >= 0),
    CONSTRAINT check_description_length
        CHECK (char_length(description) <= 500)
);

create table if not exists expense_splits(
    id serial primary key,
    expense_id integer not null,
    user_id integer not null,
    amount numeric(10, 2) not null,
    created_at timestamp default current_timestamp,
    CONSTRAINT fk_expense_split_expense
        FOREIGN KEY (expense_id)
        REFERENCES expenses(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_expense_split_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT check_amount
        CHECK (amount >= 0)
);

CREATE INDEX IF NOT EXISTS idx_refresh_sessions_user_id ON refresh_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_sessions_expires_at ON refresh_sessions (expires_at);
create index if not exists idx_expenses_group_id on expenses (group_id);
