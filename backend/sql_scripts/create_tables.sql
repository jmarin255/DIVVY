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
    created_at timestamp default current_timestamp
);

CREATE TABLE group_memberships (
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
CREATE UNIQUE INDEX one_owner_per_group
ON group_memberships (group_id)
WHERE role = 'owner';
