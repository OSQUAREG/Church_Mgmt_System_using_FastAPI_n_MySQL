checkbox = """<input type="checkbox" checked>"""
uncheckbox = """<input type="checkbox" unchecked disabled>"""
description = f"""
The Church Management System (ChMS) is an application that helps the Church manage her members, groups, events, assets, mass communication and finances (tithes, offerings, donations, seeds etc).

# Modules

## 1. Church Administration (_in progress_)
This manages the Church Hierarchy, Head Church, Churches at different levels and Church Leads, Groups and Sub-Groups.
This has the folowing Sub-Modules and endpoints:

### 1.1 Herarchy Sub-Module
{checkbox} Get All Hierarchies &nbsp;
{checkbox} Get Hierarchy by Code &nbsp;
{checkbox} Activate Hierarchy by Code &nbsp;
{checkbox} Deactivate Hierarchy by Code &nbsp;
{checkbox} Update Hierarchy by Code &nbsp;
<hr>

### 1.2 Head Church Sub-Module
{checkbox} Create New Head Church &nbsp;
{checkbox} Get Head Church by Code &nbsp;
{checkbox} Update Head Church by Code &nbsp;
{checkbox} Activate Head Church by Code (Super Admin only) &nbsp;
{checkbox} Deactivate Head Church by Code (Super Admin only) &nbsp;
<hr>

### 1.3 Churches Sub-Module
{checkbox} Create New Church &nbsp;
{checkbox} Approved Church by Code &nbsp;
{checkbox} Get All Churches &nbsp;
{checkbox} Get Churches by Level &nbsp;
{checkbox} Get Church by Code &nbsp;
{checkbox} Update Church by Code &nbsp;
{checkbox} Activate Church by Code &nbsp;
{checkbox} Deactivate Church by Code &nbsp;
<hr>

### 1.4 Church Leads Sub-Module
{checkbox} Get Church Leads by Code &nbsp;
{checkbox} Unmap Church Leads by Code &nbsp;
{checkbox} Map Church Leads by Code &nbsp;
{checkbox} Get Churches by Lead Code &nbsp;
<hr>

### 1.5 Groups Sub-Module
{uncheckbox} Create New Group &nbsp;
{uncheckbox} Get All Groups &nbsp;
{uncheckbox} Get Group by Code &nbsp;
{uncheckbox} Get Group by Church Code &nbsp;
{uncheckbox} Get Groups by Level Code &nbsp;
{uncheckbox} Update Group by Code &nbsp;
{uncheckbox} Activate Group by Code &nbsp;
{uncheckbox} Deactivate Group by Code &nbsp;
<hr>
<br>

## 2. Members Management (_in progress_) 
This manages Members, Church Positions, Member Positions.

### 2.1 Members Sub-Module
{checkbox} Create New Member &nbsp;
{checkbox} Get All Members &nbsp;
{checkbox} Get Member by Code &nbsp;
{checkbox} Get Current User Member &nbsp;
{checkbox} Get Members by Church Code &nbsp;
{checkbox} Get Members by Level Code &nbsp;
{checkbox} Update Member by Code &nbsp;
{checkbox} Update Current User Member &nbsp;
{checkbox} Activate Member by Code &nbsp;
{checkbox} Deactivate Member by Code &nbsp;
<hr>
<br>

### 2.2 Member Positions Sub-Module
{uncheckbox} Create New Member Position &nbsp;
{uncheckbox} Get All Member Positions &nbsp;
{uncheckbox} Get Member Position by Code &nbsp;
{uncheckbox} Get Member Positions by Member Code &nbsp;
{uncheckbox} Update Member Position by Code &nbsp;
{uncheckbox} Activate Member Position by Code &nbsp;
{uncheckbox} Deactivate Member Position by Code &nbsp;
<hr>
<br>


## 3. User Management (_in progress_)
This managers users, user roles, user access to modules and submodules.

## 4. Asset Management (_not implemented_)
This manages assets, asset types, assets allocation and locations.

## 5. Event Management (_not implemented_)
This manages program events and events details.

## 6. Finance Management (_not implemented_)
This manages tithes, offerings, donations, seeds etc.

## 7. Communication Management (_not implemented_)
This manages all communication channels and messages.

<br>
"""

swagger_params = dict(
    title="ChurchMan - Church Management System",
    description=description,
    version="0.0.1",
    contact={
        "name": "Gregory Ogbemudia",
        "email": "gregory.ogbemduia@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "identifier": "MIT",
    },
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    openapi_tags=[
        # Authentication Module
        {
            "name": "Authentication Operations",
            "description": "Operations on User Authentications",
        },
        # CHURCH ADMINSTRATION MODULE
        # Hierarchy Module Sub Module
        {
            "name": "Hierarchy Sub-Module Operations",
            "description": "Operations on the Church Sub-Module Hirarchy",
        },
        # Head Church Sub Module
        {
            "name": "Head Church Sub-Module Operations - Super Admin only",
            "description": "Operations on the Head Church Sub-Module by Super Admin",
        },
        {
            "name": "Head Church Sub-Module Operations",
            "description": "Operations on the Head Church",
        },
        # Churches Sub Module
        {
            "name": "Churches Sub-Module Operations - Admin only",
            "description": "Operations on the Churches Sub-Module by Admin",
        },
        {
            "name": "Churches Sub-Module Operations",
            "description": "Operations on the Churches Sub-Module",
        },
        # Church Leads Sub Module
        {
            "name": "Church Leads Sub-Module Operations - Admin only",
            "description": "Operations on the Church Leads Sub-Module by Admin",
        },
        {
            "name": "Church Leads Sub-Module Operations",
            "description": "Operations on the Church Leads Sub-Module",
        },
        # Group Sub Module
        {
            "name": "Groups Sub-Module Operations - Admin only",
            "description": "Operations on the Groups Sub-Module by Admin",
        },
        {
            "name": "Groups Sub-Module Operations",
            "description": "Operations on the Groups Sub-Module",
        },
        # Sub Group Sub Module
        {
            "name": "Sub Groups Sub-Module Operations - Admin only",
            "description": "Operations on the Sub Groups by Admin",
        },
        {
            "name": "Sub Groups Sub-Module Operations",
            "description": "Operations on the Sub Groups Sub-Module",
        },
        ## MEMBERSHIP MANAGEMENT MODULE
        # Members Sub Module
        {
            "name": "Members Sub-Module Operations - Admin only",
            "description": "Operations on the Sub Groups by Admin",
        },
        {
            "name": "Members Sub-Module Operations",
            "description": "Operations on the Sub Groups Sub-Module",
        },
        # Member Church Sub Module
        {
            "name": "Member Church Sub-Module Operations - Admin only",
            "description": "Operations on the Member's Church by Admin",
        },
        {
            "name": "Member Church Sub-Module Operations",
            "description": "Operations on the Member's Church Sub-Module",
        },
    ],
    persistAuthorization=True,
)
