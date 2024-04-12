database_name = "TestDB01"


def generate_code_trigger_query(table_name: str):
    code_trigger_query = f"""
    DELIMITER //
    
    CREATE TRIGGER Auto_Generate_Code
    BEFORE INSERT ON {table_name} FOR EACH ROW
    BEGIN
	DECLARE new_code VARCHAR(18);
	
  	UPDATE tblCodeSequence SET Code_Sequence = Code_Sequence + 1 WHERE TableName = 'tblProvince' AND Head_Code = NEW.HeadChurch_Code;

	SELECT CONCAT(Code_Prefix, LPAD(Code_Sequence, 9, '0')) INTO new_code
		FROM tblCodeSequence
		WHERE Table_Name = 'tblProvince' AND Head_Code = NEW.HeadChurch_Code;
		
	SET NEW.Code = new_code;
END//

    CREATE TRIGGER Insert_{table_name}_Code_into_tblRef
    AFTER INSERT ON {table_name}
    FOR EACH ROW
    BEGIN
        INSERT INTO tblReference (Code, Table_Name)
        VALUES (NEW.Code, {table_name});
    END//
    
    DELIMITER ;
    """
    return code_trigger_query


def generate_event_code_trigger_query():
    code_trigger_query = f"""
    DELIMITER //
    
    CREATE TRIGGER Auto_Generate_Code
    BEFORE INSERT ON tblEvent FOR EACH ROW
    BEGIN
        DECLARE next_no INT;
        DECLARE code_string VARCHAR(2);
        DECLARE church_code VARCHAR(3);
        SET event_date = DATE_FORMAT(NEW.Event_Date, '%Y%m%d');
        
        -- upadte the next sequence and get the code and the code string and store in variables
        UPDATE tblCodeSequence SET Code_Sequence = Code_Sequence + 1 WHERE Table_Name = {table_name};
        SELECT COUNT(*) +1 INTO next_no FROM tblCodeSequence WHERE DATE(Event_Date) = DATE(NEW.Event_Date);
        SELECT Code INTO code_string FROM tblCodeSequence WHERE Table_Name = {table_name};
        SELECT Head_Code INTO church_code FROM tblCodeSequence WHERE Table_Name = {table_name};

        -- set the new code
        SET NEW.Code = CONCAT(church_code, "-", code_string, event_date, "-", LPAD(next_no, 4, '0'));
    END//

    //
    CREATE TRIGGER Insert_{table_name}_Code_into_tblRef
    AFTER INSERT ON {table_name}
    FOR EACH ROW
    BEGIN
        INSERT INTO tblReference (Code, Table_Name)
        VALUES (NEW.Code, {table_name});
    END//
    
    DELIMITER ;
    """
    return code_trigger_query


def insert_code_seq_trigger_query(table_name: str):
    insert_code_trigger_query = f"""
    DELIMITER //
    CREATE TRIGGER Insert_Code_Sequence
    AFTER INSERT ON {table_name} FOR EACH ROW
    BEGIN        
	INSERT INTO tblCodeSequence
		(`Table_Name`, `Table_Code`, `Head_Code`, Code_Prefix)
	VALUES 
   	('tblProvince', 'PRV', NEW.Code, CONCAT(NEW.Code, '-', 'PRV', '-')),
		('tblZone', 'ZON', NEW.Code, CONCAT(NEW.Code, '-', 'ZON', '-')),
		('tblArea', 'ARE', NEW.Code, CONCAT(NEW.Code, '-', 'ARE', '-')),
		('tblBranch', 'BRN', NEW.Code, CONCAT(NEW.Code, '-', 'BRN', '-')),
		('tblGroup', 'GRP', NEW.Code, CONCAT(NEW.Code, '-', 'GRP', '-')),
		('tblSubGroup', 'SGP', NEW.Code, CONCAT(NEW.Code, '-', 'SGP', '-')),
		('tblMember', 'MBR', NEW.Code, CONCAT(NEW.Code, '-', 'MBR', '-')),
		('tblEvent', 'EVT', NEW.Code, CONCAT(NEW.Code, '-', 'EVT', '-')),
		('tblAsset', 'AST', NEW.Code, CONCAT(NEW.Code, '-', 'AST', '-'));
    END//    
    DELIMITER ;
    """
    return insert_code_trigger_query


auto_current_date_user = """
    Created_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    Created_By VARCHAR(100) NOT NULL,
    Modified_Date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    Modified_By VARCHAR(100) NOT NULL
    """


# MODULE: ADMINISTRATION MANAGEMENT

# ----------------FIRST LEVEL TABLES----------------

## ----------------tblCodeSequence----------------
def tblcodesequence_query():
    table_name = "tblCodeSequence"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Table_Name VARCHAR(255) NOT NULL UNIQUE,
        Head_Code VARCHAR(4) NOT NULL COMMENT 'Code of Head Church',
        Code VARCHAR(3) NOT NULL UNIQUE,
        Code_Sequence INT DEFAULT 0,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    insert_code_trigger_query = insert_code_seq_trigger_query

    # # Sample Insert
    # insert_query = f"""
    # INSERT INTO {table_name} 
    #     (Table_Name, Code)
    # VALUES 
    #     ('tblProvince', 'PV'),
    #     ('tblZone', 'ZN'),
    #     ('tblArea', 'AR'),
    #     (tblBranch', 'BR'),
    #     ('tblGroup', 'GP'),
    #     ('tblSubGroup', 'SG'),
    #     ('tblMember', 'MB');
    # """
    return create_query, c_user_trigger_query, insert_code_trigger_query


## ----------------tblChurchLevel----------------
def tblchurchlevel_query():
    table_name = "tblChurchLevel"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Alt_Name VARCHAR(255) UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Level INT NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, ALt_Name, Code, Level)
    VALUES 
        ('Church', 'HQ', 'CHU', 1),
        ('Province', 'Province', 'PRO', 2),
        ('Zone', 'Diocese, 'ZON', 3),
        ('Area', 'Archdeaconry', 'ARE', 4),
        ('Branch', 'Parish', 'BRN', 5),
        ('Group', 'Unit', 'GRP', 6),
        ('SubGroup', 'Sub Unit', 'SGP', 7);
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblLocationType----------------
def tbllocationtype_query():
    table_name = "tblLocationType"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Alt_Name VARCHAR(255) UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Level INT NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, ALt_Name, Code, Level)
    VALUES 
        ('Country', 'Country', 'CTY', 1),
        ('Region', 'Zone', 'REG', 2),
        ('State', 'State', 'STA', 3),
        (Town', 'City', 'TWN', 4);
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblGroupType----------------
def tblgrouptype_query():
    table_name = "tblGroupType"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Description VARCHAR(255),
        Code VARCHAR(3) NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, Description, Code)
    VALUES 
        ('Fellowship', 'Fellowship', 'FLS'),
        ('Committee', 'Committee', 'CMT');
        ('Department', 'Department', 'DPT');
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblGroupMemberType----------------
def tblgroupmembertype_query():
    table_name = "tblGroupMemberType"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Alt_Name VARCHAR(255) UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, ALt_Name, Code)
    VALUES 
        ('Private', 'Private', 'PVT'),
        ('Public', 'Public', 'PUB');
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblMemberType----------------
def tblmembertype_query():
    table_name = "tblMemberType"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Alt_Name VARCHAR(255) UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Level INT NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, ALt_Name, Code, Level)
    VALUES 
        ('Minister', 'Minister', 'MIN', 1),
        ('Worker', 'Staff', 'WRK', 2),
        ('Member', 'Member', 'MBR', 3);
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblPositionType----------------
def tblpositiontype_query():
    table_name = "tblPositionType"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Alt_Name VARCHAR(255) UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Level INT NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, ALt_Name, Code, Level)
    VALUES 
        ('Minister', 'Minister', 'MIN', 1),
        ('Leader', 'Head', 'LDR', 2),
        ('Others', 'Others', 'OTH', 3);
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblWorkerType----------------
def tblworkertype_query():
    table_name = "tblWorkerType"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Alt_Name VARCHAR(255) UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, ALt_Name, Code)
    VALUES 
        ('Volunteer', 'Volunteer', 'VTR'),
        ('Employee', 'Employee', 'EMP');
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblEmployStatus----------------
def tblemploystatus_query():
    table_name = "tblEmployStatus"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, Code)
    VALUES 
        ('Employed', 'EMP'),
        ('Self-Employee', 'SEM'),
        ('Unemployed', 'UEM'),
        ('Retired', 'RET'),
        ('Student', 'STU'),
        ('Others', 'OTH');
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblMaritalStatus----------------
def tblmaritalstatus_query():
    table_name = "tblMaritalStatus"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(255) NOT NULL UNIQUE,
        Code VARCHAR(3) NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, Code)
    VALUES 
        ('Married', 'MRD'),
        ('Single', 'SNG');
    """
    return create_query, c_user_trigger_query, insert_query


# ----------------SECOND LEVEL TABLES----------------
## ----------------tblCountry----------------
def tblcountry_query():
    table_name = "tblCountry"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Country VARCHAR(255) NOT NULL UNIQUE,
        Code VARCHAR(4) NOT NULL UNIQUE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)

    # Sample Insert
    insert_query = f"""
    INSERT INTO {table_name} 
        (Name, Code)
    VALUES 
        ('Nigeria', 'NIG'),
        ('Ghana', 'GHA');
    """
    return create_query, c_user_trigger_query, insert_query


## ----------------tblRegion----------------
def tblregion_query():
    table_name = "tblRegion"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Region VARCHAR(255) NOT NULL,
        Code VARCHAR(4) NOT NULL UNIQUE,
        Country_Code VARCHAR(4) NOT NULL, CONSTRAINT fk_Country_Code FOREIGN KEY (Country_Code) REFERENCES tblCountry(Code),
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query


## ----------------tblState----------------
def tblstate_query():
    table_name = "tblState"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        State VARCHAR(255) NOT NULL,
        Code VARCHAR(4) NOT NULL UNIQUE,
        Region_Code VARCHAR(4) NOT NULL, CONSTRAINT fk_Region_Code FOREIGN KEY (Region_Code) REFERENCES tblRegion(Code),
        Country_Code VARCHAR(100) NOT NULL, CONSTRAINT fk_Country_Code FOREIGN KEY (Country_Code) REFERENCES tblCountry(Code),
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query


## ----------------tblTown----------------
def tbltowm_query():
    table_name = "tblTown"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Town VARCHAR(255) NOT NULL,
        Code VARCHAR(4) NOT NULL UNIQUE,
        State_Code VARCHAR(4) NOT NULL, CONSTRAINT fk_State_Code FOREIGN KEY (State_Code) REFERENCES tblState(Code),
        Region_Code VARCHAR(4) NOT NULL, CONSTRAINT fk_Region_Code FOREIGN KEY (Region_Code) REFERENCES tblRegion(Code),
        Country_Code VARCHAR(100) NOT NULL, CONSTRAINT fk_Country_Code FOREIGN KEY (Country_Code) REFERENCES tblCountry(Code),
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query


## ----------------tblReferenceCode----------------
def tblreferencecode_query():
    table_name = "tblReferenceCode"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Table_Name VARCHAR(255) NOT NULL,
        Code VARCHAR(4) NOT NULL UNIQUE,
        {auto_current_date_user}
        );
    """
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query


# ----------------HIERARCHY MANAGEMENT----------------

## ----------------tblHeadChurch---------------
def tblchurch_query():
    table_name = "tblHeadChurch"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS tblHeadChurch (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(4) NOT NULL UNIQUE,
        Name VARCHAR(255) NOT NULL,
        Alt_Name VARCHAR(255) COMMENT 'Alternative Name of the Church',
        Address VARCHAR(255) NOT NULL,
        Founding_Date DATE,
        About TEXT COMMENT 'About the Church',
        Mission VARCHAR(1000) COMMENT 'Mission of the Church',
        Vision VARCHAR(1000) COMMENT 'Vision of the Church',
        Town_Code VARCHAR(4) NOT NULL, 
            CONSTRAINT fk_HeadChurch_Town FOREIGN KEY (Town_Code) REFERENCES tblTown(Code) ON UPDATE CASCADE,
        State_Code VARCHAR(4) NOT NULL, 
            CONSTRAINT fk_HeadChurch_State FOREIGN KEY (State_Code) REFERENCES tblState(Code) ON UPDATE CASCADE,
        Region_Code VARCHAR(4) NOT NULL, 
            CONSTRAINT fk_HeadChurch_Region FOREIGN KEY (Region_Code) REFERENCES tblRegion(Code) ON UPDATE CASCADE,
        Country_Code VARCHAR(4) NOT NULL, 
            CONSTRAINT fk_HeadChurch_Country FOREIGN KEY (Country_Code) REFERENCES tblCountry(Code) ON UPDATE CASCADE,
        Pastor_Code VARCHAR(16) NOT NULL COMMENT 'Head Pastor who oversees the Head Church',
            CONSTRAINT fk_Church_Pastor FOREIGN KEY (Pastor_Code) REFERENCES tblMember(Code) ON UPDATE CASCADE,
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblProvince---------------
def tblprovince_query():
    table_name = "tblProvince"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(10) NOT NULL UNIQUE,
        Name VARCHAR(255) NOT NULL,
        Alt_Name VARCHAR(255) COMMENT 'Alternative Name of the Province',
        Address VARCHAR(255) NOT NULL,
        Founding_Date DATE,
        About TEXT COMMENT 'About the Province',
        Mission VARCHAR(1000) COMMENT 'Mission of the Province',
        Vision VARCHAR(1000) COMMENT 'Vision of the Province',
        Town_Code VARCHAR(4) NOT NULL, CONSTRAINT 'fk_Province_Town' FOREIGN KEY (Town_Code) REFERENCES tblTown(Code),
        State_Code VARCHAR(4) NOT NULL, CONSTRAINT 'fk_Province_State' FOREIGN KEY (State_Code) REFERENCES tblState(Code),
        Region_Code VARCHAR(4) NOT NULL, CONSTRAINT 'fk_Province_Region' FOREIGN KEY (Region_Code) REFERENCES tblRegion(Code),
        Country_Code VARCHAR(4) NOT NULL, CONSTRAINT 'fk_Province_Country' FOREIGN KEY (Country_Code) REFERENCES tblCountry(Code),
        Pastor_Code VARCHAR(16) NOT NULL COMMENT 'Pastor who overseers the Province', CONSTRAINT 'fk_Province_Pastor' FOREIGN KEY (Pastor_Code) REFERENCES tblMember(Code),
        Church_Code VARCHAR(4) NOT NULL COMMENT 'Head Church where the Province reports to', CONSTRAINT 'fk_Province_HeadChurch' FOREIGN KEY (Church_Code) REFERENCES tblHeadChurch(Code),
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblZone---------------
def tblzone_query():
    table_name = "tblZone"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(10) NOT NULL UNIQUE,
        Name VARCHAR(255) NOT NULL,
        Alt_Name VARCHAR(255) COMMENT 'Alternative Name of the Zone',
        Address VARCHAR(255) NOT NULL COMMENT 'Address of the Zone',
        Founding_Date DATE,
        About TEXT COMMENT 'About the Zone',
        Mission VARCHAR(1000) COMMENT 'Mission of the Zone',
        Vision VARCHAR(1000) COMMENT 'Vision of the Zone',
        Town_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblTown(Code),
        State_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblState(Code),
        Region_code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblRegion(Code),
        Country_Code VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblCountry(Code),
        Pastor_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblMember(Code) COMMENT 'Pastor who overseers the Zone',
        Province_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblProvince(Code) COMMENT 'Province where the Zone is located',
        Church_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblChurch(Code) COMMENT 'Head Church where the zone is located',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblArea---------------
def tblarea_query():
    table_name = "tblArea"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(10) NOT NULL UNIQUE,
        Name VARCHAR(255) NOT NULL,
        Alt_Name VARCHAR(255) COMMENT 'Alternative Name of the Area',
        Address VARCHAR(255) NOT NULL COMMENT 'Address of the Area',
        Founding_Date DATE,
        About TEXT COMMENT 'About the Area',
        Mission VARCHAR(1000) COMMENT 'Mission of the Area',
        Vision VARCHAR(1000) COMMENT 'Vision of the Area',
        Town_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblTown(Code),
        State_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblState(Code),
        Region_code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblRegion(Code),
        Country_Code VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblCountry(Code),
        Pastor_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblMember(Code) COMMENT 'Pastor who overseers the Area',
        Zone_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblZone(Code) COMMENT 'Zone where the Area is located',
        Province_Code VARCHAR(10) FOREIGN KEY REFERENCES tblProvince(Code) COMMENT 'Province where the Area is located',
        Church_Code VARCHAR(4) FOREIGN KEY REFERENCES tblChurch(Code) COMMENT 'Head Church where the Area is located',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblBranch---------------
def tblbranch_query():
    table_name = "tblBranch"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(10) NOT NULL UNIQUE,
        Name VARCHAR(255) NOT NULL,
        Alt_Name VARCHAR(255),
        Address VARCHAR(255) NOT NULL,
        Founding_Date DATE,
        About TEXT,
        Mission VARCHAR(1000),
        Vision VARCHAR(1000),
        Town_Code VARCHAR(4) FOREIGN KEY REFERENCES tblTown(Code),
        State_Code VARCHAR(4) FOREIGN KEY REFERENCES tblState(Code),
        Region_code VARCHAR(4) FOREIGN KEY REFERENCES tblRegion(Code),
        Country_Code VARCHAR(3) FOREIGN KEY REFERENCES tblCountry(Code),
        Pastor_Code VARCHAR(10) FOREIGN KEY REFERENCES tblMember(Code) COMMENT 'Pastor who overseers the Branch',
        Level_Code VARCHAR(10) FOREIGN KEY REFERENCES tblChurchLevel(Code) COMMENT 'Level of the Branch',
        Zone_Code VARCHAR(10) FOREIGN KEY REFERENCES tblZone(Code) COMMENT 'Zone of the Branch',
        Province_Code VARCHAR(10) FOREIGN KEY REFERENCES tblProvince(Code) COMMENT 'Province of the Branch',
        Church_Code VARCHAR(4) FOREIGN KEY REFERENCES tblChurch(Code) COMMENT 'Head Church of the Branch',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblGroup---------------
def tblgroup_query():
    table_name = "tblGroup"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(10) NOT NULL UNIQUE,
        Name VARCHAR(255) NOT NULL,
        Alt_Name VARCHAR(255) COMMENT 'Alternative Name of the Group',
        Description VARCHAR(1000) COMMENT 'Description (Mission, Vision, Function or Reason) of the Group',
        Type VARCHAR(30) COMMENT 'Type of Group',
        Address VARCHAR(255) NOT NULL COMMENT 'Address (Secretariat or meeting venue) of the Group',
        Start_Date DATE NOT NULL,
        End_Date DATE,
        Town_Code VARCHAR(4) FOREIGN KEY REFERENCES tblTown(Code),
        State_Code VARCHAR(4) FOREIGN KEY REFERENCES tblState(Code),
        Region_code VARCHAR(4) FOREIGN KEY REFERENCES tblRegion(Code),
        Country_Code VARCHAR(3) FOREIGN KEY REFERENCES tblCountry(Code),
        Pastor_Code VARCHAR(10) FOREIGN KEY REFERENCES tblMember(Code) COMMENT 'Pastor who overseers the Branch',
        Level_Code VARCHAR(10) FOREIGN KEY REFERENCES tblChurchLevel(Code) COMMENT 'Level of the Branch',
        Zone_Code VARCHAR(10) FOREIGN KEY REFERENCES tblZone(Code) COMMENT 'Zone of the Branch',
        Province_Code VARCHAR(10) FOREIGN KEY REFERENCES tblProvince(Code) COMMENT 'Province of the Branch',
        Church_Code VARCHAR(4) FOREIGN KEY REFERENCES tblChurch(Code) COMMENT 'Head Church of the Branch',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
    );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


# MODULE: MEMBERSHIP MANAGEMENT

## ----------------tblMember---------------
def tblmember_query():
    table_name = "tblMember"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(10) NOT NULL,
        First_Name VARCHAR(255) NOT NULL,
        Middle_Name VARCHAR(255),
        Last_Name VARCHAR(255) NOT NULL,
        Title VARCHAR(50),
        Title2 VARCHAR(50),
        Family_Name VARCHAR(255) NOT NULL COMMENT 'Family Name of the Member',
        Gender VARCHsAR(50) NOT NULL,
        Date_Of_Birth DATE NOT NULL,
        Marital_Status VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblMaritalStatus(Code),
        Employ_Status VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblEmployStatus(Code),
        Occupation VARCHAR(255),
        Phone_No VARCHAR(15) NOT NULL,
        Phone_No2 VARCHAR(15),
        Email VARCHAR(255),
        Email2 VARCHAR(255),
        Home_Address VARCHAR(255),
        Town_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblTown(Code),
        State_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblState(Code),
        Region_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblRegion(Code),
        Country_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblCountry(Code),
        -- Level_Code VARCHAR(3) FOREIGN KEY REFERENCES tblChurchLevel(Code) COMMENT 'Level of the Member Branch',
        -- Ref_Code VARCHAR(10) FOREIGN KEY REFERENCES tblReferenceCode(Code),
        Branch_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblBranch(Code) COMMENT 'Branch of the Member',
        Church_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblChurch(Code) COMMENT 'Head Church of the Member',
        Member_Type VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblMemberType(Code) COMMENT 'Type of the Member',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """

    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblPosition---------------
def tblposition_query():
    table_name = "tblPosition"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(5) NOT NULL UNIQUE,
        Position VARCHAR(255) NOT NULL UNIQUE,
        Description VARCHAR(1000),
        Position_Type VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblPositionType(Code),
        Member_Type VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblMemberType(Code),
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblMemberPosition---------------
def tblmemberposition_query():
    table_name = "tblMemberPosition"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Member_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblMember(Code),
        Position_Code VARCHAR(255) NOT NULL FOREIGN KEY REFERENCES tblPosition(Code),
        Start_Date DATE NOT NULL COMMENT 'Date when the member was appointed to the position',
        End_Date DATE NOT NULL COMMENT 'Date when the member resigned from the position',
        Level_Code VARCHAR(3) FOREIGN KEY REFERENCES tblChurchLevel(Code) COMMENT 'Church Level of the Position',
        Ref_Code VARCHAR(10) FOREIGN KEY REFERENCES tblReferenceCode(Code) COMMENT 'Reference Code to the Church Level',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


## ----------------tblMemberGroup---------------
def tblmembergroup_query():
    table_name = "tblMemberGroup"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Member_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblMember(Code),
        Group_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblGroup(Code),
        Join_Date DATE NOT NULL COMMENT 'Date when the member joined the group',
        Exit_Date DATE COMMENT 'Date when the member left the group',
        Level_Code VARCHAR(3) FOREIGN KEY REFERENCES tblChurchLevel(Code) COMMENT 'Church Level of the group',
        Ref_Code VARCHAR(10) FOREIGN KEY REFERENCES tblReferenceCode(Code) COMMENT 'Reference Code to the Church Level',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """
    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


# MODULE: EVENT MANAGEMENT

## ----------------tblEvent---------------
def tblEvent_query():
    table_name = "tblMember"
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Code VARCHAR(10) NOT NULL,
        First_Name VARCHAR(255) NOT NULL,
        Middle_Name VARCHAR(255),
        Last_Name VARCHAR(255) NOT NULL,
        Title VARCHAR(50),
        Title2 VARCHAR(50),
        Family_Name VARCHAR(255) NOT NULL COMMENT 'Family Name of the Member',
        Gender VARCHsAR(50) NOT NULL,
        Date_Of_Birth DATE NOT NULL,
        Marital_Status VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblMaritalStatus(Code),
        Employ_Status VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblEmployStatus(Code),
        Occupation VARCHAR(255),
        Phone_No VARCHAR(15) NOT NULL,
        Phone_No2 VARCHAR(15),
        Email VARCHAR(255),
        Email2 VARCHAR(255),
        Home_Address VARCHAR(255),
        Town_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblTown(Code),
        State_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblState(Code),
        Region_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblRegion(Code),
        Country_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblCountry(Code),
        -- Level_Code VARCHAR(3) FOREIGN KEY REFERENCES tblChurchLevel(Code) COMMENT 'Level of the Member Branch',
        -- Ref_Code VARCHAR(10) FOREIGN KEY REFERENCES tblReferenceCode(Code),
        Branch_Code VARCHAR(10) NOT NULL FOREIGN KEY REFERENCES tblBranch(Code) COMMENT 'Branch of the Member',
        Church_Code VARCHAR(4) NOT NULL FOREIGN KEY REFERENCES tblChurch(Code) COMMENT 'Head Church of the Member',
        Member_Type VARCHAR(3) NOT NULL FOREIGN KEY REFERENCES tblMemberType(Code) COMMENT 'Type of the Member',
        Is_Active BOOLEAN DEFAULT 1,
        {auto_current_date_user}
        );
    """

    code_trigger_query = generate_code_trigger_query(table_name)
    c_user_trigger_query = add_current_user_trigger_query(table_name)
    return create_query, c_user_trigger_query, code_trigger_query


# MODULE: ROLE MANAGEMENT
## ----------------tblRole---------------
table_name = "tblRole"
tblrole_create_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description VARCHAR(255),
    Level_Id INT FOREIGN KEY REFERENCES tblHierarchy(Level),
    Is_Active BOOLEAN DEFAULT 1,
    Created_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    Created_By VARCHAR(100) NOT NULL,
    Modified_Date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    Modified_By VARCHAR(100) NOT NULL
    );
"""
tblrole_user_trigger_query = add_current_user_trigger_query(table_name)


table_name = "tblAccessType"
tblaccesstype_create_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description VARCHAR(255),
    Is_Active BOOLEAN DEFAULT 1,
    {auto_current_date_user}
    );
"""
tblaccesstype_user_trigger_query = add_current_user_trigger_query(table_name)


table_name = "tblAccessArea"
tblaccessarea_create_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL COMMENT 'Name of the Access Area',
    Description VARCHAR(255) COMMENT 'Description of the Access Area',
    Is_Active BOOLEAN DEFAULT 1,
    {auto_current_date_user}
    );
"""
tblaccessarea_user_trigger_query = add_current_user_trigger_query(table_name)


table_name = "tblRoleAccessArea"
tblroleaccessarea_create_query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Role_Id INT FOREIGN KEY REFERENCES tblRole(Id),
    Access_Area_Id INT FOREIGN KEY REFERENCES tblAccessArea(Id),
    Access_Type_Id INT FOREIGN KEY REFERENCES tblAccessType(Id),
    Is_Active BOOLEAN DEFAULT 1,
    {auto_current_date_user}
    );
"""
tblroleaccessarea_user_trigger_query = add_current_user_trigger_query(table_name)


table_name = "tblUserRole"
tbluserrole_create_query = f"""
CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Member_Id INT FOREIGN KEY REFERENCES tblMember(Id),
    Role_Id INT FOREIGN KEY REFERENCES tblRole(Id),
    Role_Access_Id INT FOREIGN KEY REFERENCES tblRoleAccessArea(Id),
    Level_Id INT FOREIGN KEY REFERENCES tblHierarchy(Level),
    Is_Active BOOLEAN DEFAULT 1,
    {auto_current_date_user}
    );
"""
tbluserrole_user_trigger_query = add_current_user_trigger_query(table_name)


table_name = "tblGoalProject"
tblgoalproject_create_query = f"""
CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (
                Id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Level_Id INT FOREIGN KEY REFERENCES tblHierarchy(Level),
                Owner_Id INT FOREIGN KEY REFERENCES tblMember(Id),
                Start_Date DATE NOT NULL,
                End_Date DATE,
                Group_Id INT FOREIGN KEY REFERENCES tblGroup(Id),
                Branch_Id INT FOREIGN KEY REFERENCES tblBranch(Id),
                Church_Id INT FOREIGN KEY REFERENCES tblChurch(Id),
                Is_Active BOOLEAN DEFAULT 1,
                Created_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
                Created_By VARCHAR(100) NOT NULL,
                Modified_Date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Modified_By VARCHAR(100) NOT NULL
                );
"""
tblgoalproject_user_trigger_query = add_current_user_trigger_query(table_name)



insert_into_tblchurch = """
INSERT INTO tblChurch (Name, Alt_Name, Address, Location, Mission, Vision)
VALUE
('Church A', 'Alternate Name A', '123 Main Street', 'City A', 'Mission Statement A', 'Vision Statement A');
"""

check = f"""

CREATE TABLE IF NOT EXISTS tblEvents (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    
    Group_Id INT NOT NULL FOREIGN KEY REFERENCES tblGroup(Id),
    );

DELIMITER //

CREATE TRIGGER trg_calculate_next_meeting_date
BEFORE INSERT ON MeetingSchedule
FOR EACH ROW
BEGIN
    IF NEW.MeetingFrequency = 'Daily' THEN
        SET NEW.NextMeetingDate = NEW.MeetingStartDate + INTERVAL 1 DAY;
    ELSEIF NEW.MeetingFrequency = 'Weekly' THEN
        SET NEW.NextMeetingDate = DATE_ADD(
            NEW.MeetingStartDate, INTERVAL (
                7 - WEEKDAY(NEW.MeetingStartDate) + ==7-2 (Tuesday)
                IFNULL(
                    FIELD(
                        NEW.DayOfWeek, 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
                        ), 0
                    )
                ) % 7 DAY
            );
    ELSEIF NEW.MeetingFrequency = 'Monthly' THEN
        SET NEW.NextMeetingDate = DATE_ADD(NEW.MeetingStartDate, INTERVAL (DAY(NEW.MeetingStartDate) - 1 + IFNULL(FIELD(NEW.DayOfWeek, 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'), 0)) DAY);
    ELSEIF NEW.MeetingFrequency = 'Yearly' THEN
        SET NEW.NextMeetingDate = DATE_ADD(DATE_ADD(NEW.MeetingStartDate, INTERVAL YEAR(CURRENT_DATE()) - YEAR(NEW.MeetingStartDate) YEAR), INTERVAL IFNULL(FIELD(NEW.DayOfWeek, 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'), 0) DAY);
    END IF;
END//

DELIMITER ;
""'



