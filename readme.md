# Group7 Topic4
# SQL DDL Generator

* A0119392B Huang Weilong (Main framework and integration)
* A0113594E Li Mengying  (ddl generator)
* A0105508M Xu Gelin  (bcnf)

# Specification
* Runnable SQL DDL statements
* Multiple Database Support
* Auto table merging
* Smart type filling and keywords violation detection
* Name conflicts solver
* User Confirmation
* Normal form detection and BCNF validation(beta)

# Merging Mechanism

- Weak Entity Relationship (merged automatically)
    - weak entity becomes a relation 
    - the primary key of the weak entity will become the primary key of the schema
    - the relation schema contains the weak entity's properties and the key of the strong entity
    - weak relationship disappears, the relationship's properties become attribute of the relation's schema
- Recursive Relationship (merged automatically)
    - if the cardinality of the relationship if 1-many or 1-1, then a second attribute of the same domain as the key
    may be added to the entity relation to establish the relationship. Attributes of the relationship can also be added
    to the entity relation
    - for many-many recursive relationships, we create one relation including the attributes of the relation but with
    the primary keys of the entity included twice, one for each role (husband and wife)
- N-ary Relationship (Merged automatically)
    - create a relation to represent the relationship
    - include primary keys of all participating entities as foreign keys 
    - primary key is the combination of all the foreign keys
- binary 1:1 relationship (merged using ALTER TABLE statement)
    - if there is total participation (min_participation is 1, max_participation is 1), 
    merge the total participation entity with the relationship
    - include primary of the other entity as foreign key
    - include all attributes of the relationship into the merged table
- one-to-many relationship (merged using ALTER TABLE statement)
   - relationship is merged into the entity at the "many" side
   - include the primary key of the "one" side to the merged table as foreign keys
   - attributes of the relationship are also included in the merged table






# Dependencies
* Django 1.10


# Installation
To run the server:

    python manage.py migrate
    python manage.py runserver 0.0.0.0:8888

Now please check your site at http://localhost:8888/ddl

To get test cases:
    `unzip demo.zip`
Those templates should be enough for demo all functions.

# How to contribute
* BCNF is still in development
* Please create your own branch and commit the code, thanks.
