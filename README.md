# flask_learning_journal_v3
This project objectives:

- Model class for adding and editing tags
- Journal entries show tags.
- Selecting tag takes you to a list of specific tags.
- Details pages shows tags
- Add/Edit page password protected
- Add/Edit includes tags
- Ability to delete an entry
- Each section of the journal entry uses the correct CSS from the supplied file: Entry itself, Title, Date, Time Spent, What You Learned, Resources to Remember
- Routing uses slugs instead of IDs:

/entries/{slug}
/entries/{slug}/edit
/entries/{slug}/delete
NOTE: This means a slug must be unique to identify a single entry as an ID does. Two entries cannot share the same slug.

To manage data i used peewee ORM and SQLite database
