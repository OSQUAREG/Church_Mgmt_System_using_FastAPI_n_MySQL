from typing import Annotated
from fastapi import Depends  # type: ignore
from sqlalchemy import create_engine, text, inspect  # type: ignore
from sqlalchemy.orm import sessionmaker, Session  # type: ignore

from .config import settings

host = settings.host
port = settings.port
user = settings.user
password = settings.password
database = settings.database

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{user}:{str(password)}@{host}:{port}/{database}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Connecting to the Database
def get_db() -> Session:
    db = SessionLocal()
    print("Database connection was successful!")
    try:
        yield db
    finally:
        db.close()
        print("Database connection closed.")


# Automating Trigger Creation for Audit Logs
EXEMPT_COLUMNS = {
    "Created_Date",
    "Created_By",
    "Modified_Date",
    "Modified_By",
    "Status_Date",
    "Status_By",
}

EXEMPT_TABLES = {"tblAuditLog", "tblCodeSequence"}


# Get Columns
def get_columns(db, table_name):
    columns = db.execute(text(f"SHOW COLUMNS FROM {table_name}")).all()
    return [column[0] for column in columns]


# Drop Triggers if they exist
def drop_trigger(db, trigger_name):
    db.execute(text(f"DROP TRIGGER IF EXISTS {trigger_name};"))


def create_concat_statement(prefix, columns):
    concat_parts = []
    for column in columns:
        # concat_parts.append(f"'{column}: ', IFNULL({prefix}.{column}, 'null')")
        concat_parts.append(
            f"""
            '"{column}": ', '"',IFNULL({prefix}.{column}, 'null'),'"'
            """
        )
    return "CONCAT('{', " + ", ', ', ".join(concat_parts) + ", '}')"


# Create Insert Triggers
def create_insert_trigger(table_name, columns):
    new_data_concat = create_concat_statement("NEW", columns)
    return f"""
    CREATE TRIGGER log_{table_name}_after_insert
    AFTER INSERT ON {table_name}
    FOR EACH ROW
    BEGIN
        DECLARE log_user VARCHAR(255);
        DECLARE user_type VARCHAR(20);
        DECLARE new_data_concat TEXT;
        
        IF @current_user IS NOT NULL THEN
            SET log_user = @current_user;
            SET user_type = 'APP USER';
        ELSE
            SET log_user = CURRENT_USER();
            SET user_type = 'DB USER';
        END IF;
        
        SET new_data_concat = {new_data_concat};
        
        INSERT INTO tblAuditLog (Table_Name, Row_Id, Log_Type, Log_By, New_Data, User_Type)
        VALUES ('{table_name}', NEW.Id, 'CREATE', log_user, new_data_concat, user_type);
    END;
    """


# Create Update Triggers
def create_update_trigger(table_name, columns):
    trigger = f"""
    CREATE TRIGGER log_{table_name}_after_update
    AFTER UPDATE ON {table_name}
    FOR EACH ROW
    BEGIN
        DECLARE log_user VARCHAR(255);
        DECLARE user_type VARCHAR(20);
        IF @current_user IS NOT NULL THEN
            SET log_user = @current_user;
            SET user_type = 'APP USER';
        ELSE
            SET log_user = CURRENT_USER();
            SET user_type = 'DB USER';
        END IF;
    """
    for column in columns:
        if column in EXEMPT_COLUMNS:
            continue
        trigger += f"""
        IF OLD.{column} != NEW.{column} THEN
            INSERT INTO tblAuditLog (Table_Name, Column_Name, Row_Id, Log_Type, Log_By, Old_Data, New_Data, User_Type)
            VALUES ('{table_name}', '{column}', NEW.Id, 'UPDATE', log_user, OLD.{column}, NEW.{column}, user_type);
        END IF;
        """
    trigger += "END;"
    return trigger


def create_delete_trigger(table_name, columns):
    old_data_concat = create_concat_statement("OLD", columns)
    return f"""
    CREATE TRIGGER log_{table_name}_after_delete
    AFTER DELETE ON {table_name}
    FOR EACH ROW
    BEGIN
        DECLARE log_user VARCHAR(255);
        DECLARE user_type VARCHAR(20);
        DECLARE old_data_concat TEXT;
        
        IF @current_user IS NOT NULL THEN
            SET log_user = @current_user;
            SET user_type = 'APP USER';
        ELSE
            SET log_user = CURRENT_USER();
            SET user_type = 'DB USER';
        END IF;

        SET old_data_concat = {old_data_concat};
        
        INSERT INTO tblAuditLog (Table_Name, Row_Id, Log_Type, Log_By, Old_data, User_Type)
        VALUES ('{table_name}', OLD.Id, 'DELETE', log_user, {old_data_concat}, user_type);
    END;
    """


def create_audit_log_triggers():
    db = SessionLocal()
    try:
        # Get all tables starting with 'tbl'
        inspector = inspect(engine)
        table_names = [
            table_name
            for table_name in inspector.get_table_names()
            if table_name.startswith("tbl")
        ]

        for table_name in table_names:
            if table_name in EXEMPT_TABLES:
                continue
            # Get columns
            columns = get_columns(db, table_name)

            # Trigger names
            insert_trigger_name = f"log_{table_name}_after_insert"
            update_trigger_name = f"log_{table_name}_after_update"
            delete_trigger_name = f"log_{table_name}_after_delete"

            # Drop existing triggers
            drop_trigger(db, insert_trigger_name)
            drop_trigger(db, update_trigger_name)
            drop_trigger(db, delete_trigger_name)

            # Create triggers
            insert_trigger = create_insert_trigger(table_name, columns)
            update_trigger = create_update_trigger(table_name, columns)
            delete_trigger = create_delete_trigger(table_name, columns)

            # Execute trigger creation
            db.execute(text(insert_trigger))
            db.execute(text(update_trigger))
            db.execute(text(delete_trigger))
            db.commit()
            print(f"Triggers for table '{table_name}' created/updated successfully.")
    except Exception as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        db.close()
