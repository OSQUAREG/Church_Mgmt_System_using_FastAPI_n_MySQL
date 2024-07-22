# from contextlib import asynccontextmanager, contextmanager

from typing import List
from .utils import extract_submodule, generate_endpoint_code
from fastapi import FastAPI, APIRouter  # type: ignore
from fastapi.routing import APIRoute  # type: ignore
from sqlalchemy import create_engine, text, inspect  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from .config import settings

database = settings.database
db_schema_headchu = settings.db_schema_headchu
db_schema_generic = settings.db_schema_generic


# Connecting to the MySQL Server
def get_engine_session(db_name=None):
    # define connection parameters
    host = settings.host
    port = settings.port
    user = settings.user
    password = settings.password

    SQLALCHEMY_DATABASE_URL = (
        f"mysql+mysqlconnector://{user}:{str(password)}@{host}:{port}"
        if db_name is None
        else f"mysql+mysqlconnector://{user}:{str(password)}@{host}:{port}/{db_name}"
    )

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


# Creating engine and Session instances
engine, SessionLocal = get_engine_session()
engine1, SessionLocal1 = get_engine_session(db_schema_headchu)
# engine2, SessionLocal2 = get_engine_session(db_schema_generic)


# Connecting to MySQL Server (without specified databases/schemas)
async def get_db():  # -> Session:
    db = SessionLocal()
    print("Server/DB connection was successful!")
    try:
        yield db
    finally:
        db.close()
        print("Server/DB connection closed.")


# # Connecting to MySQL Server (with specified databases/schemas)
# # Connecting to the Head Church Database/Schema
# @asynccontextmanager
# async def get_db_main():  # -> Session:
#     db = SessionLocal1()
#     print("Main Database connection was successful!")
#     try:
#         yield db
#     finally:
#         db.close()
#         print("Main Database connection closed.")


# # Connecting to the Generic Database/Schema
# @asynccontextmanager
# async def get_db_generic():  # -> Session:
#     db2 = SessionLocal2()
#     print("Generic Database connection was successful!")
#     try:
#         yield db2
#     finally:
#         db2.close()
#         print("Generic Database connection closed.")


# async def get_dbs():  # -> (Session, Session):
#     async with get_db_main() as db_main, get_db_generic() as db_generic:
#         yield db_main, db_generic


# Automating Trigger Creation for Audit Logs
EXEMPT_COLUMNS = {
    "Created_Date",
    "Created_By",
    "Modified_Date",
    "Modified_By",
    "Status_Date",
    "Status_By",
}

STATUS_COLUMNS = {"Status", "Status_Date", "Status_By"}

EXEMPT_TABLES = {"tblAuditLog", "tblCodeSequence"}


# Get Columns
def get_columns(db, table_name, filter_columns=None):
    columns = (
        db.execute(text(f"SHOW COLUMNS FROM {db_schema_headchu}.{table_name}")).all()
        if filter_columns is None
        else db.execute(
            text(
                f"SHOW COLUMNS FROM {db_schema_headchu}.{table_name} WHERE Field IN {tuple(filter_columns)}"
            )
        ).all()
    )
    return [column[0] for column in columns]


# Drop Triggers if they exist
def drop_trigger(db, trigger_name):
    try:
        db.execute(text(f"DROP TRIGGER IF EXISTS {db_schema_headchu}.{trigger_name};"))
        db.commit()
    except Exception as e:
        print(f"Error dropping trigger {db_schema_headchu}.{trigger_name}: {e}")
        db.rollback()


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


# Create Insert Log Triggers
def create_insert_log_trigger(table_name, columns):
    new_data_concat = create_concat_statement("NEW", columns)
    return f"""
    CREATE TRIGGER {db_schema_headchu}.zlog_{table_name}_after_insert
    AFTER INSERT ON {db_schema_headchu}.{table_name}
    FOR EACH ROW
    BEGIN
        DECLARE log_user VARCHAR(255);
        DECLARE user_type VARCHAR(20);
        DECLARE new_data_concat TEXT;
        
        IF @current_user IS NOT NULL THEN
            SET log_user = @current_user;
            SET user_type = 'APP USER';
        ELSE
            SET log_user = SUBSTRING_INDEX(CURRENT_USER(), '@', 1);
            SET user_type = 'DB USER';
        END IF;
        
        SET new_data_concat = {new_data_concat};
        
        INSERT INTO {db_schema_headchu}.tblAuditLog (Table_Name, Row_Id, Log_Type, Log_By, New_Data, User_Type)
        VALUES ('{table_name}', NEW.Id, 'CREATE', log_user, new_data_concat, user_type);
    END;
    """


# Create Update Log Triggers
def create_update_log_trigger(table_name, columns):
    trigger = f"""
    CREATE TRIGGER {db_schema_headchu}.zlog_{table_name}_after_update
    AFTER UPDATE ON {db_schema_headchu}.{table_name}
    FOR EACH ROW
    BEGIN
        DECLARE log_user VARCHAR(255);
        DECLARE user_type VARCHAR(20);
        
        IF @current_user IS NOT NULL THEN
            SET log_user = @current_user;
            SET user_type = 'APP USER';
        ELSE
            SET log_user = SUBSTRING_INDEX(CURRENT_USER(), '@', 1);
            SET user_type = 'DB USER';
        END IF;
    """
    for column in columns:
        if column in EXEMPT_COLUMNS:
            continue
        trigger += f"""
        IF OLD.{column} != NEW.{column} THEN
            INSERT INTO {db_schema_headchu}.tblAuditLog (Table_Name, Column_Name, Row_Id, Log_Type, Log_By, Old_Data, New_Data, User_Type)
            VALUES ('{table_name}', '{column}', NEW.Id, 'UPDATE', log_user, OLD.{column}, NEW.{column}, user_type);
        END IF;
        """
    trigger += "END;"
    return trigger


# Create Delete Log Triggers
def create_delete_log_trigger(table_name, columns):
    old_data_concat = create_concat_statement("OLD", columns)
    return f"""
    CREATE TRIGGER {db_schema_headchu}.zlog_{table_name}_after_delete
    AFTER DELETE ON {db_schema_headchu}.{table_name}
    FOR EACH ROW
    BEGIN
        DECLARE log_user VARCHAR(255);
        DECLARE user_type VARCHAR(20);
        DECLARE old_data_concat TEXT;
        
        IF @current_user IS NOT NULL THEN
            SET log_user = @current_user;
            SET user_type = 'APP USER';
        ELSE
            SET log_user = SUBSTRING_INDEX(CURRENT_USER(), '@', 1);
            SET user_type = 'DB USER';
        END IF;

        SET old_data_concat = {old_data_concat};
        
        INSERT INTO {db_schema_headchu}.tblAuditLog (Table_Name, Row_Id, Log_Type, Log_By, Old_data, User_Type)
        VALUES ('{table_name}', OLD.Id, 'DELETE', log_user, {old_data_concat}, user_type);
    END;
    """


# Create Insert By User Triggers
def create_insert_crt_trigger(db, table_name):
    columns = get_columns(db, table_name, filter_columns=STATUS_COLUMNS)
    if len(columns) > 0:
        trigger_text = f"""
        CREATE TRIGGER {db_schema_headchu}.ztrk_{table_name}_before_insert
        BEFORE INSERT ON {db_schema_headchu}.{table_name}
        FOR EACH ROW
        BEGIN
            DECLARE log_user VARCHAR(255);
            DECLARE _code VARCHAR(5);
        
            -- Checks the Status entered before inserting
            SELECT `Code` INTO _code FROM {db_schema_generic}.tblCodeTable 
                WHERE Category = 'Status' AND `Code`= NEW.Status;
            
            IF _code IS NULL THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Foreign key constraint violated: Invalid Status';
            END IF;
            
            IF @current_user IS NOT NULL THEN
                SET log_user = @current_user;
            ELSE
                SET log_user = SUBSTRING_INDEX(CURRENT_USER(), '@', 1);
            END IF;

            IF NEW.Created_By IS NULL THEN
                SET NEW.Created_By = log_user;
            END IF;
        END;
        """
        return trigger_text
    else:
        trigger_text = f"""
        CREATE TRIGGER {db_schema_headchu}.ztrk_{table_name}_before_insert
        BEFORE INSERT ON {db_schema_headchu}.{table_name}
        FOR EACH ROW
        BEGIN
            DECLARE log_user VARCHAR(255);
            
            IF @current_user IS NOT NULL THEN
                SET log_user = @current_user;
            ELSE
                SET log_user = SUBSTRING_INDEX(CURRENT_USER(), '@', 1);
            END IF;
            
            IF NEW.Created_By IS NULL THEN
                SET NEW.Created_By = log_user;
            END IF;
        END;
        """
        return trigger_text


# Create Insert By User Triggers
def create_update_mod_trigger(db, table_name):
    columns = get_columns(db, table_name, filter_columns=STATUS_COLUMNS)
    if len(columns) > 0:
        trigger_text = f"""
        CREATE TRIGGER {db_schema_headchu}.ztrk_{table_name}_before_update
        BEFORE UPDATE ON {db_schema_headchu}.{table_name}
        FOR EACH ROW
        BEGIN
            DECLARE log_user VARCHAR(255);
            DECLARE _code VARCHAR(5);

            -- Set log user
            IF @current_user IS NOT NULL THEN
                SET log_user = @current_user;
            ELSE
                SET log_user = SUBSTRING_INDEX(CURRENT_USER(), '@', 1);
            END IF;

            IF NEW.Modified_By IS NULL THEN
                SET NEW.Modified_By = log_user;
            END IF;

            -- updating status related columns
            IF NEW.Is_Active != OLD.Is_Active OR NEW.Status != OLD.Status THEN
                SET NEW.Status_Date = NOW();
                SET NEW.Status_By = log_user;
                
                IF NEW.Is_Active = 0 THEN
                    SET NEW.Status = 'INA';
                END IF;
                
                IF NEW.Is_Active = 1 AND OLD.Is_Active = 0 THEN
                    SET NEW.Status = 'PND';
                END IF;

                -- Checks the Status entered before inserting
                SELECT `Code` INTO _code FROM {db_schema_generic}.tblCodeTable 
                    WHERE Category = 'Status' AND `Code`= NEW.Status;
                
                IF _code IS NULL THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Foreign key constraint violated: Invalid Status';
                END IF;
            END IF;
        END;
        """
        return trigger_text
    else:
        trigger_text = f"""
        CREATE TRIGGER {db_schema_headchu}.ztrk_{table_name}_before_update
        BEFORE UPDATE ON {db_schema_headchu}.{table_name}
        FOR EACH ROW
        BEGIN
            DECLARE log_user VARCHAR(255);
            
            IF @current_user IS NOT NULL THEN
                SET log_user = @current_user;
            ELSE
                SET log_user = SUBSTRING_INDEX(CURRENT_USER(), '@', 1);
            END IF;

            IF NEW.Modified_By IS NULL THEN
                SET NEW.Modified_By = log_user;
            END IF;
        END;
        """
        return trigger_text


def create_audit_log_triggers():
    db = SessionLocal()
    try:
        inspector = inspect(engine1)
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
            insert_log_trigger_name = f"zlog_{table_name}_after_insert"
            update_log_trigger_name = f"zlog_{table_name}_after_update"
            delete_log_trigger_name = f"zlog_{table_name}_after_delete"

            # Drop existing triggers
            drop_trigger(db, insert_log_trigger_name)
            drop_trigger(db, update_log_trigger_name)
            drop_trigger(db, delete_log_trigger_name)

            # Create triggers
            insert_log_trigger = create_insert_log_trigger(table_name, columns)
            update_log_trigger = create_update_log_trigger(table_name, columns)
            delete_log_trigger = create_delete_log_trigger(table_name, columns)

            # Execute trigger creation
            db.execute(text(insert_log_trigger))
            db.execute(text(update_log_trigger))
            db.execute(text(delete_log_trigger))
            db.commit()
            print(
                f"Audit Log Triggers for table '{db_schema_headchu}.{table_name}' created/updated successfully."
            )
    except Exception as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        db.close()


def create_change_track_triggers():
    db = SessionLocal()
    try:
        inspector = inspect(engine1)
        table_names = [
            table_name
            for table_name in inspector.get_table_names()
            if table_name.startswith("tbl")
        ]

        for table_name in table_names:
            if table_name in EXEMPT_TABLES:
                continue

            # Trigger names
            insert_crt_trigger_name = f"ztrk_{table_name}_before_insert"
            update_mod_trigger_name = f"ztrk_{table_name}_before_update"

            # Drop existing triggers
            drop_trigger(db, insert_crt_trigger_name)
            drop_trigger(db, update_mod_trigger_name)

            # Create triggers
            insert_crt_trigger = create_insert_crt_trigger(db, table_name)
            update_mod_trigger = create_update_mod_trigger(db, table_name)
            # Execute trigger creation
            db.execute(text(insert_crt_trigger))
            db.execute(text(update_mod_trigger))
            db.commit()

            print(
                f"Change Tracking Trigger for table '{db_schema_headchu}.{table_name}' created/updated successfully."
            )
    except Exception as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        db.close()


def get_all_endpoints(app: FastAPI) -> List[str]:
    endpoints = []
    openapi_schema = app.openapi()
    tag_descriptions = {
        tag["name"]: tag.get("description", "")
        for tag in openapi_schema.get("tags", [])
    }
    for route in app.routes:
        if isinstance(route, APIRoute):
            router_name = route.tags[0] if route.tags else "Default"
            # Get the router description from the tags
            router_description = tag_descriptions.get(router_name, "")

            route_details = {
                # "router_name": router_name,
                "router_description": router_description,
                "name": route.name,
                "mod_sub": extract_submodule(router_name),
                "description": (
                    route.description.replace("## ", "") if route.description else ""
                ),
            }
            endpoints.append(route_details)
    return endpoints


def insert_mod_sub_endpts_table(app: FastAPI):
    db = SessionLocal()
    endpoints = get_all_endpoints(app)
    try:
        # Truncate the AccessTable
        db.execute(text("SET foreign_key_checks = 0;"))
        db.execute(
            text(f"TRUNCATE TABLE {db_schema_generic}.tblEndpoints;"),
        )
        db.execute(
            text(f"TRUNCATE TABLE {db_schema_generic}.tblSubModules;"),
        )
        db.execute(
            text(f"TRUNCATE TABLE {db_schema_generic}.tblModules;"),
        )
        db.execute(text("SET foreign_key_checks = 1;"))
        db.commit()

        end_points = set()
        modules = set()
        submodules = set()
        for endpoint in endpoints:
            code = generate_endpoint_code(endpoint["name"])  # type: ignore
            router_description = endpoint["router_description"]  # type: ignore
            submodule_description = (
                router_description.split(":")[0] if router_description else ""
            )
            # Add endpoints to the Endpoints set for unique values
            end_points.add(
                (
                    code,
                    endpoint["name"],  # type: ignore
                    endpoint["description"],  # type: ignore
                    endpoint["mod_sub"]["submodule_code"],  # type: ignore
                    # endpoint["methods"],  # type: ignore
                )
            )
            # print(end_points)
            # Add modules to the Modules set for unique values
            modules.add(
                (
                    endpoint["mod_sub"]["module_code"],  # type: ignore
                    endpoint["mod_sub"]["module_name"],  # type: ignore
                )
            )
            # Add submodules to the SubModules set for unique values
            submodules.add(
                (
                    endpoint["mod_sub"]["submodule_code"],  # type: ignore
                    endpoint["mod_sub"]["submodule_name"],  # type: ignore
                    endpoint["mod_sub"]["module_code"],  # type: ignore
                    submodule_description,  # type: ignore
                )
            )

        # Insert new records into the Modules Table
        for code, name in modules:
            db.execute(
                text(
                    f"""
                    INSERT INTO {db_schema_generic}.tblModules (Code, Module)
                    VALUES (:Code, :Module);
                    """
                ),
                {
                    "Code": code,
                    "Module": name,
                },
            )
            db.commit()
            print(f"Modules Table updated for module '{name}' - {code}")  # type: ignore

        # Insert new records into the SubModules Table
        for code, name, module_code, description in submodules:
            db.execute(
                text(
                    f"""
                    INSERT INTO {db_schema_generic}.tblSubModules (Code, SubModule, Description, Module_Code)
                    VALUES (:Code, :SubModule, :Description, :Module_Code);
                    """
                ),
                {
                    "Code": code,
                    "SubModule": name,
                    "Module_Code": module_code,
                    "Description": description,
                },
            )
            db.commit()
            print(f"SubModules Table updated for submodule '{name}' - {code}")

        # Insert new records into the Endpoints Table
        for code, name, description, submodule_code in end_points:
            db.execute(
                text(
                    f"""
                    INSERT INTO {db_schema_generic}.tblEndpoints (Code, Name, Description, SubModule_Code)
                    VALUES (:Code, :Name, :Description, :SubModule_Code);
                    """
                ),
                {
                    "Code": code,
                    "Name": name,
                    "Description": description,
                    "SubModule_Code": submodule_code,
                },
            )
            db.commit()
            print(f"Endpoints Table updated for endpoint '{name}' - {code}")  # type: ignore
    except Exception as err:
        print(f"Error: {err}")
        db.rollback()
