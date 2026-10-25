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
    ('Megadyptes'),
    ('Palaeeudyptes');

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

INSERT INTO
    art (title, artist, price_cents, image_path, room_id)
VALUES
    (
        'Macaroni',
        'Sastognuti',
        '941503',
        '/assets/Macaroni Penguin 3.jpg',
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
        'Ellen Rykers',
        '749958',
        '/assets/Royal Penguin 2.jpg',
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
        'Antoine Lamielle',
        '250046',
        '/assets/Northern Rockhopper Penguin 2.jpg',
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
        'Godot13',
        '317348',
        '/assets/Southern Rockhopper Penguin 2.jpg',
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
        'Stewart Armstrong',
        '870389',
        '/assets/Fiordland Crested Penguin 2.jpg',
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
        'Brocken Inaglory',
        '215729',
        '/assets/Snares Penguin 2.jpg',
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
        'Christopher Stephens',
        '582540',
        '/assets/Erect-crested Penguin 2.jpg',
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
        'putneymark',
        '379361',
        '/assets/Galápagos Penguin 2.jpg',
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
        'William Crochot',
        '543887',
        '/assets/Humboldt Penguin 2.jpg',
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
        'Charles J. Sharp',
        '269522',
        '/assets/Magellanic Penguin 2.jpg',
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
        'Salimfadhley',
        '844049',
        '/assets/African Penguin 2.jpg',
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
        'Jason Auch',
        '668387',
        '/assets/Adélie Penguin 2.jpg',
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
        'Gordon Leggett',
        '442801',
        '/assets/Chinstrap Penguin 2.jpg',
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
        'Liam Quinn',
        '250288',
        '/assets/Gentoo Penguin 2.jpg',
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
        'Ben Tubby',
        '684478',
        '/assets/King Penguin 2.jpg',
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
        'Christopher Michel',
        '418212',
        '/assets/Emperor Penguin 2.jpg',
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
        'Calistemon',
        '371044',
        '/assets/Little Penguin 2.jpg',
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
        'Bernard Spragg',
        '873955',
        '/assets/Yellow-eyed Penguin 2.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Megadyptes'
        )
    );

INSERT INTO
    art (title, artist, price_cents, image_path, room_id)
VALUES
    (
        'Erect-crested',
        'John Barkla',
        '919202',
        '/assets/Erect-crested Penguin 3.jpg',
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
        'C00ch',
        '736873',
        '/assets/Erect-crested Penguin 4.jpg',
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
        'John Barkla',
        '548253',
        '/assets/Fiordland Crested Penguin 3.jpg',
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
        'Greg Schechter',
        '852398',
        '/assets/Fiordland Crested Penguin 4.jpg',
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
        'Macaroni',
        'Jerzy Strzelecki',
        '910245',
        '/assets/Macaroni Penguin 4.jpg',
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
        'Macaroni',
        'lwolfartist',
        '313094',
        '/assets/Macaroni Penguin 5.jpg',
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
        'Brian Gratwicke',
        '745718',
        '/assets/Northern Rockhopper Penguin 3.jpg',
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
        'Antoine Lamielle',
        '638790',
        '/assets/Northern Rockhopper Penguin 4.jpg',
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
        'Mark Fraser',
        '301141',
        '/assets/Royal Penguin 3.jpg',
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
        'John Barkla',
        '996954',
        '/assets/Royal Penguin 4.jpg',
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
        'Lin Padgham',
        '188973',
        '/assets/Snares Penguin 3.jpg',
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
        'Julia Palmer',
        '622807',
        '/assets/Snares Penguin 4.jpg',
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
        '808850',
        '/assets/Southern Rockhopper Penguin 3.jpg',
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
        'Stan Shebs',
        '964296',
        '/assets/Southern Rockhopper Penguin 4.jpg',
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
        'African',
        'Sander Spek',
        '787185',
        '/assets/African Penguin 3.jpg',
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
        'Bernard Gagnon',
        '684179',
        '/assets/African Penguin 4.jpg',
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
        'Galápagos',
        'James Preston',
        '890957',
        '/assets/Galápagos Penguin 3.jpg',
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
        'Galápagos',
        'Mike Weston',
        '511683',
        '/assets/Galápagos Penguin 4.jpg',
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
        'William Crochot',
        '281177',
        '/assets/Humboldt Penguin 3.jpg',
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
        'William Crochot',
        '411542',
        '/assets/Humboldt Penguin 4.jpg',
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
        'David',
        '317723',
        '/assets/Magellanic Penguin 3.jpg',
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
        'Diego Delso',
        '560469',
        '/assets/Magellanic Penguin 4.jpg',
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
        'ravas51',
        '169551',
        '/assets/Adélie Penguin 3.jpg',
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
        'Adélie',
        'Virtual-Pano',
        '358689',
        '/assets/Adélie Penguin 4.jpg',
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
        'Christopher Michel',
        '939751',
        '/assets/Chinstrap Penguin 3.jpg',
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
        'Linar Khalitov',
        '659089',
        '/assets/Chinstrap Penguin 4.jpg',
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
        'Jens Bludau',
        '591061',
        '/assets/Gentoo Penguin 3.jpg',
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
        'W. Bulach',
        '787564',
        '/assets/Gentoo Penguin 4.jpg',
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
        'Emperor',
        'Denis Luyten',
        '626077',
        '/assets/Emperor Penguin 3.jpg',
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
        'Denis Luyten',
        '199923',
        '/assets/Emperor Penguin 4.jpg',
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
        'King',
        'Pismire',
        '767319',
        '/assets/King Penguin 3.jpg',
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
        'King',
        'Isiwal',
        '583733',
        '/assets/King Penguin 4.jpg',
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
        'Pelagic',
        '110638',
        '/assets/Little Penguin 3.jpg',
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
        'Little',
        'Calistemon',
        '137741',
        '/assets/Little Penguin 4.jpg',
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
        'Ciell',
        '490385',
        '/assets/Yellow-eyed Penguin 3.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Megadyptes'
        )
    ),
    (
        'Yellow-eyed',
        'Christian Mehlführer',
        '630531',
        '/assets/Yellow-eyed Penguin 4.jpg',
        (
            SELECT
                id
            FROM
                room
            WHERE
                name = 'Megadyptes'
        )
    );
