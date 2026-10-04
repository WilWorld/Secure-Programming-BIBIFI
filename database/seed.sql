-- Dev-only credentials. These passwords are intentionally weak and public so
-- each teammate can sign in locally. Never reuse them anywhere real.
--   guest1 / GuestPass1
--   employee1 / EmployeePass1
--   administrator1 / AdminPass1
INSERT INTO
    users (username, password_hash, role)
VALUES
    (
        'guest1',
        '$argon2id$v=19$m=65536,t=3,p=4$aRPJFjcSWrryzbvhctMlkw$yYxasdwY2YyGsK7X84Ja14E8TKGq5/nHNeaxuoU8mWE',
        'guest'
    ),
    (
        'employee1',
        '$argon2id$v=19$m=65536,t=3,p=4$dz0/paeIxPWFs/ew5YASNw$V7OegTJr3+1oVg3Gi4BJPKZr9wU/L76juNkCj4fPMEE',
        'employee'
    ),
    (
        'administrator1',
        '$argon2id$v=19$m=65536,t=3,p=4$n3YxWFRmeElpBULvkzw8jQ$IMsryhbZI8mI0ACGuAIZ8Jzef+kjb01R6wxPTRthtnw',
        'administrator'
    );

-- The room names are the different genuses of penguins
INSERT INTO
    room (name)
VALUES
    ('Eudyptes'),
    ('Spheniscus'),
    ('Pygoscelis'),
    ('Aptenodytes'),
    ('Eudyptula'),
    ('Megadyptes');

INSERT INTO
    art (title, artist, price_cents, image_path, room_id)
VALUES
    (
        'Macaroni',
        'Andrew Shiva',
        '1000000',
        '/assets/Macaroni Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptes'
        )
    ),
    (
        'Royal',
        'M. Murphy',
        '1000000',
        '/assets/Royal Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptes'
        )
    ),
    (
        'Northern Rockhopper',
        'Arjan Haverkamp',
        '1000000',
        '/assets/Northern Rockhopper Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptes'
        )
    ),
    (
        'Southern Rockhopper',
        'Liam Quinn',
        '1000000',
        '/assets/Southern Rockhopper Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptes'
        )
    ),
    (
        'Fiordland Crested',
        'travelwayoflife',
        '1000000',
        '/assets/Fiordland Crested Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptes'
        )
    ),
    (
        'Snares',
        'Christopher Stephens',
        '1000000',
        '/assets/Snares Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptes'
        )
    ),
    (
        'Erect-crested',
        'N/A',
        '1000000',
        '/assets/Erect-crested Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptes'
        )
    ),
    (
        'Galápagos',
        'Charles J. Sharp',
        '1000000',
        '/assets/Galápagos Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Spheniscus'
        )
    ),
    (
        'Humboldt',
        'Chrisoph Moning',
        '1000000',
        '/assets/Humboldt Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Spheniscus'
        )
    ),
    (
        'Magellanic',
        'Polinova',
        '1000000',
        '/assets/Magellanic Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Spheniscus'
        )
    ),
    (
        'African',
        'Matii Blume',
        '1000000',
        '/assets/African Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Spheniscus'
        )
    ),
    (
        'Adélie',
        'Andrew Shiva',
        '1000000',
        '/assets/Adélie Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Pygoscelis'
        )
    ),
    (
        'Chinstrap',
        'Andrew Shiva',
        '1000000',
        '/assets/Chinstrap Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Pygoscelis'
        )
    ),
    (
        'Gentoo',
        'Andrew Shiva',
        '1000000',
        '/assets/Gentoo Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Pygoscelis'
        )
    ),
    (
        'King',
        'Andrew Shiva',
        '1000000',
        '/assets/King Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Aptenodytes'
        )
    ),
    (
        'Emperor',
        'Ian Duffy',
        '1000000',
        '/assets/Emperor Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Aptenodytes'
        )
    ),
    (
        'Little',
        'JJ Harrison',
        '1000000',
        '/assets/Little Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Eudyptula'
        )
    ),
    (
        'Yellow-eyed',
        'Christian Mehlfüher',
        '1000000',
        '/assets/Yellow-eyed Penguin.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Megadyptes'
        )
    );