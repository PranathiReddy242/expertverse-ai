import sqlite3

def run_migration():
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()

    # Check experts columns
    cursor.execute('PRAGMA table_info(experts)')
    expert_cols = [row[1] for row in cursor.fetchall()]
    print('Existing expert cols:', expert_cols)

    if 'verification_status' not in expert_cols:
        cursor.execute("ALTER TABLE experts ADD COLUMN verification_status TEXT DEFAULT 'pending'")
        print('Added verification_status to experts')
    if 'rejection_reason' not in expert_cols:
        cursor.execute("ALTER TABLE experts ADD COLUMN rejection_reason TEXT")
        print('Added rejection_reason to experts')
    if 'reviewed_at' not in expert_cols:
        cursor.execute("ALTER TABLE experts ADD COLUMN reviewed_at TIMESTAMP")
        print('Added reviewed_at to experts')

    # Check documents columns
    cursor.execute('PRAGMA table_info(documents)')
    doc_cols = [row[1] for row in cursor.fetchall()]
    print('Existing doc cols:', doc_cols)

    if 'status' not in doc_cols:
        cursor.execute("ALTER TABLE documents ADD COLUMN status TEXT DEFAULT 'approved'")
        print('Added status to documents')
    if 'review_notes' not in doc_cols:
        cursor.execute("ALTER TABLE documents ADD COLUMN review_notes TEXT")
        print('Added review_notes to documents')
    if 'reviewed_at' not in doc_cols:
        cursor.execute("ALTER TABLE documents ADD COLUMN reviewed_at TIMESTAMP")
        print('Added reviewed_at to documents')

    conn.commit()
    conn.close()
    print('Safe SQLite migration completed.')

if __name__ == '__main__':
    run_migration()
