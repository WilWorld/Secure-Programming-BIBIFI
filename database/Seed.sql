INSERT INTO
    users (username, password_hash, role)
VALUES
    (
        'guest1',
        '$argon2id$v=19$m=65536,t=3,p=4$05FdtU/GHRvpxKN9jsHC2g$rc288NGmP8In4UTpPMIKLXyDcMl7kSfQrEk8pVts9EY',
        'guest'
    ),
    (
        'employee1',
        '$argon2id$v=19$m=65536,t=3,p=4$HkN/Y9ZcVzODARS3P+tp1g$xihWX/DDSVVsgqKAJl1krlnLk2bBdqnPIKDWI+wV3qQ',
        'employee'
    ),
    (
        'administrator1',
        '$argon2id$v=19$m=65536,t=3,p=4$/LlBD61uOK9TrRAN59I2ow$9YqlCm0ALdV6zLLBbefICdZi+PKyn2PyHCoqfHDbWj0',
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